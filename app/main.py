import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
import pandas as pd
from datetime import datetime
from app.services import google_sheets_service as sheets
from app.config import settings
from app.engines import config_manager, phase_engine, adherence_engine, risk_engine, projection_engine, ai_feedback_engine

st.set_page_config(
    page_title="Health Tracker Élite",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Initialize sheets if needed (lazy init)
    if 'sheets_initialized' not in st.session_state:
        sheets.init_sheets()
        st.session_state['sheets_initialized'] = True

    # 1. Load Config (User Profile + Targets)
    config = config_manager.load_config()
    
    st.title(f"🧬 Dashboard Élite: {config.get('name', 'Atleta')}")
    
    today = datetime.now().date()
    
    # 2. Load Data (Cached)
    with st.spinner("Analizando datos fisiológicos..."):
        body_df = sheets.load_data(settings.SHEET_BODY_METRICS)
        nutrition_df = sheets.load_data(settings.SHEET_NUTRITION_LOG)
        water_df = sheets.load_data(settings.SHEET_WATER_LOG)
        meds_df = sheets.load_data(settings.SHEET_MEDICATION_LOG)
        habits_df = sheets.load_data(settings.SHEET_HABITS_LOG)
        
    # 3. Process Logic Engines
    
    # A. Phase Engine
    phase_name, phase_desc = phase_engine.determine_phase(config.get('start_date'))
    
    # B. Adherence Engine
    adherence_score, adherence_level, adherence_details = adherence_engine.calculate_weekly_adherence(nutrition_df, habits_df, config)
    
    # C. Risk Engine
    risk_flags = risk_engine.check_dropout_risk(nutrition_df, body_df, adherence_score, config)
    
    # D. Projection Engine
    weekly_loss, target_date, real_deficit = projection_engine.predict_progress(nutrition_df, config)
    
    # E. AI Feedback Engine (Gemini)
    weight_change = 0
    if not body_df.empty:
        # Calculate recent change (last 7 days or total?)
        # Let's say last vs first of last 7 days or just total logic inside prompt
        # Passing simple scalar to AI for now
        current_w = config.get('current_weight', 0)
        start_w = config.get('peso_inicial', 0)
        weight_change = round(current_w - start_w, 1)

    ai_message = ai_feedback_engine.generate_coach_feedback(
        phase_name, 
        adherence_level, 
        weight_change, 
        risk_flags, 
        config.get('name', 'Atleta')
    )

    # --- DASHBOARD LAYOUT ---
    
    # Top Section: Phase & Coach Message
    c1, c2 = st.columns([1, 2])
    with c1:
        st.info(f"**FASE ACTUAL:** {phase_name}\n\n_{phase_desc}_")
    with c2:
        if risk_flags:
            st.error(f"⚠️ **ATENCIÓN:** {ai_message}")
        elif adherence_level == "ÉLITE":
            st.success(f"🏆 **COACH:** {ai_message}")
        else:
            st.info(f"💡 **COACH:** {ai_message}")
            
    # Risk Flags Banner
    if risk_flags:
        for flag in risk_flags:
            st.warning(flag)

    st.markdown("---")
    
    # Section: TODAY'S METRICS
    st.subheader("📅 Hoy")
    
    # Calculate Today's numbers
    today_calories = 0
    if not nutrition_df.empty:
        nutrition_df['date'] = pd.to_datetime(nutrition_df['date'], errors='coerce').dt.date
        today_nutrition = nutrition_df[nutrition_df['date'] == today]
        today_calories = today_nutrition['calories'].sum()
        
    daily_goal = config.get('calorias_objetivo', 2000)
    remaining = daily_goal - today_calories
    
    # Habits Today
    today_elite_habits = 0
    if not habits_df.empty:
        habits_df['date'] = pd.to_datetime(habits_df['date'], errors='coerce').dt.date
        today_habits = habits_df[habits_df['date'] == today]
        if not today_habits.empty:
            today_habits = today_habits.drop_duplicates(subset=['habit_name'], keep='last')
            # Count elite habits
            for h in settings.ELITE_HABITS:
                 if not today_habits[today_habits['habit_name'] == h].empty:
                     if today_habits[today_habits['habit_name'] == h].iloc[0]['status'] == "Completado":
                         today_elite_habits += 1

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Calorías Restantes", f"{int(remaining)}", f"Meta: {daily_goal}")
    k2.metric("Hábitos Élite", f"{today_elite_habits}/5", delta_color="off")
    k3.metric("Adherencia Semanal", f"{int(adherence_score)}%", adherence_level)
    k4.metric("Déficit Real (7d)", f"{real_deficit} kcal", "Promedio diario")

    st.markdown("---")

    # Section: PROGRESS & PROJECTION
    st.subheader("🚀 Proyección y Progreso")
    
    p1, p2, p3 = st.columns(3)
    
    with p1:
        st.write("#### Ritmo Actual")
        st.write(f"Perdiendo **{weekly_loss} kg/semana**")
        st.caption("Basado en tu déficit real de la última semana.")
        
    with p2:
        st.write("#### Meta Estimada")
        if target_date:
            st.write(f"Llegada: **{target_date}**")
        else:
            st.write("Datos insuficientes o sin déficit.")
        st.caption(f"Peso Meta: {config.get('peso_meta')} kg")

    with p3:
        st.write("#### Detalles de Adherencia")
        st.progress(adherence_score / 100)
        with st.expander("Ver desglose"):
            st.write(f"- Déficit Calórico: {int(adherence_details['deficit'])}%")
            st.write(f"- Proteína: {int(adherence_details['protein'])}%")
            st.write(f"- Entrenamiento: {int(adherence_details['workout'])}%")
            st.write(f"- Registro Comidas: {int(adherence_details['logging'])}%")
            st.write(f"- Hábitos Élite: {int(adherence_details['elite'])}%")

    # Quick Actions (Bottom)
    st.divider()
    c1, c2, c3 = st.columns(3)
    if c1.button("🍽️ Registrar Comida", use_container_width=True):
        st.switch_page("pages/2_Nutricion.py")
    if c2.button("✅ Checklist Hábitos", use_container_width=True):
        st.switch_page("pages/5_Habitos.py")
    if c3.button("⚖️ Actualizar Peso", use_container_width=True):
        st.switch_page("pages/1_Progreso_Corporal.py")

if __name__ == "__main__":
    main()
