# AI Coach System - Enhanced Documentation

## Current System Overview

The current system is a Telegram-based AI coach called "Catalyst" that:
- Uses Gemini API for AI responses
- Stores user data in Supabase
- Has a basic onboarding flow with 4 steps
- Provides daily tasks based on user goals

## Proposed Enhanced System

### Core Philosophy
The enhanced system will be a **personality-driven AI coach** that:
1. **Assesses personality** through conversational questions
2. **Understands goals and ideal self** based on personality insights
3. **Creates personalized daily plans** with 3-4 tasks (physical, emotional, mental)
4. **Maintains ongoing accountability** through daily check-ins

### System Architecture

#### 1. Multi-Phase Onboarding Flow

**Phase 1: Personality Assessment**
- Week highlight question → Understand interests and activities
- Follow-up questions based on responses → Deep dive into personality traits
- Pattern recognition → Identify behavioral patterns and preferences

**Phase 2: Goal Setting & Ideal Self**
- Vision statement creation → Who do you want to become?
- Weakness identification → What holds you back?
- Bad habits recognition → What needs to change?

**Phase 3: Plan Creation**
- Generate personalized daily plan with 3-4 tasks
- Mix of physical, emotional, and mental development
- Set accountability framework

#### 2. Daily Execution Flow

**Morning Check-in**
- Review previous day's tasks
- Present today's tasks
- Brief motivation/context

**Evening Reflection**
- Task completion status
- Emotional state assessment
- Adjustments for next day

### Data Structure

```json
{
  "user_info": {
    "name": "Nathic",
    "personality_traits": ["sports-oriented", "entrepreneurial", "competitive"],
    "communication_style": "direct",
    "motivation_factors": ["achievement", "growth", "recognition"]
  },
  "onboarding": {
    "phase": "personality_assessment|goal_setting|plan_creation|complete",
    "current_step": "week_highlight|personality_deep_dive|vision_statement|weaknesses|habits|plan_generation",
    "responses": {
      "week_highlight": "played tennis, worked on startup",
      "personality_insights": ["enjoys physical activity", "goal-oriented"],
      "vision_statement": "I want to be a successful entrepreneur who maintains work-life balance",
      "weaknesses": ["procrastination", "perfectionism"],
      "bad_habits": ["late night work", "skipping exercise"]
    }
  },
  "goals": {
    "vision_statement": "Ideal self description",
    "timeframe": "5 years",
    "key_areas": ["career", "health", "relationships", "personal_growth"]
  },
  "daily_plan": {
    "current_date": "2024-01-15",
    "tasks": [
      {
        "id": 1,
        "type": "physical",
        "title": "30-minute tennis practice",
        "description": "Improve your game and stay active",
        "completed": false,
        "difficulty": "medium"
      },
      {
        "id": 2,
        "type": "emotional",
        "title": "Practice gratitude journaling",
        "description": "Write 3 things you're grateful for today",
        "completed": false,
        "difficulty": "easy"
      },
      {
        "id": 3,
        "type": "mental",
        "title": "Work on startup pitch deck",
        "description": "Focus on the problem-solution fit section",
        "completed": false,
        "difficulty": "hard"
      }
    ],
    "daily_reflection": {
      "mood": "motivated",
      "energy_level": "high",
      "challenges": "time management",
      "wins": "completed morning routine"
    }
  },
  "progress_tracking": {
    "streak_days": 5,
    "total_tasks_completed": 12,
    "weekly_goals_met": 3,
    "monthly_reflection": "Making steady progress on startup while maintaining health"
  }
}
```

### Enhanced Prompt Strategy

#### Personality Assessment Prompts
```
"Hey Nathic, what was the highlight of your week?"
→ Based on response: "That's interesting, you mentioned tennis and startup work. Do you find any connection between sports and your entrepreneurial mindset?"
→ Follow-up: "When you're playing tennis, what mindset do you bring to the game?"
```

#### Goal Setting Prompts
```
"Based on what I've learned about you, describe your ideal self 5 years from now. Be specific about daily routines, achievements, and how you'll feel."
"Now, what are your biggest weaknesses that might hold you back from this vision?"
"What bad habits do you need to break to become this person?"
```

#### Daily Task Prompts
```
"Hey Nathic, how did today's tasks go? Did you complete the tennis practice and gratitude journaling?"
→ If incomplete: "What got in the way? Let's figure out how to make tomorrow better."
→ If complete: "Great! How did the gratitude practice make you feel?"
```

### Implementation Plan

#### Phase 1: Enhanced Onboarding
1. **Personality Assessment Module**
   - Dynamic question generation based on responses
   - Pattern recognition for personality traits
   - Communication style adaptation

2. **Goal Setting Module**
   - Vision statement creation
   - Weakness and habit identification
   - Timeline and milestone setting

3. **Plan Generation Module**
   - Personalized daily task creation
   - Balance of physical, emotional, mental tasks
   - Difficulty progression system

#### Phase 2: Daily Execution
1. **Morning Check-in System**
   - Task presentation with context
   - Motivation based on personality
   - Energy level assessment

2. **Evening Reflection System**
   - Task completion tracking
   - Emotional state monitoring
   - Plan adjustment logic

3. **Progress Tracking**
   - Streak maintenance
   - Weekly/monthly reflections
   - Goal progress monitoring

### Technical Implementation

#### Multiple API Calls Strategy
Instead of single API calls, the system will:
1. **First API Call**: Analyze user response and generate follow-up questions
2. **Second API Call**: Process personality insights and create user profile
3. **Third API Call**: Generate personalized daily plan
4. **Fourth API Call**: Create accountability and reflection prompts

Guardrails to avoid endless questioning and to keep replies human-like and efficient:
- Enforce at most one question per reply.
- Respect user intent to stop via `STOP_FOLLOW_UP_PHRASES`.
- Bound deep-dive follow-ups to `MAX_DEEP_DIVE_QUESTIONS`.

#### Enhanced Response Structure
```json
{
  "reply_to_user": "Hey Nathic, how did today's tasks go?",
  "updated_user_data": { /* complete user data */ },
  "next_actions": [
    "wait_for_response",
    "generate_tomorrow_plan",
    "send_motivation_message"
  ],
  "personality_insights": {
    "new_traits": ["resilient", "goal-focused"],
    "communication_preferences": "direct_and_supportive"
  }
}
```

### Key Features to Implement

1. **Dynamic Personality Assessment**
   - Contextual follow-up questions
   - Pattern recognition algorithms
   - Communication style adaptation

2. **Personalized Task Generation**
   - Task difficulty progression
   - Personality-based task selection
   - Balance of different development areas

3. **Emotional Intelligence**
   - Mood tracking and adaptation
   - Supportive failure handling
   - Celebration of wins

4. **Accountability Framework**
   - Daily check-ins
   - Weekly reflections
   - Monthly goal reviews

5. **Progress Visualization**
   - Streak tracking
   - Goal progress monitoring
   - Achievement celebration

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

This enhanced system will create a more personalized, engaging, and effective AI coaching experience that truly understands and adapts to each user's unique personality and goals. 

### Retrieval-Augmented Generation (RAG)

- Toggle with `RAG_ENABLED` in `config.py`.
- Place coach knowledge files in the `knowledge/` directory (`.txt`/`.md`). Create it if it doesn't exist.
- The system retrieves short, relevant snippets and injects them into prompts.
- Keep total added context under `RAG_MAX_CONTEXT_CHARS` to control latency and cost.