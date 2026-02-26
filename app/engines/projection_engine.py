from datetime import datetime, timedelta
import pandas as pd
from app.config import settings

def predict_progress(nutrition_df, config):
    """
    Predicts weight loss progress based on average REAL calorie deficit over the last 7 days.
    """
    goal_calories = config.get('calorias_objetivo', settings.DEFAULT_CALORIE_GOAL)
    current_weight = config.get('current_weight', 80.0)
    goal_weight = config.get('peso_meta', 70.0)
    configured_deficit = config.get('deficit_calorico', 500)
    
    # Calculate real average deficit from last 7 days
    real_deficit = configured_deficit # Default fallback
    
    if not nutrition_df.empty:
        nutrition_df['date'] = pd.to_datetime(nutrition_df['date'], errors='coerce').dt.date
        today = datetime.now().date()
        start_date = today - timedelta(days=6)
        last_7_days = nutrition_df[nutrition_df['date'] >= start_date]
        
        if not last_7_days.empty:
            avg_consumed = last_7_days.groupby('date')['calories'].sum().mean()
            real_deficit = goal_calories - avg_consumed
            
    # Formula: 7700 kcal = 1kg fat
    # Ensure positive deficit for calculation, otherwise 0 loss
    if real_deficit < 0:
        real_deficit = 0
        
    weekly_loss_kg = (real_deficit * 7) / 7700.0
    
    remaining_weight = current_weight - goal_weight
    
    if remaining_weight <= 0:
        weeks_needed = 0
        target_date = datetime.now().date()
    elif weekly_loss_kg > 0:
        weeks_needed = remaining_weight / weekly_loss_kg
        target_date = datetime.now().date() + timedelta(weeks=weeks_needed)
    else:
        weeks_needed = 999
        target_date = None # Never
        
    return round(weekly_loss_kg, 2), target_date, int(real_deficit)
