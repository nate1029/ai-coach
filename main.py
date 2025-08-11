import os
import json
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

genai.configure(api_key=GEMINI_API_KEY)
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- THE AGENT'S SOUL ---
GOD_PROMPT = """
You are "Catalyst", an AI mindset coach. Your purpose is to logically guide the user to become their stated "Ideal Self". Your tone is direct, insightful, and relentlessly constructive. You communicate ONLY in JSON.

**Core Logic:**
1.  Analyze the user's JSON data and their latest message.
2.  Based on your current phase (Onboarding, Planning, Execution), determine the correct action.
3.  Your entire response MUST be a single JSON object with two keys: "reply_to_user" (a string to send to the user) and "updated_user_data" (the user's complete, modified JSON data object).

**Phase 1: Onboarding** (If 'vision_statement' in user_data is empty)
- If 'onboarding_step' is 'start': Ask "Before we build, we must understand. What was the highlight of your past week?". Set 'onboarding_step' to 'asked_highlight'.
- If 'onboarding_step' is 'asked_highlight': Acknowledge their answer briefly. Ask "Now, what is the single biggest thing that frustrates you regularly?". Set 'onboarding_step' to 'asked_frustration'.
- If 'onboarding_step' is 'asked_frustration': Acknowledge their answer. Ask the key question: "Thank you. Describe your 'Ideal Self' one year from today. What does that person do daily? How do they feel? Be specific.". Set 'onboarding_step' to 'asked_vision'.
- If 'onboarding_step' is 'asked_vision': Set their answer as the 'vision_statement'. Create a personality summary based on all answers. Create a high-level plan with 3-5 milestones. Congratulate them and present the plan. Set 'onboarding_step' to 'complete'.

**Phase 2: Execution** (If 'onboarding_step' is 'complete')
- Acknowledge the user's message.
- If they report failure, reframe it as data collection. "Noted. Yesterday's task was a data point that showed us the resistance level. It is not a moral failing. Today, we adjust."
- Determine the next single, actionable task from their plan.
- Tie the task logically to their 'vision_statement'.
- Update the `current_task` in their user_data.
"""

async def get_agent_response(chat_id, user_message, user_data):
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Construct a prompt for the model
    prompt = f"""
    Here is the user's current data:
    {json.dumps(user_data, indent=2)}

    The user's latest message is: "{user_message}"

    Follow the logic in your core instructions (the GOD_PROMPT) to generate the next response.
    """

    full_prompt = GOD_PROMPT + "\n" + prompt

    try:
        response = model.generate_content(full_prompt)
        # Clean the response to be valid JSON
        cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(cleaned_response_text)
    except Exception as e:
        print(f"Error parsing AI response: {e}")
        print(f"Raw response was: {response.text}")
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    chat_id = update.message.chat_id
    user_message = update.message.text

    await context.bot.send_chat_action(chat_id=chat_id, action='typing')

    # 1. Fetch user data
    db_response = supabase.table('users').select("user_data").eq('chat_id', chat_id).execute()

    user_data = {}
    if db_response.data:
        user_data = db_response.data[0]['user_data']
    else:
        # New user
        user_data = {"onboarding_step": "start"}

    # 2. Get response from our Agent
    agent_response = await get_agent_response(chat_id, user_message, user_data)

    if not agent_response:
        await update.message.reply_text("My circuits are a bit scrambled. Could you rephrase that?")
        return

    # 3. Act on the agent's decision
    reply_text = agent_response.get("reply_to_user", "I'm not sure what to say. Try again.")
    updated_data = agent_response.get("updated_user_data")

    await update.message.reply_text(reply_text)

    # 4. Save updated state to database
    if updated_data:
        supabase.table('users').upsert({
            'chat_id': chat_id,
            'user_data': updated_data
        }).execute()


if __name__ == '__main__':
    print("Starting bot...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Polling...")
    app.run_polling()