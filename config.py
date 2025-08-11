# Enhanced AI Coach Configuration

# --- SYSTEM CONFIGURATION ---
SYSTEM_NAME = "Catalyst"
SYSTEM_VERSION = "2.0"
MAX_API_RETRIES = 3
API_TIMEOUT = 30
MAX_DEEP_DIVE_QUESTIONS = 3
MAX_QUESTIONS_PER_REPLY = 1

# Phrases that signal the user wants to move on or stop deep questioning
STOP_FOLLOW_UP_PHRASES = [
    "move on",
    "let's move on",
    "lets move on",
    "enough",
    "next",
    "stop",
    "that's all",
    "thats all",
    "skip",
    "we can continue",
]

# --- PERSONALITY ASSESSMENT CONFIGURATION ---
PERSONALITY_TRAITS = [
    "competitive", "collaborative", "analytical", "creative", 
    "introverted", "extroverted", "goal-oriented", "process-oriented",
    "risk-taking", "cautious", "optimistic", "realistic",
    "sports-oriented", "intellectual", "artistic", "entrepreneurial"
]

COMMUNICATION_STYLES = [
    "direct", "supportive", "analytical", "motivational",
    "casual", "formal", "encouraging", "challenging"
]

MOTIVATION_FACTORS = [
    "achievement", "growth", "recognition", "autonomy",
    "mastery", "purpose", "connection", "security"
]

# --- TASK TYPES AND CATEGORIES ---
TASK_TYPES = {
    "physical": {
        "examples": ["exercise", "sports", "yoga", "walking", "gym"],
        "personality_fit": ["sports-oriented", "goal-oriented", "competitive"]
    },
    "emotional": {
        "examples": ["gratitude journaling", "meditation", "reflection", "social connection"],
        "personality_fit": ["introverted", "analytical", "process-oriented"]
    },
    "mental": {
        "examples": ["learning", "reading", "skill development", "planning"],
        "personality_fit": ["intellectual", "goal-oriented", "analytical"]
    },
    "social": {
        "examples": ["networking", "mentoring", "team activities", "relationship building"],
        "personality_fit": ["extroverted", "collaborative", "connection-oriented"]
    }
}

# --- DIFFICULTY LEVELS ---
DIFFICULTY_LEVELS = {
    "easy": {
        "description": "Simple, quick tasks that can be completed in 5-15 minutes",
        "examples": ["drink water", "take a short walk", "write one gratitude note"]
    },
    "medium": {
        "description": "Moderate effort tasks that take 15-45 minutes",
        "examples": ["30-minute workout", "read a chapter", "practice a skill"]
    },
    "hard": {
        "description": "Challenging tasks that require significant effort or time",
        "examples": ["complete a project", "learn a new skill", "deep work session"]
    }
}

# --- ONBOARDING FLOW CONFIGURATION ---
ONBOARDING_STEPS = {
    "start": {
        "question": "What was the highlight of your past week?",
        "purpose": "Understand interests and activities",
        "next_step": "week_highlight"
    },
    "week_highlight": {
        "purpose": "Store week highlight and analyze personality",
        "next_step": "personality_deep_dive"
    },
    "personality_deep_dive": {
        "purpose": "Generate follow-up questions based on initial response",
        "next_step": "vision_statement"
    },
    "vision_statement": {
        "question": "Based on what I've learned about you, describe your ideal self 5 years from now. Be specific about daily routines, achievements, and how you'll feel.",
        "purpose": "Create vision statement",
        "next_step": "weaknesses"
    },
    "weaknesses": {
        "question": "Now, what are your biggest weaknesses that might hold you back from this vision?",
        "purpose": "Identify areas for improvement",
        "next_step": "habits"
    },
    "habits": {
        "question": "What bad habits do you need to break to become this person?",
        "purpose": "Identify negative patterns",
        "next_step": "plan_generation"
    },
    "plan_generation": {
        "purpose": "Create personalized daily plan",
        "next_step": "complete"
    },
    "complete": {
        "purpose": "Daily execution and accountability",
        "next_step": None
    }
}

