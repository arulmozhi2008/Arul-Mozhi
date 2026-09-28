from typing import Literal, List, Optional
from pydantic import BaseModel, Field, ConfigDict

Goal = Literal["general wellness", "muscle gain", "weight_loss", "flexibility", "cardio fitness"]
Intensity = Literal["low", "medium", "high"]
Experience = Literal["beginner", "intermediate", "advanced"]

class WorkoutExercise(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str = "Exercise"
    sets: Optional[str] = "3"
    reps: Optional[str] = "10"
    instruction: Optional[str] = "Do properly"
    rest: Optional[str] = "30s"
    duration: Optional[str] = None

class WorkoutDay(BaseModel):
    model_config = ConfigDict(extra="ignore")
    day: str = "Day 1"
    focus: str = "General"
    warmup: Optional[str] = "5 min walk"
    exercises: List[WorkoutExercise] = []
    cooldown: Optional[str] = "Stretch"

class WorkoutPlan(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str = "7 Day Plan"
    safety_note: str = "Stay hydrated"
    days: List[WorkoutDay] = Field(default_factory=list)

class NutritionTip(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str = "Nutrition Tip"
    tip: str = "Eat healthy and sleep 8 hrs"

class UserInput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: Optional[str] = "01"
    name: Optional[str] = None
    age: Optional[int] = 25
    weight: Optional[float] = 70
    height: Optional[float] = 170
    goal: Optional[Goal] = "general wellness"
    level: Optional[Experience] = "beginner"
    experience: Optional[Experience] = "beginner"
    intensity: Optional[Intensity] = "medium"
    # Extra aliases your main.py might be searching
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    fitness_level: Optional[str] = None

    def __getattr__(self, name):
        # This makes weight_kg work even if only weight is given
        if name == "weight_kg":
            return self.weight or self.__pydantic_extra__.get("weight_kg") or 70
        if name == "height_cm":
            return self.height or 170
        if name == "fitness_level":
            return self.level or self.experience or "beginner"
        return super().__getattr__(name) if hasattr(super(), '__getattr__') else None

    @property
    def get_weight(self):
        return self.weight_kg or self.weight or 70

class FeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    feedback: str

class FeedbackUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    feedback: str = Field(default="good")