import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from app.services import google_sheets_service as sheets
from app.config import settings
from app.engines import config_manager, phase_engine, adherence_engine, risk_engine, projection_engine, ai_feedback_engine
from app.engines import fasting_engine
from app.utils import time_utils
from app.components import ui

st.set_page_config(
    page_title="Health Tracker Élite",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    ui.inject_global_style()

    # Initialize sheets if needed (lazy init)
    if 'sheets_initialized' not in st.session_state:
        sheets.init_sheets()
        st.session_state['sheets_initialized'] = True

    # 1. Load Config (User Profile + Targets)
    config = config_manager.load_config()
    
    ui.title("Calculadora de déficit calórico", f"{config.get('name', 'Atleta')} · Hoy y progreso en una sola pantalla")
    
    today = time_utils.local_today()
    yesterday = today - timedelta(days=1)
    
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

    daily_goal = float(config.get('calorias_objetivo', 2000))
    protein_goal = float(config.get('proteina_objetivo', 160))
    tdee = float(config.get('tdee', daily_goal))

    today_calories = 0
    today_protein = 0
    today_carbs = 0
    today_fats = 0
    if not nutrition_df.empty:
        nutrition_df['date'] = pd.to_datetime(nutrition_df['date'], errors='coerce').dt.date
        today_nutrition = nutrition_df[nutrition_df['date'] == today]
        if not today_nutrition.empty:
            today_nutrition['calories'] = pd.to_numeric(today_nutrition['calories'], errors='coerce').fillna(0)
            today_nutrition['protein'] = pd.to_numeric(today_nutrition['protein'], errors='coerce').fillna(0)
            today_nutrition['carbs'] = pd.to_numeric(today_nutrition.get('carbs', 0), errors='coerce').fillna(0)
            today_nutrition['fats'] = pd.to_numeric(today_nutrition.get('fats', 0), errors='coerce').fillna(0)
            today_calories = today_nutrition['calories'].sum()
            today_protein = today_nutrition['protein'].sum()
            today_carbs = today_nutrition['carbs'].sum()
            today_fats = today_nutrition['fats'].sum()
        
    remaining = daily_goal - today_calories
    protein_remaining = protein_goal - today_protein

    today_water = 0
    if not water_df.empty:
        water_df['date'] = pd.to_datetime(water_df['date'], errors='coerce').dt.date
        today_water_df = water_df[water_df['date'] == today]
        if not today_water_df.empty:
            today_water_df['amount_ml'] = pd.to_numeric(today_water_df['amount_ml'], errors='coerce').fillna(0)
            today_water = today_water_df['amount_ml'].sum()
    water_goal = settings.DEFAULT_WATER_GOAL
    water_remaining = water_goal - today_water
    
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

    fats_goal = max(int((daily_goal * 0.25) / 9), 40)
    carbs_goal = max(int((daily_goal - (protein_goal * 4) - (fats_goal * 9)) / 4), 0)

    streak = 0
    if not habits_df.empty:
        hdf = habits_df.copy()
        hdf['date'] = pd.to_datetime(hdf['date'], errors='coerce').dt.date
        hdf = hdf.dropna(subset=['date'])
        if not hdf.empty:
            hdf = hdf[hdf['habit_name'].isin(settings.ELITE_HABITS)]
            hdf = hdf.drop_duplicates(subset=['date', 'habit_name'], keep='last')
            day_scores = hdf[hdf['status'] == "Completado"].groupby('date')['habit_name'].nunique()
            d = today
            while True:
                if day_scores.get(d, 0) >= 4:
                    streak += 1
                    d = d - timedelta(days=1)
                else:
                    break

    phone_cols = st.columns([1, 1.15, 1])
    with phone_cols[1]:
        ui.phone_shell_start()
        ui.phone_top("Hoy", time_utils.format_date_es(today), streak)
        burned = max(int(tdee - today_calories), 0)
        ui.mini_metrics("Comido", f"{int(today_calories)}", "Quemado", f"{burned}")

        st.markdown('<div class="ht-phone-card">', unsafe_allow_html=True)
        st.plotly_chart(ui.gauge_kcal(remaining=remaining, goal=daily_goal), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        ui.macros_row(
            [
                {"name": "Carbohidratos", "icon": "🌾", "value": today_carbs, "goal": carbs_goal, "color": "rgba(245,158,11,0.95)"},
                {"name": "Proteínas", "icon": "🥩", "value": today_protein, "goal": protein_goal, "color": "rgba(255,75,75,0.95)"},
                {"name": "Grasas", "icon": "🫒", "value": today_fats, "goal": fats_goal, "color": "rgba(56,189,248,0.95)"},
            ]
        )

        plan_hours = int(config.get("fasting_plan_hours", 16))
        fast_state = fasting_engine.get_state(plan_hours=plan_hours)
        st.markdown('<div class="ht-phone-card">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="ht-row"><div><div class="ht-row-title">⏱️ AYUNO</div><div class="ht-row-sub">Ayuno de {plan_hours}h</div></div></div>',
            unsafe_allow_html=True,
        )
        if fast_state.active and fast_state.start_at and fast_state.target_end_at:
            st.markdown(
                f"<div class='ht-mini-grid' style='margin-top:0.35rem;'>"
                f"<div><div class='ht-mini-label'>Última comida</div><div class='ht-mini-value'>{time_utils.format_time_ampm(fast_state.start_at)}</div></div>"
                f"<div style='text-align:right;'><div class='ht-mini-label'>Primera comida</div><div class='ht-mini-value'>{time_utils.format_time_ampm(fast_state.target_end_at)}</div></div>"
                f"</div>",
                unsafe_allow_html=True,
            )
            total_seconds = plan_hours * 3600
            elapsed_seconds = min(max(int(fast_state.elapsed.total_seconds()), 0), total_seconds)
            st.progress(elapsed_seconds / total_seconds)
            rem = fast_state.remaining
            rem_h = int(rem.total_seconds() // 3600)
            rem_m = int((rem.total_seconds() % 3600) // 60)
            st.caption(f"Tiempo restante: {rem_h}h {rem_m}m")
            end_btn = st.button("Finalizar ayuno", key="fast_end_btn", use_container_width=True)
            if end_btn:
                if fasting_engine.end_fast():
                    st.rerun()
        else:
            st.caption("Actívalo para calcular tus ventanas de comida y dar seguimiento.")
            start_btn = st.button("Iniciar ayuno", key="fast_start_btn", use_container_width=True)
            if start_btn:
                if fasting_engine.start_fast(plan_hours=plan_hours):
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        ui.water_row(int(today_water), int(water_goal), cups=5)

        last_meal_name = "Sin registros aún"
        last_meal_kcal = 0
        last_meal_tag = "Diario"
        if not nutrition_df.empty:
            tn = nutrition_df[nutrition_df['date'] == today]
            if not tn.empty:
                tn = tn.copy()
                tn['calories'] = pd.to_numeric(tn['calories'], errors='coerce').fillna(0)
                tn = tn.reset_index(drop=True)
                last = tn.iloc[-1].to_dict()
                raw_notes = str(last.get('notes', '')).strip()
                last_meal_name = raw_notes.replace("[IA]", "").strip() if raw_notes else "Comida registrada"
                last_meal_kcal = int(last.get('calories', 0))
                if "desay" in raw_notes.lower():
                    last_meal_tag = "Desayuno"
                elif "alm" in raw_notes.lower():
                    last_meal_tag = "Almuerzo"
                elif "cena" in raw_notes.lower():
                    last_meal_tag = "Cena"
                else:
                    last_meal_tag = "Registro"

        st.markdown('<div class="ht-phone-card">', unsafe_allow_html=True)
        st.markdown('<div class="ht-row"><div class="ht-row-title">📓 DIARIO</div><div class="ht-row-sub"></div></div>', unsafe_allow_html=True)
        ui.diary_item(last_meal_name, last_meal_kcal, last_meal_tag)
        st.markdown("</div>", unsafe_allow_html=True)

        nav_cols = st.columns([1, 1, 0.9, 1, 1])
        with nav_cols[0]:
            if st.button("🍎\nNutrición", key="nav_nut", use_container_width=True):
                st.switch_page("pages/2_Nutricion.py")
        with nav_cols[1]:
            if st.button("🏃\nFitness", key="nav_fit", use_container_width=True):
                st.switch_page("pages/5_Habitos.py")
        with nav_cols[2]:
            if st.button("➕", key="nav_plus", use_container_width=True):
                st.session_state["quick_actions"] = not st.session_state.get("quick_actions", False)
        with nav_cols[3]:
            if st.button("🧠\nCoach", key="nav_coach", use_container_width=True):
                st.session_state["show_details"] = True
                st.rerun()
        with nav_cols[4]:
            if st.button("📈\nProgreso", key="nav_prog", use_container_width=True):
                st.switch_page("pages/1_Progreso_Corporal.py")

        if st.session_state.get("quick_actions", False):
            qa = st.columns(2)
            with qa[0]:
                if st.button("🍽️ Registrar comida", key="qa_food", use_container_width=True):
                    st.switch_page("pages/2_Nutricion.py")
                if st.button("💧 +250ml agua", key="qa_water", use_container_width=True):
                    row = {"date": str(today), "amount_ml": 250, "goal_ml": water_goal}
                    if sheets.add_row(settings.SHEET_WATER_LOG, row):
                        st.rerun()
            with qa[1]:
                if st.button("✅ Checklist hábitos", key="qa_habits", use_container_width=True):
                    st.switch_page("pages/5_Habitos.py")
                if st.button("⚖️ Registrar peso", key="qa_weight", use_container_width=True):
                    st.switch_page("pages/1_Progreso_Corporal.py")

        ui.phone_shell_end()

    expanded_details = bool(st.session_state.get("show_details", False))
    with st.expander("Detalles avanzados (fase, riesgo, proyección, histórico)", expanded=expanded_details):
        ui.section_title("Coach")
        if risk_flags:
            st.error(ai_message)
        else:
            st.info(ai_message)
        ui.section_title("Fase")
        ui.pill(f"{phase_name}", "blue")
        st.write(phase_desc)
        ui.section_title("Adherencia semanal")
        st.progress(min(max(adherence_score / 100, 0.0), 1.0))
        st.write(f"{int(adherence_score)}% · {adherence_level}")
        ui.section_title("Proyección")
        st.write(f"Déficit real promedio (7d): {int(max(real_deficit, 0))} kcal/día")
        st.write(f"Ritmo: {weekly_loss} kg/semana")
        if target_date:
            st.write(f"Fecha estimada: {target_date}")
        else:
            st.write("Fecha estimada: datos insuficientes")

if __name__ == "__main__":
    main()
