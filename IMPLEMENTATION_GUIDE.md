# Enhanced AI Coach Implementation Guide

## Overview

This guide will help you implement the enhanced AI coach system with personality assessment, multi-phase onboarding, and daily task management.

## System Architecture

### 1. Core Components

- **`enhanced_main.py`**: Main application with enhanced AI coach logic
- **`config.py`**: Configuration and constants
- **`scheduler.py`**: Daily check-in scheduler
- **`AI_COACH_DOCUMENTATION.md`**: Complete system documentation

### 2. Key Features

#### Personality Assessment
- Dynamic question generation based on user responses
- Pattern recognition for personality traits
- Communication style adaptation

#### Multi-Phase Onboarding
1. **Personality Assessment**: Understand user's interests and traits
2. **Goal Setting**: Define ideal self and identify weaknesses
3. **Plan Creation**: Generate personalized daily tasks
4. **Daily Execution**: Ongoing accountability and progress tracking

#### Daily Task Management
- 3-4 personalized tasks per day
- Balance of physical, emotional, and mental development
- Progress tracking and streak maintenance

## Implementation Steps

### Step 1: Environment Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Environment Variables**
Create a `.env` file with:
```
TELEGRAM_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### Step 2: Database Setup

1. **Supabase Table Structure**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT UNIQUE NOT NULL,
    user_data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

2. **User Data Schema**
```json
{
  "user_info": {
    "name": "User Name",
    "personality_traits": ["trait1", "trait2"],
    "communication_style": "direct",
    "motivation_factors": ["achievement", "growth"]
  },
  "onboarding": {
    "phase": "personality_assessment|goal_setting|plan_creation|complete",
    "current_step": "week_highlight|personality_deep_dive|vision_statement|weaknesses|habits|plan_generation",
    "responses": {
      "week_highlight": "user response",
      "personality_insights": ["insight1", "insight2"]
    }
  },
  "goals": {
    "vision_statement": "Ideal self description",
    "weaknesses": ["weakness1", "weakness2"],
    "bad_habits": ["habit1", "habit2"]
  },
  "daily_plan": {
    "date": "2024-01-15",
    "tasks": [
      {
        "id": 1,
        "type": "physical|emotional|mental",
        "title": "Task title",
        "description": "Task description",
        "difficulty": "easy|medium|hard",
        "completed": false
      }
    ],
    "motivation_message": "Personalized motivation"
  },
  "progress_tracking": {
    "streak_days": 0,
    "total_tasks_completed": 0,
    "weekly_goals_met": 0
  }
}
```

### Step 3: Running the System

1. **Start the Main Application**
```bash
python enhanced_main.py
```

2. **Start the Scheduler (Optional)**
```bash
python scheduler.py
```

### Step 4: Testing the System

#### Test Conversation Flow

1. **First Interaction**
```
User: "Hey, I'm Nathic"
Bot: "Hey! I'm Catalyst, your AI coach. What was the highlight of your past week?"
```

2. **Personality Assessment**
```
User: "This week I played tennis and worked on my startup"
Bot: "That's interesting, you mentioned tennis and startup work. Do you find any connection between sports and your entrepreneurial mindset?"
```

3. **Goal Setting**
```
Bot: "Based on what I've learned about you, describe your ideal self 5 years from now. Be specific about daily routines, achievements, and how you'll feel."
```

4. **Daily Execution**
```
Bot: "Hey Nathic, how did today's tasks go? Did you complete the tennis practice and gratitude journaling?"
```

## Configuration Options

### Personality Traits
Edit `config.py` to customize:
- `PERSONALITY_TRAITS`: Available personality traits
- `COMMUNICATION_STYLES`: Communication style options
- `MOTIVATION_FACTORS`: Motivation factor categories

### Task Types
Customize task categories in `config.py`:
```python
TASK_TYPES = {
    "physical": {
        "examples": ["exercise", "sports", "yoga"],
        "personality_fit": ["sports-oriented", "goal-oriented"]
    },
    "emotional": {
        "examples": ["gratitude journaling", "meditation"],
        "personality_fit": ["introverted", "analytical"]
    }
}
```

### Onboarding Flow
Modify onboarding steps in `config.py`:
```python
ONBOARDING_STEPS = {
    "start": {
        "question": "What was the highlight of your past week?",
        "purpose": "Understand interests and activities",
        "next_step": "week_highlight"
    }
}
```

## API Integration

### Multiple API Calls Strategy

The system uses multiple API calls for different purposes:

1. **Personality Analysis API Call**
   - Purpose: Analyze user responses for personality insights
   - Input: User message and current user data
   - Output: Personality traits, follow-up questions

2. **Plan Generation API Call**
   - Purpose: Create personalized daily plans
   - Input: Complete user profile and goals
   - Output: Daily task plan with motivation

3. **Accountability Response API Call**
   - Purpose: Generate contextual responses for daily interactions
   - Input: User message and current context
   - Output: Personalized response and next actions
   - Guardrails: At most one question per reply. Detects stop intents using `STOP_FOLLOW_UP_PHRASES` and caps deep dives with `MAX_DEEP_DIVE_QUESTIONS`.

### API Call Optimization

```python
# Example of optimized API call
async def analyze_personality(self, user_message, user_data):
    prompt = f"""
    Analyze the user's response for personality insights.
    
    User Data: {json.dumps(user_data, indent=2)}
    User Message: "{user_message}"
    
    Identify personality traits, interests, and communication preferences.
    """
    
    response = self.model.generate_content(prompt)
    return json.loads(response.text.strip())
