import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_bmi(weight_kg, height_cm):
    """
    Calculates Body Mass Index (BMI).
    """
    if not height_cm or height_cm <= 0:
        return 0
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)

def calculate_tmb(weight_kg, height_cm, age, gender, activity_level="sedentary"):
    """
    Calculates Basal Metabolic Rate (BMR) using Mifflin-St Jeor Equation.
    Activity level multipliers:
    - sedentary: 1.2
    - lightly_active: 1.375
    - moderately_active: 1.55
    - very_active: 1.725
    - extra_active: 1.9
    """
    if gender.lower() == "male":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
        
    multipliers = {
        "sedentary": 1.2,
        "lightly_active": 1.375,
        "moderately_active": 1.55,
        "very_active": 1.725,
        "extra_active": 1.9
    }
    
    return round(bmr * multipliers.get(activity_level, 1.2))

def project_weight_loss(current_weight, goal_weight, weekly_loss_kg):
    """
    Projects the date to reach the goal weight based on weekly loss rate.
    """
    if weekly_loss_kg <= 0:
        return None # No loss or gain
    
    diff = current_weight - goal_weight
    if diff <= 0:
        return datetime.now().date()
        
    weeks_needed = diff / weekly_loss_kg
    days_needed = weeks_needed * 7
    
    target_date = datetime.now() + timedelta(days=days_needed)
    return target_date.date()

def calculate_phase(start_date):
    """
    Calculates the current phase based on weeks since start.
    Phase 1: Week 0-4 (Adaptation)
    Phase 2: Week 5-12 (Progression)
    Phase 3: Week 12+ (Maintenance/Advanced)
    """
    if not start_date:
        return "Fase 1: Adaptación", 0
        
    if isinstance(start_date, str):
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        except:
            return "Fase 1: Adaptación", 0
            
    today = datetime.now().date()
    days_diff = (today - start_date).days
    weeks = days_diff // 7
    
    if weeks <= 4:
        return "Fase 1: Adaptación", weeks
    elif weeks <= 12:
        return "Fase 2: Progresión", weeks
    else:
        return "Fase 3: Mantenimiento", weeks

def get_motivation_message(nutrition_df, weight_df, calorie_goal):
    """
    Returns a motivational message based on recent data.
    """
    today = datetime.now().date()
    
    # Check today's logs
    has_logged_today = False
    calories_today = 0
    
    if not nutrition_df.empty:
        # Ensure date is date object
        nutrition_df['date'] = pd.to_datetime(nutrition_df['date']).dt.date
        today_log = nutrition_df[nutrition_df['date'] == today]
        if not today_log.empty:
            has_logged_today = True
            calories_today = today_log['calories'].sum()
            
    if not has_logged_today:
        return "📢 ¡No olvides registrar tus comidas hoy! La constancia es clave."
        
    if calories_today > calorie_goal:
        return "⚠️ Te has pasado de calorías. ¡Trata de cenar ligero o caminar un poco más!"
        
    # Check weight plateau (no change in 7 days)
    if not weight_df.empty and len(weight_df) > 1:
        weight_df['date'] = pd.to_datetime(weight_df['date']).dt.date
        weight_df = weight_df.sort_values('date', ascending=False)
        
        latest_weight = weight_df.iloc[0]['weight']
        week_ago = today - timedelta(days=7)
        
        old_weights = weight_df[weight_df['date'] <= week_ago]
        if not old_weights.empty:
            prev_weight = old_weights.iloc[0]['weight']
            if abs(latest_weight - prev_weight) < 0.1:
                return "📉 El peso está estable. ¡Es normal! Revisa tu ingesta de sodio o agua."

    return "🔥 ¡Vas muy bien! Sigue así."

def get_weekly_summary(df, date_col='date', metric_col='weight'):
    """
    Returns weekly average and change for a given metric.
    """
    if df.empty:
        return {}
        
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(by=date_col)
    
    # Resample by week
    weekly = df.set_index(date_col).resample('W')[metric_col].mean()
    
    return weekly

def analyze_medication_impact(meds_df, weight_df):
    """
    Analyzes the correlation between medication dose and weight loss/appetite.
    """
    # Merge dataframes on date
    # Implementation depends on data availability
    pass
