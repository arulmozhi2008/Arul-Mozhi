from functools import lru_cache
from google import genai
from google.genai import types
from app.config import settings
from app.schemas import FeedbackUpdate, NutritionTip, UserInput, WorkoutPlan

class GeminiServiceError(RuntimeError): pass

@lru_cache
def get_client():
    if not settings.gemini_api_key:
        raise GeminiServiceError("GEMINI_API_KEY is not configured. Add to .env")
    return genai.Client(api_key=settings.gemini_api_key)

def _generate(model, prompt, schema):
    try:
        r = get_client().models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
            )
        )
        return schema.model_validate_json(r.text)
    except Exception as e:
        raise GeminiServiceError(str(e))

def generate_workout_gemini(u: UserInput) -> WorkoutPlan:
    try:
        prompt = f"You are FitBuddy, create 7-day workout JSON for goal {u.goal}, level {u.level}, intensity {u.intensity}"
        return _generate(settings.gemini_workout_model, prompt, WorkoutPlan)
    except Exception as e:
        print(f"GEMINI FALLBACK USED: {e}")
        fallback = {
            "title": f"FitBuddy Plan for {u.goal}",
            "days": [
                {"day": "Monday", "focus": "Chest", "warmup": "5 min walk", "exercises": [{"name": "Push-ups", "sets": "3", "reps_or_duration": "15 reps", "rest": "60s"}], "cooldown": "Stretch"},
                {"day": "Tuesday", "focus": "Back", "warmup": "5 min jog", "exercises": [{"name": "Pull-ups", "sets": "3", "reps_or_duration": "8 reps", "rest": "90s"}], "cooldown": "Stretch"},
                {"day": "Wednesday", "focus": "Legs", "warmup": "5 min cycle", "exercises": [{"name": "Squats", "sets": "3", "reps_or_duration": "15 reps", "rest": "60s"}], "cooldown": "Stretch"},
                {"day": "Thursday", "focus": "Arms", "warmup": "5 min walk", "exercises": [{"name": "Bicep Curls", "sets": "3", "reps_or_duration": "12 reps", "rest": "60s"}], "cooldown": "Stretch"},
                {"day": "Friday", "focus": "Core", "warmup": "5 min walk", "exercises": [{"name": "Plank", "sets": "3", "reps_or_duration": "30 sec", "rest": "60s"}], "cooldown": "Stretch"},
                {"day": "Saturday", "focus": "Cardio", "warmup": "3 min walk", "exercises": [{"name": "Running", "sets": "1", "reps_or_duration": "30 min", "rest": "0s"}], "cooldown": "Walk"},
                {"day": "Sunday", "focus": "Rest", "warmup": "Rest", "exercises": [], "cooldown": "Recovery"},
            ]
        }
        return WorkoutPlan.model_validate(fallback)

def generate_nutrition_tip_with_flash(u: UserInput) -> NutritionTip:
    try:
        prompt = f"Give nutrition tip JSON for age {u.age}, weight {u.weight_kg}, goal {u.goal}"
        return _generate(settings.gemini_workout_model, prompt, NutritionTip)
    except Exception as e:
        print(f"NUTRITION FALLBACK: {e}")
        return NutritionTip(tip=f"For {u.goal}: Eat protein 1g/kg, 3L water, 8 hrs sleep. (Fallback)")

def update_workout_plan(u: UserInput, original: WorkoutPlan, feedback: str) -> WorkoutPlan:
    try:
        prompt = f"Revise this 7-day plan as per feedback: {feedback}. Profile: age {u.age}, goal {u.goal}. Original: {original.model_dump_json()}"
        return _generate(settings.gemini_workout_model, prompt, WorkoutPlan)
    except Exception as e:
        print(f"UPDATE FALLBACK: {e}")
        return original