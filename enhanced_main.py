import os
import json
import asyncio
from datetime import datetime, timedelta
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from supabase import create_client, Client
from dotenv import load_dotenv
import logging
from config import (
    MAX_DEEP_DIVE_QUESTIONS,
    MAX_QUESTIONS_PER_REPLY,
    STOP_FOLLOW_UP_PHRASES,
    RAG_ENABLED,
    KNOWLEDGE_DIR,
    RAG_MAX_CONTEXT_CHARS,
    AUTO_SILENCE_ON_ACK,
    ACKNOWLEDGEMENT_PHRASES,
)

# Lightweight RAG retriever
def retrieve_context(query: str) -> str:
    if not RAG_ENABLED:
        return ""
    try:
        import os
        import re
        ctx_chunks = []
        if not os.path.isdir(KNOWLEDGE_DIR):
            return ""
        # naive keyword scanning across small text/pdf summaries
        for root, _, files in os.walk(KNOWLEDGE_DIR):
            for name in files:
                if not name.lower().endswith((".txt", ".md")):
                    continue
                path = os.path.join(root, name)
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                # prioritize files containing any keyword from query
                keywords = [w for w in re.findall(r"[a-zA-Z]{4,}", query.lower())]
                score = sum(1 for k in keywords if k in text.lower())
                if score > 0:
                    snippet = text[: RAG_MAX_CONTEXT_CHARS]
                    ctx_chunks.append(f"Source: {name}\n{snippet}")
        combined = "\n\n".join(ctx_chunks)
        return combined[: RAG_MAX_CONTEXT_CHARS]
    except Exception:
        return ""

load_dotenv()

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

genai.configure(api_key=GEMINI_API_KEY)
logging.basicConfig(level=logging.INFO)

