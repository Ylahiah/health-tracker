import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
import pandas as pd
from datetime import datetime
from app.services import google_sheets_service as sheets
from app.services import analytics_service as analytics
from app.services import profile_service
from app.config import settings

st.set_page_config(
    page_title="Health Tracker",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Initialize sheets if needed (lazy init)
    if 'sheets_initialized' not in st.session_state:
        sheets.init_sheets()
        st.session_state['sheets_initialized'] = True

    # Ensure profile is loaded
    user_profile = profile_service.get_user_profile()

    st.title(f"💪 Dashboard Principal: {user_profile.get('name', 'Usuario')}")
    
    today = datetime.now().date()
    
    # --- Load Data ---
    with st.spinner("Cargando datos de Google Sheets..."):
        body_df = sheets.load_data(settings.SHEET_BODY_METRICS)
        nutrition_df = sheets.load_data(settings.SHEET_NUTRITION_LOG)
        water_df = sheets.load_data(settings.SHEET_WATER_LOG)
        meds_df = sheets.load_data(settings.SHEET_MEDICATION_LOG)
        habits_df = sheets.load_data(settings.SHEET_HABITS_LOG)
    
    # --- Calculate Daily Metrics ---

    # Goal from profile
    daily_goal = user_profile.get('daily_calories', settings.DEFAULT_CALORIE_GOAL)
    
    # Nutrition
    today_calories = 0
    if not nutrition_df.empty:
        # Convert date column to datetime objects safely
        nutrition_df['date'] = pd.to_datetime(nutrition_df['date'], errors='coerce').dt.date
        today_nutrition = nutrition_df[nutrition_df['date'] == today]
        today_calories = today_nutrition['calories'].sum()

    calories_remaining = daily_goal - today_calories
        
    # Water
    today_water = 0
    if not water_df.empty:
        water_df['date'] = pd.to_datetime(water_df['date'], errors='coerce').dt.date
        today_water_log = water_df[water_df['date'] == today]
        today_water = today_water_log['amount_ml'].sum()

    # Weight
    current_weight = user_profile.get('current_weight', 0)
    weight_delta = 0
    if not body_df.empty:
        body_df['date'] = pd.to_datetime(body_df['date'], errors='coerce').dt.date
        body_df = body_df.sort_values(by="date", ascending=True)
        # Use the latest weight from logs if available, otherwise profile
        if not body_df.empty:
            last_log_weight = body_df.iloc[-1]['weight']
            # Optionally update current weight display if logs are newer
            # current_weight = last_log_weight 
            
            if len(body_df) > 1:
                start_weight = body_df.iloc[0]['weight']
                weight_delta = round(last_log_weight - start_weight, 1)

    # Meds
    meds_taken = False
    if not meds_df.empty:
        meds_df['date'] = pd.to_datetime(meds_df['date'], errors='coerce').dt.date
        today_meds = meds_df[meds_df['date'] == today]
        if not today_meds.empty:
            meds_taken = True

    # Habits Score
    habit_score = 0
    habit_msg = "Sin registros hoy"
    score_color = "blue" # default
    
    if not habits_df.empty:
        habits_df['date'] = pd.to_datetime(habits_df['date'], errors='coerce').dt.date
        today_habits = habits_df[habits_df['date'] == today]
        
        if not today_habits.empty:
            # Deduplicate keeping last
            today_habits = today_habits.drop_duplicates(subset=['habit_name'], keep='last')
            
            completed_count = 0
            for h in settings.ELITE_HABITS:
                record = today_habits[today_habits['habit_name'] == h]
                if not record.empty and record.iloc[0]['status'] == "Completado":
                    completed_count += 1
            
            habit_score = completed_count
            
            if habit_score == 5:
                habit_msg = "🔥 5/5 Día Perfecto"
                score_color = "green"
            elif habit_score == 4:
                habit_msg = "✅ 4/5 Día Efectivo (Pérdida de grasa)"
                score_color = "green"
            elif habit_score == 3:
                habit_msg = "⚠️ 3/5 Aún Funcional"
                score_color = "orange"
            else:
                habit_msg = f"❌ {habit_score}/5 Día a Corregir"
                score_color = "red"
            
    # Phase
    start_date_str = user_profile.get('updated_at', str(datetime.now().date()))
    try:
        start_date = pd.to_datetime(start_date_str).date()
    except:
        start_date = datetime.now().date()
        
    if not body_df.empty:
        start_date = body_df.iloc[0]['date']
        
    phase_name, week_num = analytics.calculate_phase(start_date)

    # Motivation
    motivation_msg = analytics.get_motivation_message(nutrition_df, body_df, daily_goal)
    
    # --- Motivation Banner ---
    st.info(motivation_msg)

    # --- Daily Score Banner ---
    if score_color == "green":
        st.success(f"🎯 PUNTUACIÓN DEL DÍA: **{habit_msg}**")
    elif score_color == "orange":
        st.warning(f"🎯 PUNTUACIÓN DEL DÍA: **{habit_msg}**")
    elif score_color == "red":
        st.error(f"🎯 PUNTUACIÓN DEL DÍA: **{habit_msg}**")
    else:
        st.info(f"🎯 PUNTUACIÓN DEL DÍA: **{habit_msg}**")

    # --- Display Metrics ---
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Peso Actual", f"{current_weight} kg", f"{weight_delta} kg desde inicio")
        st.caption(f"Meta: {user_profile.get('goal_weight')} kg")
        
    with col2:
        st.metric("Calorías Hoy", f"{int(today_calories)}", f"{int(calories_remaining)} restantes",
                 delta_color="normal" if calories_remaining > 0 else "inverse")
        st.caption(f"Meta: {daily_goal} kcal")
        
    with col3:
        st.metric("Agua Hoy", f"{today_water} ml", f"{settings.DEFAULT_WATER_GOAL - today_water} ml restantes")
        
    with col4:
        st.metric("Medicación", "✅ Tomada" if meds_taken else "⚠️ Pendiente")

    st.markdown("---")
    
    # --- Profile Summary Section (New) ---
    st.subheader("📋 Resumen del Perfil")
    with st.expander("Ver detalles del perfil", expanded=True):
        p1, p2, p3 = st.columns(3)
        with p1:
            st.write(f"**Nombre:** {user_profile.get('name', '-')}")
            st.write(f"**Edad:** {user_profile.get('age', '-')} años")
            st.write(f"**Género:** {user_profile.get('gender', '-')}")
        with p2:
            st.write(f"**Altura:** {user_profile.get('height', '-')} cm")
            st.write(f"**TDEE (Mantenimiento):** {user_profile.get('tdee', '-')} kcal")
            st.write(f"**Déficit Configurado:** {user_profile.get('calorie_deficit', '-')} kcal")
        with p3:
            st.write(f"**Nivel Actividad:** {user_profile.get('activity_level', '-')}")
            st.write(f"**Última Actualización:** {user_profile.get('updated_at', '-')}")
            if st.button("✏️ Editar Perfil"):
                st.switch_page("pages/6_Configuracion.py")

    st.markdown("---")

    # --- Quick Actions ---
    st.subheader("Acciones Rápidas")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        if st.button("💧 +250ml Agua", use_container_width=True):
            row = {
                "date": str(today),
                "amount_ml": 250,
                "goal_ml": settings.DEFAULT_WATER_GOAL
            }
            if sheets.add_row(settings.SHEET_WATER_LOG, row):
                st.toast("Agua registrada!")
                st.rerun()
            else:
                st.error("Error al guardar agua.")

    with c2:
        if st.button("💊 Registrar Meds", use_container_width=True):
            row = {
                "date": str(today),
                "dose_mg": 0,
                "time_taken": str(datetime.now().time()),
                "notes": "Quick add"
            }
            if sheets.add_row(settings.SHEET_MEDICATION_LOG, row):
                st.toast("Medicación registrada!")
                st.rerun()
            else:
                st.error("Error al guardar medicación.")
            
    with c3:
        if st.button("❤️ Registrar Comida", use_container_width=True):
            st.switch_page("pages/2_Nutricion.py")
            
    # --- Historical Progress (Weight) ---
    if not body_df.empty:
        st.subheader("Progreso de Peso")
        st.line_chart(body_df, x='date', y='weight')

if __name__ == "__main__":
    main()
