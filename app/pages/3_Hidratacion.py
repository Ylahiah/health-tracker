import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import streamlit as st
import pandas as pd
from datetime import datetime
from app.services import google_sheets_service as sheets
from app.config import settings
from app.utils import time_utils
from app.components import ui

st.set_page_config(page_title="Hidratación", page_icon="💧")

ui.inject_global_style()
ui.title("Hidratación", "Control diario y por historial")

today = time_utils.local_today()

# Load data
df = sheets.load_data(settings.SHEET_WATER_LOG)

current_water = 0
goal = settings.DEFAULT_WATER_GOAL

if not df.empty:
    # Ensure date column is datetime object for accurate comparison
    # Coerce errors to NaT to handle potential bad data, then drop them or ignore
    df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date
    
    # Filter for today's records
    today_df = df[df['date'] == today]
    
    if not today_df.empty:
        # Sum the amount_ml column
        # Ensure amount_ml is numeric
        today_df['amount_ml'] = pd.to_numeric(today_df['amount_ml'], errors='coerce').fillna(0)
        current_water = today_df['amount_ml'].sum()

# Calculate progress
# Avoid division by zero
if goal <= 0: goal = 2500
progress_value = min(current_water / goal, 1.0)

# Display Metrics
ui.card_start(soft=True)
ui.kpi_grid(
    [
        {"label": "Total hoy", "value": f"{int(current_water)} ml", "sub": f"Meta {goal} ml"},
        {"label": "Restante", "value": f"{max(int(goal - current_water), 0)} ml", "sub": "Para cumplir la meta"},
        {"label": "Progreso", "value": f"{int(progress_value*100)}%", "sub": "Del objetivo diario"},
        {"label": "Meta", "value": f"{goal} ml", "sub": "Objetivo del día"},
    ]
)
st.progress(progress_value)
ui.card_end()

if current_water >= goal:
    st.balloons()
    st.success("¡Meta diaria alcanzada! 🎉")

with st.expander("📅 Ver resumen por día"):
    view_date = st.date_input("Día", today, key="water_view_day")
    view_total = 0
    if not df.empty:
        view_df = df[df['date'] == view_date]
        if not view_df.empty:
            view_df['amount_ml'] = pd.to_numeric(view_df['amount_ml'], errors='coerce').fillna(0)
            view_total = view_df['amount_ml'].sum()
    ui.kpi_grid(
        [
            {"label": "Total del día", "value": f"{int(view_total)} ml", "sub": f"Meta {goal} ml"},
            {"label": "Restante", "value": f"{max(int(goal - view_total), 0)} ml", "sub": "Para cumplir la meta"},
        ]
    )

st.divider()

st.subheader("Registrar Agua")

def log_water(amount):
    row = {
        "date": str(today),
        "amount_ml": amount,
        "goal_ml": goal
    }
    if sheets.add_row(settings.SHEET_WATER_LOG, row):
        st.toast(f"Añadido {amount}ml")
        st.rerun()

c1, c2, c3 = st.columns(3)

with c1:
    if st.button("💧 + 250 ml", use_container_width=True):
        log_water(250)
with c2:
    if st.button("🥤 + 500 ml", use_container_width=True):
        log_water(500)
with c3:
    if st.button("🧴 + 1 Litro", use_container_width=True):
        log_water(1000)

with st.expander("📝 Registro Manual"):
    with st.form("water_form"):
        custom_amount = st.number_input("Cantidad Personalizada (ml)", min_value=0, step=50)
        submitted = st.form_submit_button("Registrar")
        if submitted:
            log_water(custom_amount)

st.divider()
st.subheader("Historial Reciente")
if not df.empty:
    # Show history sorted by date descending
    st.dataframe(df.sort_values(by="date", ascending=False).head(10), use_container_width=True)
else:
    st.info("No hay registros de agua aún.")