# --- ENHANCED AGENT SYSTEM ---
class EnhancedAICoach:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    async def analyze_personality(self, user_message, user_data):
        """First API call: Analyze response and generate follow-up questions"""
        rag_context = retrieve_context(user_message)
        prompt = f"""
        You are an empathetic, authoritative coaching analyst. Start with brief reflective listening (1 sentence), then infer practical personality signals. Keep it concise and human.
        
        User Data: {json.dumps(user_data, indent=2)}
        User Message: "{user_message}"
        Retrieved Coaching Knowledge (optional):\n{rag_context}
        
        Tasks:
        1) Reflect what they shared and likely feel (1 sentence).
        2) Identify traits, interests, communication style, motivation factors.
        3) Provide at most one focused follow-up question. If the user already made a clear commitment or gave a complete answer, do not ask a question.
        
        Return JSON:
        {{
            "personality_insights": {{
                "traits": ["trait1", "trait2"],
                "interests": ["interest1", "interest2"],
                "communication_style": "direct|supportive|analytical|motivational",
                "motivation_factors": ["achievement", "growth", "recognition"]
            }},
            "follow_up_question": "One concise question or empty if not needed",
            "conversation_context": "What we learned from this response"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(cleaned_response)
        except Exception as e:
            print(f"Error in personality analysis: {e}")
            return None
    
    async def generate_personalized_plan(self, user_data):
        """Second API call: Create personalized daily plan based on personality"""
        prompt = f"""
        You are an empathetic, practical coach designing a small daily plan. Reflect briefly, then propose tasks that fit the user's personality and goals.
        
        User Data: {json.dumps(user_data, indent=2)}
        
        Requirements:
        - 3–4 tasks balancing physical, emotional, and mental development.
        - Make tasks tiny and specific; reduce friction; include clear cues.
        - Include difficulty mix (easy/medium/hard) and a brief personality-fit.
        - Provide a short motivation line matching the user's tone (no hype).
        
        Return JSON:
        {{
            "daily_plan": {{
                "date": "YYYY-MM-DD",
                "tasks": [
                    {{
                        "id": 1,
                        "type": "physical|emotional|mental",
                        "title": "Task title",
                        "description": "Brief, concrete action with cue",
                        "difficulty": "easy|medium|hard",
                        "personality_fit": "Why this suits them"
                    }}
                ],
                "motivation_message": "Brief personalized motivation"
            }}
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(cleaned_response)
        except Exception as e:
            print(f"Error in plan generation: {e}")
            return None
    
    async def create_accountability_response(self, user_message, user_data):
        """Third API call: Generate accountability and reflection responses"""
        rag_context = retrieve_context(user_message)
        prompt = f"""
        You are an empathetic, authoritative coach responding to a check-in. Start with one reflective sentence. Offer one practical suggestion. End with at most one purposeful question only if needed. Match tone to mood. Avoid hype.
        
        User Data: {json.dumps(user_data, indent=2)}
        User Message: "{user_message}"
        Retrieved Coaching Knowledge (optional):\n{rag_context}
        
        Guidelines:
        - Normalize setbacks (“data, not a verdict”), suggest a tiny next step.
        - Use micro-techniques when apt: reframing, scaling (0–10), tiny commitments.
        - If the user makes a clear commitment (e.g., “first chapter tonight”), do not ask a question—confirm and close.
        - Keep language natural, respectful, and concise (2–3 sentences).
        
        Return JSON:
        {{
            "reply_to_user": "Concise reflection + one practical suggestion + optional question",
            "next_action": "wait_for_response|generate_new_plan|send_motivation|no_reply",
            "updated_insights": {{
                "new_traits": ["..."],
                "progress_notes": "What we learned about their progress"
            }}
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(cleaned_response)
        except Exception as e:
            print(f"Error in accountability response: {e}")
            return None

# --- ENHANCED PROMPT SYSTEM ---
ENHANCED_PROMPT = """
You are a skilled, empathetic AI coach. Respond like a thoughtful human: warm, brief, emotionally intelligent, and grounded in behavioral psychology.

Style & Conduct:
- Start with brief reflective listening: acknowledge key points and likely feelings.
- Match tone to mood: soft when low; steady and clear when neutral; energized when high.
- Be concise (2–3 sentences). Use natural variety; avoid repetitive phrases or hype.
- Ask at most one meaningful question unless two are essential for clarity.
- Use micro-techniques when helpful: reflective listening, scaling (0–10), reframing, tiny commitments (“What’s one small step?”), identity-based habits.
- Keep guidance practical: reduce friction, use clear cues, and choose tiny next steps.

Multi-Phase Coaching:
- Phase 1: Personality Assessment (onboarding_step: start → week_highlight → personality_deep_dive)
  • Explore interests, patterns, and motivations with focused, single questions.
- Phase 2: Goal Setting (onboarding_step: vision_statement → weaknesses → habits)
  • Clarify vision, name obstacles, and identify habit levers.
- Phase 3: Plan Creation (onboarding_step: plan_generation)
  • Propose 3–4 small, specific tasks across physical/emotional/mental; explain fit.
- Phase 4: Daily Execution (onboarding_step: complete)
  • Check progress, normalize setbacks, adjust difficulty, and make one clear next step.

Response Format (strict JSON):
{
  "reply_to_user": "2–3 sentences max; brief reflection first; at most one question",
  "updated_user_data": { /* fully updated state */ },
  "next_actions": ["wait_for_response" | "generate_new_plan" | "send_motivation"],
  "personality_insights": {
    "new_traits": ["..."],
    "communication_style": "direct|supportive|analytical|motivational"
  }
}
"""

async def get_enhanced_agent_response(chat_id, user_message, user_data):
    """Enhanced agent response with multiple API calls"""
    coach = EnhancedAICoach()
    
    # Determine current phase and appropriate action
    onboarding_step = user_data.get('onboarding', {}).get('current_step', 'start')
    
    if onboarding_step == 'start':
        # First interaction - start personality assessment
        return await handle_first_interaction(user_message, user_data, coach)
    
    elif onboarding_step in ['week_highlight', 'personality_deep_dive']:
        # Personality assessment phase
        return await handle_personality_assessment(user_message, user_data, coach)
    
    elif onboarding_step in ['vision_statement', 'weaknesses', 'habits']:
        # Goal setting phase
        return await handle_goal_setting(user_message, user_data, coach)
    
    elif onboarding_step == 'plan_generation':
        # Plan creation phase
        return await handle_plan_creation(user_data, coach)
    
    else:
        # Daily execution phase
        return await handle_daily_execution(user_message, user_data, coach)

async def handle_first_interaction(user_message, user_data, coach):
    """Handle the very first interaction with a new user"""
    # Initialize user data structure
    updated_data = {
        "user_info": {
            "name": user_message.split()[0] if user_message else "User",
            "personality_traits": [],
            "communication_style": "direct",
            "motivation_factors": []
        },
        "onboarding": {
            "phase": "personality_assessment",
            "current_step": "week_highlight",
            "responses": {}
        },
        "goals": {},
        "daily_plan": {},
        "progress_tracking": {
            "streak_days": 0,
            "total_tasks_completed": 0,
            "weekly_goals_met": 0
        }
    }
    
    return {
        "reply_to_user": "Hey bro! I'm Jose Marino, your mindset coach. What was the highlight of your week? 💪",
        "updated_user_data": updated_data,
        "next_actions": ["wait_for_response"],
        "personality_insights": {}
    }

async def handle_personality_assessment(user_message, user_data, coach):
    """Handle personality assessment phase"""
    # First API call: Analyze personality
    personality_analysis = await coach.analyze_personality(user_message, user_data)
    
    if not personality_analysis:
        return {
            "reply_to_user": "Not catching that, man. Try again?",
            "updated_user_data": user_data,
            "next_actions": ["wait_for_response"],
            "personality_insights": {}
        }
    
    # Update user data with personality insights
    current_step = user_data.get('onboarding', {}).get('current_step', 'week_highlight')
    
    # Store the response
    if 'responses' not in user_data.get('onboarding', {}):
        user_data['onboarding']['responses'] = {}
    
    user_data['onboarding']['responses'][current_step] = user_message
    
    # Update personality traits
    if 'user_info' not in user_data:
        user_data['user_info'] = {}
    insights = personality_analysis['personality_insights']
    # Normalize keys into our schema
    if insights.get('traits'):
        user_data['user_info']['personality_traits'] = insights.get('traits', [])
    if insights.get('interests'):
        user_data['user_info']['interests'] = insights.get('interests', [])
    if insights.get('communication_style'):
        user_data['user_info']['communication_style'] = insights.get('communication_style')
    if insights.get('motivation_factors'):
        user_data['user_info']['motivation_factors'] = insights.get('motivation_factors', [])
    
    # Determine next step with bounded deep-dive
    deep_count = user_data['onboarding'].get('deep_dive_count', 0)
    user_message_lower = (user_message or "").strip().lower()
    wants_to_stop = any(p in user_message_lower for p in STOP_FOLLOW_UP_PHRASES)

    if current_step == 'week_highlight' and not wants_to_stop:
        user_data['onboarding']['current_step'] = 'personality_deep_dive'
        user_data['onboarding']['deep_dive_count'] = 1
        follow_up = personality_analysis['follow_up_question']
    elif current_step == 'personality_deep_dive' and deep_count < MAX_DEEP_DIVE_QUESTIONS and not wants_to_stop:
        user_data['onboarding']['current_step'] = 'personality_deep_dive'
        user_data['onboarding']['deep_dive_count'] = deep_count + 1
        follow_up = personality_analysis['follow_up_question']
    else:
        user_data['onboarding']['current_step'] = 'vision_statement'
        follow_up = (
            "Based on what I've learned about you, describe your ideal self 5 years from now. Be specific about daily routines, achievements, and how you'll feel."
        )

    # Enforce max one question in follow-up
    if follow_up.count('?') > MAX_QUESTIONS_PER_REPLY:
        first_q_idx = follow_up.find('?')
        if first_q_idx != -1:
            follow_up = follow_up[: first_q_idx + 1]
    
    return {
        "reply_to_user": follow_up,
        "updated_user_data": user_data,
        "next_actions": ["wait_for_response"],
        "personality_insights": personality_analysis['personality_insights']
    }

async def handle_goal_setting(user_message, user_data, coach):
    """Handle goal setting phase"""
    current_step = user_data.get('onboarding', {}).get('current_step', 'vision_statement')
    
    # Store the response
    user_data['onboarding']['responses'][current_step] = user_message
    
    if current_step == 'vision_statement':
        user_data['goals']['vision_statement'] = user_message
        user_data['onboarding']['current_step'] = 'weaknesses'
        next_question = "Now, what are your biggest weaknesses that might hold you back from this vision?"
    
    elif current_step == 'weaknesses':
        user_data['goals']['weaknesses'] = user_message
        user_data['onboarding']['current_step'] = 'habits'
        next_question = "What bad habits are holding you back, man?"
    
    elif current_step == 'habits':
        user_data['goals']['bad_habits'] = user_message
        user_data['onboarding']['current_step'] = 'plan_generation'
        user_data['onboarding']['phase'] = 'plan_creation'
        next_question = "Boom! Let's create your game plan. Give me a sec..."
    
    return {
        "reply_to_user": next_question,
        "updated_user_data": user_data,
        "next_actions": ["wait_for_response"] if current_step != 'habits' else ["generate_plan"],
        "personality_insights": {}
    }

async def handle_plan_creation(user_data, coach):
    """Handle plan creation phase"""
    # Second API call: Generate personalized plan
    plan_data = await coach.generate_personalized_plan(user_data)
    
    if not plan_data:
        return {
            "reply_to_user": "Plan creation's glitching, bro. Let me try again.",
            "updated_user_data": user_data,
            "next_actions": ["generate_plan"],
            "personality_insights": {}
        }
    
    # Update user data with the plan
    user_data['daily_plan'] = plan_data['daily_plan']
    user_data['onboarding']['current_step'] = 'complete'
    user_data['onboarding']['phase'] = 'complete'
    
    # Create welcome message
    welcome_message = f"""
Plan ready.

{plan_data['daily_plan']['motivation_message']}

Today's tasks:
"""
    
    for task in plan_data['daily_plan']['tasks']:
        title = task.get('title', 'Task')
        ttype = task.get('type', 'task')
        difficulty = task.get('difficulty', '')
        welcome_message += f"\n• {title} ({ttype}{' · ' + difficulty if difficulty else ''})"
    
    welcome_message += "\n\nConfirm you’re good with this, or request a tweak."
    
    return {
        "reply_to_user": welcome_message,
        "updated_user_data": user_data,
        "next_actions": ["wait_for_response"],
        "personality_insights": {}
    }

async def handle_daily_execution(user_message, user_data, coach):
    """Handle daily execution phase"""
    # Third API call: Generate accountability response
    accountability_response = await coach.create_accountability_response(user_message, user_data)
    
    if not accountability_response:
        return {
            "reply_to_user": "Not catching that, man. Try again?",
            "updated_user_data": user_data,
            "next_actions": ["wait_for_response"],
            "personality_insights": {}
        }
    
    # Update user data with new insights
    if accountability_response.get('updated_insights'):
        if 'user_info' not in user_data:
            user_data['user_info'] = {}
        user_data['user_info'].update(accountability_response['updated_insights'])
    
    # Ensure a single follow-up question max; optionally strip multiple questions
    reply_text = accountability_response['reply_to_user']
    if reply_text.count('?') > MAX_QUESTIONS_PER_REPLY:
        first_q_idx = reply_text.find('?')
        if first_q_idx != -1:
            reply_text = reply_text[: first_q_idx + 1]

    # If model suggests no further interaction, respect it
    next_action = accountability_response.get('next_action', 'wait_for_response')
    if next_action == 'no_reply':
        reply_text = "Okay—lock it in. Update me when it's done."
        next_action = 'wait_for_response'

    return {
        "reply_to_user": reply_text,
        "updated_user_data": user_data,
        "next_actions": [next_action],
        "personality_insights": accountability_response.get('updated_insights', {})
    }

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced message handler with multiple API calls"""
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    chat_id = update.message.chat_id
    user_message = update.message.text

    await context.bot.send_chat_action(chat_id=chat_id, action='typing')

    # 1. Fetch user data
    try:
        db_response = supabase.table('users').select("user_data").eq('chat_id', chat_id).execute()
        user_data = db_response.data[0]['user_data'] if db_response.data else {}
    except Exception as e:
        logging.error(f"DB fetch error: {e}")
        user_data = {}

    # Optional: silence on acknowledgements
    if AUTO_SILENCE_ON_ACK and (user_message or "").strip().lower() in ACKNOWLEDGEMENT_PHRASES:
        try:
            # Persist minimal heartbeat
            supabase.table('users').upsert({
                'chat_id': chat_id,
                'user_data': {**user_data, 'last_seen': datetime.utcnow().isoformat()}
            }).execute()
            # Do not reply on simple acks
            return
        except Exception as e:
            # If persisting fails, continue to normal flow to avoid silent failures
            print(f"Silence-on-ack upsert failed: {e}")

    # 2. Get enhanced response from our Agent
    try:
        agent_response = await get_enhanced_agent_response(chat_id, user_message, user_data)
    except Exception as e:
        logging.error(f"Agent error: {e}")
        agent_response = None

    if not agent_response:
        try:
            await update.message.reply_text("I'm having a hiccup. Let's keep it simple—what's one small step you want to take next?")
        except Exception as send_err:
            logging.error(f"Reply send error (fallback): {send_err}")
        return

    # 3. Act on the agent's decision
    reply_text = agent_response.get("reply_to_user", "Not sure what to say, man. Try again.")
    if reply_text.count('?') > MAX_QUESTIONS_PER_REPLY:
        first_q_idx = reply_text.find('?')
        if first_q_idx != -1:
            reply_text = reply_text[: first_q_idx + 1]
    updated_data = agent_response.get("updated_user_data")

    try:
        await update.message.reply_text(reply_text)
    except Exception as send_err:
        logging.error(f"Reply send error: {send_err}")

    # 4. Handle next actions
    next_actions = agent_response.get("next_actions", [])
    
    for action in next_actions:
        if action == "generate_plan":
            # Generate plan asynchronously
            plan_response = await handle_plan_creation(updated_data, EnhancedAICoach())
            if plan_response:
                await update.message.reply_text(plan_response["reply_to_user"])
                updated_data = plan_response["updated_user_data"]
        elif action == "generate_new_plan":
            plan_response = await handle_plan_creation(updated_data, EnhancedAICoach())
            if plan_response:
                await update.message.reply_text(plan_response["reply_to_user"])
                updated_data = plan_response["updated_user_data"]
        elif action == "send_motivation":
            # Lightweight motivation message based on current tasks
            tasks = (updated_data or {}).get("daily_plan", {}).get("tasks", [])
            if tasks:
                tasks_list = "\n".join([f"• {t.get('title', 'Task')} ({t.get('difficulty','')})" for t in tasks])
                motivation = (updated_data or {}).get("daily_plan", {}).get("motivation_message") or "Stay consistent. Small wins compound."
                msg = f"🚀 Quick boost: {motivation}\n\nToday's lineup:\n{tasks_list}\n\nWhich one are you hitting first?"
            else:
                msg = "🚀 Quick boost: Stay consistent. Small wins compound. What's the one thing you'll do next?"
            await update.message.reply_text(msg)

    # 5. Save updated state to database
    if updated_data:
        try:
            supabase.table('users').upsert({
                'chat_id': chat_id,
                'user_data': updated_data
            }).execute()
        except Exception as e:
            logging.error(f"DB upsert error: {e}")

if __name__ == '__main__':
    print("Starting Jose Marino AI coach...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Jose Marino is live and ready to coach! 💪")
    app.run_polling() 