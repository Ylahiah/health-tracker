import pandas as pd
from datetime import datetime, timedelta

def check_dropout_risk(nutrition_df, body_df, adherence_score, config):
    """
    Detects dropout risk flags based on user behavior.
    
    Flags:
    - 2 days no logging (consecutive)
    - 2 days excess calories (consecutive)
    - 7 days no weight change (plateau)
    - Adherence < 70%
    """
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    day_before = today - timedelta(days=2)
    
    daily_goal = config.get('calorias_objetivo', 2000)
    
    risk_flags = []
    
    # Check logging
    if not nutrition_df.empty:
        nutrition_df['date'] = pd.to_datetime(nutrition_df['date'], errors='coerce').dt.date
        last_2_days = nutrition_df[nutrition_df['date'].isin([yesterday, day_before])]
        if last_2_days.empty: # No logs in last 2 days
            risk_flags.append("⚠️ 2 días sin registrar comida")
            
        # Check excess calories
        excess_count = 0
        for day in [yesterday, day_before]:
            day_logs = nutrition_df[nutrition_df['date'] == day]
            if not day_logs.empty and day_logs['calories'].sum() > daily_goal:
                excess_count += 1
        
        if excess_count >= 2:
            risk_flags.append("⚠️ Calorías excedidas 2 días seguidos")
            
    else:
        risk_flags.append("⚠️ Sin registros de nutrición")

    # Check weight plateau
    if not body_df.empty:
        body_df['date'] = pd.to_datetime(body_df['date'], errors='coerce').dt.date
        last_7_days = body_df[body_df['date'] >= (today - timedelta(days=7))]
        if not last_7_days.empty and len(last_7_days) >= 2:
            weights = last_7_days['weight'].values
            if max(weights) - min(weights) < 0.2: # Less than 200g variation
                risk_flags.append("⚠️ Peso estancado (7 días sin cambio)")
                
    # Check adherence
    if adherence_score < 70:
        risk_flags.append(f"⚠️ Adherencia crítica ({int(adherence_score)}%)")
        
    return risk_flags
