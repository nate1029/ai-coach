import asyncio
import schedule
import time
from datetime import datetime, timedelta
import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv
import google.generativeai as genai
from config import DAILY_CHECK_IN_TIMES, RESPONSE_TEMPLATES, SYSTEM_NAME

load_dotenv()

# Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

genai.configure(api_key=GEMINI_API_KEY)

class DailyScheduler:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    async def send_morning_check_in(self, chat_id, user_data):
        """Send morning check-in with daily tasks"""
        try:
            # Generate personalized morning message
            morning_prompt = f"""
            Create a personalized morning check-in message for the user.
            
            User Data: {json.dumps(user_data, indent=2)}
            
            The message should:
            1. Be motivating and personalized to their personality
            2. Present today's tasks in an engaging way
            3. Be concise and conversational
            4. Match their communication style
            
            Return only the message text, no JSON.
            """
            
            response = self.model.generate_content(morning_prompt)
            morning_message = response.text.strip()
            
            # Send via Telegram (you'll need to implement this)
            print(f"Morning check-in for {chat_id}: {morning_message}")
            
            return morning_message
            
        except Exception as e:
            print(f"Error sending morning check-in: {e}")
            return None
    
    async def send_evening_reflection(self, chat_id, user_data):
        """Send evening reflection prompt"""
        try:
            # Generate personalized evening reflection
            evening_prompt = f"""
            Create a personalized evening reflection prompt for the user.
            
            User Data: {json.dumps(user_data, indent=2)}
            
            The prompt should:
            1. Ask about today's task completion
            2. Encourage reflection on the day
            3. Be supportive regardless of completion status
            4. Match their communication style
            
            Return only the prompt text, no JSON.
            """
            
            response = self.model.generate_content(evening_prompt)
            evening_message = response.text.strip()
            
            # Send via Telegram (you'll need to implement this)
            print(f"Evening reflection for {chat_id}: {evening_message}")
            
            return evening_message
            
        except Exception as e:
            print(f"Error sending evening reflection: {e}")
            return None
    
    async def generate_new_daily_plan(self, user_data):
        """Generate new daily plan for tomorrow"""
        try:
            plan_prompt = f"""
            Generate a new daily plan for tomorrow based on the user's personality and goals.
            
            User Data: {json.dumps(user_data, indent=2)}
            
            Create 3-4 tasks that:
            1. Balance physical, emotional, and mental development
            2. Match their personality traits
            3. Progress toward their goals
            4. Are specific and actionable
            
            Return JSON with:
            {{
                "daily_plan": {{
                    "date": "YYYY-MM-DD",
                    "tasks": [
                        {{
                            "id": 1,
                            "type": "physical|emotional|mental",
                            "title": "Task title",
                            "description": "Detailed description",
                            "difficulty": "easy|medium|hard"
                        }}
                    ],
                    "motivation_message": "Personalized motivation"
                }}
            }}
            """
            
            response = self.model.generate_content(plan_prompt)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(cleaned_response)
            
        except Exception as e:
            print(f"Error generating daily plan: {e}")
            return None
    
    async def process_all_users(self):
        """Process all active users for daily check-ins"""
        try:
            # Get all users from database
            response = self.supabase.table('users').select("*").execute()
            
            if not response.data:
                print("No users found for daily processing")
                return
            
            current_time = datetime.now()
            current_hour = current_time.hour
            
            for user in response.data:
                chat_id = user['chat_id']
                user_data = user.get('user_data', {})
                
                # Check if user is in daily execution phase
                onboarding_step = user_data.get('onboarding', {}).get('current_step')
                if onboarding_step != 'complete':
                    continue
                
                # Morning check-in (around 9 AM)
                if current_hour == 9:
                    await self.send_morning_check_in(chat_id, user_data)
                
                # Evening reflection (around 8 PM)
                elif current_hour == 20:
                    await self.send_evening_reflection(chat_id, user_data)
                    
                    # Generate new plan for tomorrow
                    new_plan = await self.generate_new_daily_plan(user_data)
                    if new_plan:
                        user_data['daily_plan'] = new_plan['daily_plan']
                        
                        # Update database
                        self.supabase.table('users').upsert({
                            'chat_id': chat_id,
                            'user_data': user_data
                        }).execute()
                        
                        print(f"Generated new plan for user {chat_id}")
                
        except Exception as e:
            print(f"Error processing users: {e}")
    
    def run_scheduler(self):
        """Run the scheduler"""
        print("Starting daily scheduler...")
        
        # Schedule daily processing
        schedule.every().hour.do(self.process_all_users)
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

async def main():
    """Main function to run the scheduler"""
    scheduler = DailyScheduler()
    
    # Run the scheduler
    scheduler.run_scheduler()

if __name__ == "__main__":
    asyncio.run(main())