```

## Monitoring and Analytics

### Success Metrics

1. **User Engagement**
   - Daily interaction rate
   - Task completion rate
   - Long-term retention

2. **Personal Development**
   - Goal achievement progress
   - Habit formation success
   - Emotional well-being improvement

3. **System Effectiveness**
   - Personality assessment accuracy
   - Task relevance scores
   - User satisfaction ratings

### Logging and Monitoring

Add logging to track system performance:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_coach.log'),
        logging.StreamHandler()
    ]
)
```

## Troubleshooting

### Common Issues

1. **API Rate Limits**
   - Implement retry logic with exponential backoff
   - Cache responses when possible
   - Monitor API usage

2. **Database Connection Issues**
   - Check Supabase credentials
   - Verify network connectivity
   - Implement connection pooling

3. **Telegram Bot Issues**
   - Verify bot token
   - Check webhook configuration
   - Monitor message delivery

### Debug Mode

Enable debug mode for development:

```python
DEBUG_MODE = True

if DEBUG_MODE:
    logging.getLogger().setLevel(logging.DEBUG)
    print("Debug mode enabled")
```

## Deployment

### Production Deployment

1. **Environment Setup**
   - Use production environment variables
   - Set up proper logging
   - Configure monitoring

2. **Database Migration**
   - Backup existing data
   - Run database migrations
   - Verify data integrity

3. **Application Deployment**
   - Deploy to production server
   - Set up process monitoring
   - Configure auto-restart

### Scaling Considerations

1. **Database Scaling**
   - Implement connection pooling
   - Consider read replicas for analytics
   - Monitor query performance

2. **API Scaling**
   - Implement rate limiting
   - Use API caching
   - Monitor response times

3. **Application Scaling**
   - Use load balancers
   - Implement horizontal scaling
   - Monitor resource usage

## Retrieval-Augmented Generation (RAG)

- Enable by setting `RAG_ENABLED = True` in `config.py`.
- Add `.txt` or `.md` knowledge sources into `knowledge/`.
- The system performs lightweight retrieval and injects snippets into prompts.
- Tune `RAG_MAX_CONTEXT_CHARS` to balance quality and latency.

## Future Enhancements

### Planned Features

1. **Advanced Analytics**
   - User behavior analysis
   - Progress visualization
   - Predictive task recommendations

2. **Integration Capabilities**
   - Calendar integration
   - Fitness tracker integration
   - Social media integration

3. **AI Improvements**
   - Multi-modal conversations
   - Voice interaction
   - Advanced personality modeling

### Development Roadmap

1. **Phase 1**: Core personality assessment and daily tasks
2. **Phase 2**: Advanced analytics and progress tracking
3. **Phase 3**: Integration with external services
4. **Phase 4**: Advanced AI features and multi-modal support

This implementation guide provides a comprehensive overview of the enhanced AI coach system. Follow these steps to successfully deploy and maintain the system. 