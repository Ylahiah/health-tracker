import streamlit as st
from datetime import datetime
from app.services import google_sheets_service as sheets
from app.config import settings

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
                profile['start_date'] = profile.get('updated_at', str(datetime.now().date()))
                
            if 'peso_inicial' not in profile or not profile['peso_inicial']:
                profile['peso_inicial'] = profile.get('current_weight', 80.0)
                
            if 'peso_meta' not in profile:
                profile['peso_meta'] = profile.get('goal_weight', 70.0)
                
            if 'calorias_objetivo' not in profile:
                profile['calorias_objetivo'] = profile.get('daily_calories', settings.DEFAULT_CALORIE_GOAL)
                
            if 'proteina_objetivo' not in profile:
                # Default 2g per kg of goal weight or current weight
                weight = profile.get('current_weight', 80.0)
                profile['proteina_objetivo'] = int(weight * 2.0)

            return profile
    except Exception as e:
        print(f"Error loading config: {e}")
        pass
        
    # Default fallback
    return {
        'name': 'Usuario',
        'start_date': str(datetime.now().date()),
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
        'age': 30
    }
