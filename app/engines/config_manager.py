import streamlit as st
from datetime import datetime
from app.services import google_sheets_service as sheets
from app.config import settings
from app.utils import time_utils

def _safe_float(value, default: float) -> float:
    if value is None:
        return float(default)
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if s == "" or s.lower() in ["nan", "none"]:
        return float(default)
    try:
        return float(s)
    except Exception:
        return float(default)


def _safe_int(value, default: int) -> int:
    return int(round(_safe_float(value, float(default))))


def load_config():
    """
    Loads user configuration/profile from Google Sheets with caching.
    Ensures all required fields for the system are present.
    """
    try:
        df = sheets.load_data(settings.SHEET_PROFILE)
        if not df.empty:
            profile = df.iloc[-1].to_dict()
            
            # Normalize and fill missing fields
            if 'start_date' not in profile or not profile['start_date']:
                profile['start_date'] = profile.get('updated_at', str(time_utils.local_today()))
                
            if 'peso_inicial' not in profile or str(profile.get('peso_inicial', '')).strip() == "":
                profile['peso_inicial'] = profile.get('current_weight', 80.0)
                
            if 'peso_meta' not in profile or str(profile.get('peso_meta', '')).strip() == "":
                profile['peso_meta'] = profile.get('goal_weight', 70.0)
                
            if 'calorias_objetivo' not in profile or str(profile.get('calorias_objetivo', '')).strip() == "":
                profile['calorias_objetivo'] = profile.get('daily_calories', settings.DEFAULT_CALORIE_GOAL)
                
            if 'proteina_objetivo' not in profile or str(profile.get('proteina_objetivo', '')).strip() == "":
                weight = _safe_float(profile.get('current_weight', 80.0), 80.0)
                profile['proteina_objetivo'] = int(weight * 2.0)

            if 'fasting_plan_hours' not in profile or not profile['fasting_plan_hours']:
                profile['fasting_plan_hours'] = 16

            profile['current_weight'] = _safe_float(profile.get('current_weight', 80.0), 80.0)
            profile['goal_weight'] = _safe_float(profile.get('goal_weight', 70.0), 70.0)
            profile['peso_inicial'] = _safe_float(profile.get('peso_inicial', profile['current_weight']), profile['current_weight'])
            profile['peso_meta'] = _safe_float(profile.get('peso_meta', profile['goal_weight']), profile['goal_weight'])
            profile['calorias_objetivo'] = _safe_float(profile.get('calorias_objetivo', settings.DEFAULT_CALORIE_GOAL), settings.DEFAULT_CALORIE_GOAL)
            profile['proteina_objetivo'] = _safe_float(profile.get('proteina_objetivo', 160), 160)
            profile['tdee'] = _safe_float(profile.get('tdee', profile.get('tdee', 2500)), 2500)
            profile['deficit_calorico'] = _safe_float(profile.get('deficit_calorico', profile.get('calorie_deficit', 500)), 500)
            profile['fasting_plan_hours'] = _safe_int(profile.get('fasting_plan_hours', 16), 16)

            return profile
    except Exception as e:
        print(f"Error loading config: {e}")
        pass
        
    # Default fallback
    return {
        'name': 'Usuario',
        'start_date': str(time_utils.local_today()),
        'current_weight': 80.0,
        'peso_inicial': 80.0,
        'peso_meta': 70.0,
        'calorias_objetivo': 2000,
        'proteina_objetivo': 160,
        'tdee': 2500,
        'deficit_calorico': 500,
        'activity_level': 1.2,
        'gender': 'M',
        'height': 175,
        'age': 30,
        'fasting_plan_hours': 16
    }
