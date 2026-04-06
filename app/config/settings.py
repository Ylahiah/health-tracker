import os
import streamlit as st

# App Runtime Settings
try:
    TIMEZONE = st.secrets.get("timezone", os.getenv("APP_TIMEZONE", "America/Mexico_City"))
except Exception:
    TIMEZONE = os.getenv("APP_TIMEZONE", "America/Mexico_City")

# Sheet Names
SHEET_BODY_METRICS = "body_metrics"
SHEET_NUTRITION_LOG = "nutrition_log"
SHEET_WATER_LOG = "water_log"
SHEET_MEDICATION_LOG = "medication_log"
SHEET_HABITS_LOG = "habits_log"
SHEET_GOALS = "goals"
SHEET_PROFILE = "user_profile"
SHEET_FASTING_LOG = "fasting_log"

ALL_SHEETS = [
    SHEET_BODY_METRICS,
    SHEET_NUTRITION_LOG,
    SHEET_WATER_LOG,
    SHEET_MEDICATION_LOG,
    SHEET_HABITS_LOG,
    SHEET_GOALS,
    SHEET_PROFILE,
    SHEET_FASTING_LOG
]

# Column Definitions
COLS_BODY = ["date", "weight", "body_fat_percentage", "waist", "hip", "chest", "arms", "thighs", "notes"]
COLS_NUTRITION = ["date", "calories", "protein", "carbs", "fats", "notes"]
COLS_WATER = ["date", "amount_ml", "goal_ml"]
COLS_MEDS = [
    "date", "dose_mg", "time_taken", "appetite_level", "energy_level", 
    "heart_rate", "blood_pressure", "sleep_quality", "side_effects", "adherence", "notes"
]
COLS_HABITS = ["date", "habit_name", "status", "notes"]
COLS_GOALS = ["category", "metric", "target_value", "start_date", "target_date", "status"]
COLS_FASTING = ["date", "start_at", "end_at", "plan_hours", "status", "notes"]
COLS_PROFILE = [
    "name", "age", "gender", "height", "current_weight", "goal_weight", 
    "activity_level", "calorie_deficit", "daily_calories", "tdee", 
    "updated_at", "start_date", "peso_inicial", "proteina_objetivo", "fecha_objetivo_estimada", "fasting_plan_hours"
]

# Default Goals (fallback)
DEFAULT_CALORIE_GOAL = 2000
DEFAULT_WATER_GOAL = 2500

# Elite Habits Definition
ELITE_HABITS = [
    "🏋️ ENTRENAMIENTO (Cardio/Fuerza)",
    "🥩 PROTEÍNA (160g+)",
    "💧 AGUA (3-4L)",
    "🌙 CONTROL NOCTURNO (Sin atracón >9pm)",
    "💊 SUPLEMENTOS (Creatina + Metformina)"
]