# --- DAILY EXECUTION CONFIGURATION ---
DAILY_CHECK_IN_TIMES = {
    "morning": "09:00",
    "evening": "20:00"
}

# --- RAG / KNOWLEDGE BASE CONFIGURATION ---
# If true, prompts will be augmented with retrieved context from local knowledge files
RAG_ENABLED = True
KNOWLEDGE_DIR = "knowledge"
RAG_MAX_CONTEXT_CHARS = 1400

# --- CONVERSATION SILENCE POLICY ---
# If the user sends low-content acknowledgements (e.g., "ok", "thanks"),
# the bot may choose not to reply to reduce noise.
AUTO_SILENCE_ON_ACK = True
ACKNOWLEDGEMENT_PHRASES = [
    "ok",
    "okay",
    "k",
    "kk",
    "cool",
    "nice",
    "thanks",
    "thank you",
    "got it",
    "noted",
    "done",
    "great",
    "awesome",
    "👍",
    "👌",
    "🙌",
]

# --- PROMPT TEMPLATES ---
PROMPT_TEMPLATES = {
    "personality_analysis": """
    Analyze the user's response for personality insights.
    
    User Data: {user_data}
    User Message: "{user_message}"
    
    Identify:
    1. Personality traits from the predefined list
    2. Interests and activities mentioned
    3. Communication style preferences
    4. Motivation factors
    
    Return JSON with personality insights and follow-up question.
    """,
    
    "plan_generation": """
    Create a personalized daily plan based on user's personality and goals.
    
    User Data: {user_data}
    
    Create 3-4 daily tasks that balance:
    - Physical development (exercise, health)
    - Emotional development (mindfulness, relationships)
    - Mental development (learning, career)
    
    Consider their personality traits and make tasks specific and actionable.
    """,
    
    "accountability_response": """
    You are an AI coach having a conversation about daily tasks.
    
    User Data: {user_data}
    User Message: "{user_message}"
    
    Respond in a way that:
    1. Matches their communication style
    2. Acknowledges their personality traits
    3. Provides constructive feedback
    4. Keeps responses concise and conversational
    5. Asks follow-up questions to maintain engagement
    """
}

# --- RESPONSE TEMPLATES ---
RESPONSE_TEMPLATES = {
    "welcome": "Hey! I'm {system_name}, your AI coach. What was the highlight of your past week?",
    "plan_introduction": """
🎯 Your personalized plan is ready!

{motivation_message}

Today's tasks:
{tasks_list}

Let's start with the first task. How does this plan feel to you?
    """,
    "task_completion_celebration": "Great job completing {task_name}! How did it make you feel?",
    "task_incomplete_support": "No worries about {task_name}. What got in the way? Let's figure out how to make tomorrow better.",
    "daily_motivation": "Good morning! Here are your tasks for today: {tasks_list}",
    "evening_reflection": "How did today's tasks go? Let's reflect on what worked and what we can improve."
}

# --- ERROR MESSAGES ---
ERROR_MESSAGES = {
    "api_error": "I'm having trouble processing that. Could you rephrase?",
    "parsing_error": "My circuits are a bit scrambled. Could you try again?",
    "timeout_error": "I'm taking longer than expected. Please try again.",
    "general_error": "Something went wrong. Let me try again."
}

# --- SUCCESS METRICS ---
SUCCESS_METRICS = {
    "engagement": {
        "daily_interaction_rate": "Percentage of users who interact daily",
        "task_completion_rate": "Percentage of assigned tasks completed",
        "long_term_retention": "Users who continue after 30 days"
    },
    "development": {
        "goal_progress": "Progress toward stated goals",
        "habit_formation": "Success in building new habits",
        "emotional_wellbeing": "Improvement in emotional state"
    },
    "system": {
        "personality_accuracy": "Accuracy of personality assessment",
        "task_relevance": "User satisfaction with task relevance",
        "overall_satisfaction": "Overall user satisfaction rating"
    }
} 