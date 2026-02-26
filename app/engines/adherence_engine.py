import pandas as pd
from datetime import datetime, timedelta
from app.config import settings

def calculate_weekly_adherence(nutrition_df, habits_df, config):
    """
    Calculates adherence score based on the last 7 days.
    
    Components:
    - Days in deficit (calories < daily_goal)
    - Protein met (protein >= protein_goal)
    - Workout done (from habits)
    - Meal logging (entry exists)
    - Elite habits completed (>= 4 habits per day)
    """
    today = datetime.now().date()
    start_date = today - timedelta(days=6) # Last 7 days including today
    
    # Pre-process dates
    if not nutrition_df.empty:
        nutrition_df['date'] = pd.to_datetime(nutrition_df['date'], errors='coerce').dt.date
    if not habits_df.empty:
        habits_df['date'] = pd.to_datetime(habits_df['date'], errors='coerce').dt.date
        
    # Initialize counters
    days_in_deficit = 0
    protein_met = 0
    workout_done = 0
    logging_days = 0
    elite_habits_days = 0
    
    daily_goal = config.get('calorias_objetivo', settings.DEFAULT_CALORIE_GOAL)
    protein_goal = config.get('proteina_objetivo', 160)
    
    # Loop through last 7 days
    for i in range(7):
        current_day = start_date + timedelta(days=i)
        
        # Nutrition checks
        day_nutrition = pd.DataFrame()
        if not nutrition_df.empty:
            day_nutrition = nutrition_df[nutrition_df['date'] == current_day]
            
        if not day_nutrition.empty:
            logging_days += 1
            total_cal = day_nutrition['calories'].sum()
            total_pro = day_nutrition['protein'].sum()
            
            if total_cal <= daily_goal:
                days_in_deficit += 1
            if total_pro >= protein_goal:
                protein_met += 1
                
        # Habits checks
        day_habits = pd.DataFrame()
        if not habits_df.empty:
            day_habits = habits_df[habits_df['date'] == current_day]
            
        if not day_habits.empty:
            # Check for workout
            workout = day_habits[day_habits['habit_name'].str.contains("ENTRENAMIENTO", case=False, na=False)]
            if not workout.empty and (workout['status'] == "Completado").any():
                workout_done += 1
            
            # Check elite habits count
            completed_count = day_habits[day_habits['status'] == "Completado"].drop_duplicates(subset=['habit_name']).shape[0]
            if completed_count >= 4:
                elite_habits_days += 1

    # Calculate scores (max 7 points per category)
    score_deficit = (days_in_deficit / 7) * 100
    score_protein = (protein_met / 7) * 100
    score_workout = (workout_done / 7) * 100 # Assuming workout every day? Maybe adjust if workout plan is different. Let's assume daily adherence goal for now.
    score_logging = (logging_days / 7) * 100
    score_elite = (elite_habits_days / 7) * 100
    
    # Weighted average or simple average? Let's do simple average of the 5 pillars
    avg_adherence = (score_deficit + score_protein + score_workout + score_logging + score_elite) / 5
    
    # Classification
    if avg_adherence >= 90:
        level = "ÉLITE"
    elif avg_adherence >= 75:
        level = "ALTO"
    elif avg_adherence >= 60:
        level = "MEDIO"
    else:
        level = "RIESGO"
        
    return avg_adherence, level, {
        "deficit": score_deficit,
        "protein": score_protein,
        "workout": score_workout,
        "logging": score_logging,
        "elite": score_elite
    }
