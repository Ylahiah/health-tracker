import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from app.services import google_sheets_service as sheets
from app.config import settings

def get_user_profile():
    """Loads user profile from Google Sheets or session state."""
    # Try to load from session first
    if 'user_profile' in st.session_state:
        return st.session_state['user_profile']
        
    # Try to load from sheets
    try:
        df = sheets.load_data(settings.SHEET_PROFILE)
        if not df.empty:
            # Get latest profile
            latest = df.iloc[-1].to_dict()
            st.session_state['user_profile'] = latest
            return latest
    except Exception:
        pass
        
    # Default fallback
    return {
        'name': 'Usuario',
        'current_weight': 80.0,
        'goal_weight': 70.0,
        'height': 175,
        'age': 30,
        'gender': 'M',
        'activity_level': 1.2, # Sedentary
        'calorie_deficit': 500,
        'daily_calories': 2000,
        'tdee': 2500
    }

def save_user_profile(profile):
    """Saves profile to Google Sheets and session."""
    st.session_state['user_profile'] = profile
    
    # Add timestamp
    profile['updated_at'] = str(datetime.now())
    
    # Save to sheets
    sheets.add_row(settings.SHEET_PROFILE, profile)
    return True

def calculate_bmr(weight, height, age, gender):
    """Calculates Basal Metabolic Rate using Mifflin-St Jeor Equation."""
    if gender == 'M':
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

def calculate_tdee(bmr, activity_level):
    """Calculates Total Daily Energy Expenditure."""
    return bmr * activity_level

def calculate_daily_targets(profile):
    """Calculates daily calorie and macro targets."""
    bmr = calculate_bmr(profile['current_weight'], profile['height'], profile['age'], profile['gender'])
    tdee = calculate_tdee(bmr, profile['activity_level'])
    target_calories = tdee - profile['calorie_deficit']
    
    # Minimum safety check
    if profile['gender'] == 'M' and target_calories < 1500: target_calories = 1500
    if profile['gender'] == 'F' and target_calories < 1200: target_calories = 1200
    
    return int(target_calories), int(tdee)

def project_weight_loss(profile):
    """Projects weight loss over time based on deficit."""
    # 7700 kcal deficit ~= 1kg weight loss
    weekly_loss = (profile['calorie_deficit'] * 7) / 7700
    weeks_to_goal = abs(profile['current_weight'] - profile['goal_weight']) / weekly_loss
    return round(weekly_loss, 2), round(weeks_to_goal, 1)
