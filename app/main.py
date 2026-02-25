import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
import pandas as pd
from datetime import datetime
from app.services import google_sheets_service as sheets
from app.services import analytics_service as analytics
from app.config import settings

st.set_page_config(
    page_title="Health Tracker",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("💪 Dashboard Principal")
    
    # Initialize sheets if needed (lazy init)
    if 'sheets_initialized' not in st.session_state:
        sheets.init_sheets()
        st.session_state['sheets_initialized'] = True

    today = datetime.now().date()
    
    # --- Load Data ---
    body_df = sheets.load_data(settings.SHEET_BODY_METRICS)
    nutrition_df = sheets.load_data(settings.SHEET_NUTRITION_LOG)
    water_df = sheets.load_data(settings.SHEET_WATER_LOG)
    meds_df = sheets.load_data(settings.SHEET_MEDICATION_LOG)
    
    # --- Calculate Daily Metrics ---
    
    # Nutrition
    today_calories = 0
    if not nutrition_df.empty:
        today_nutrition = nutrition_df[nutrition_df['date'] == today]
        today_calories = today_nutrition['calories'].sum()
        
    # Water
    today_water = 0
    if not water_df.empty:
        today_water_log = water_df[water_df['date'] == today]
        today_water = today_water_log['amount_ml'].sum()

    # Weight
    current_weight = 0
    weight_delta = 0
    if not body_df.empty:
        body_df = body_df.sort_values(by="date", ascending=False)
        current_weight = body_df.iloc[0]['weight']
        if len(body_df) > 1:
            prev_weight = body_df.iloc[1]['weight']
            weight_delta = round(current_weight - prev_weight, 2)

    # Meds
    meds_taken = False
    if not meds_df.empty:
        today_meds = meds_df[meds_df['date'] == today]
        if not today_meds.empty:
            meds_taken = True
            
    # Phase
    start_date = st.session_state.get("start_date", "2023-01-01") # TODO: Get from goals
    phase_name, week_num = analytics.calculate_phase(start_date)

    # Motivation
    motivation_msg = analytics.get_motivation_message(nutrition_df, body_df, settings.DEFAULT_CALORIE_GOAL)
    
    # --- Motivation Banner ---
    st.info(motivation_msg)

    # --- Display Metrics ---
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Peso Actual", f"{current_weight} kg", f"{weight_delta} kg")
        st.caption(f"{phase_name} (Semana {week_num})")
        
    with col2:
        st.metric("Calorías Hoy", f"{today_calories}", f"{settings.DEFAULT_CALORIE_GOAL - today_calories} left")
        
    with col3:
        st.metric("Agua Hoy", f"{today_water} ml", f"{settings.DEFAULT_WATER_GOAL - today_water} left")
        
    with col4:
        st.metric("Medicación", "✅ Tomada" if meds_taken else "⚠️ Pendiente")

    st.markdown("---")
    
    # --- Quick Actions ---
    st.subheader("Acciones Rápidas")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        if st.button("💧 +250ml Agua"):
            row = {
                "date": str(today),
                "amount_ml": 250,
                "goal_ml": settings.DEFAULT_WATER_GOAL
            }
            if sheets.add_row(settings.SHEET_WATER_LOG, row):
                st.toast("Agua registrada!")
                st.rerun()

    with c2:
        if st.button("💊 Registrar Meds"):
            st.switch_page("pages/4_Tratamiento.py")
            
    with c3:
        if st.button("🍎 Registrar Comida"):
            st.switch_page("pages/2_Nutricion.py")

if __name__ == "__main__":
    main()
