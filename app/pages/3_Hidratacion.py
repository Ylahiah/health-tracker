import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import streamlit as st
from datetime import datetime
from app.services import google_sheets_service as sheets
from app.config import settings

st.set_page_config(page_title="Hidratación", page_icon="💧")

st.title("💧 Hidratación")

today = datetime.now().date()
df = sheets.load_data(settings.SHEET_WATER_LOG)

current_water = 0
if not df.empty:
    today_df = df[df['date'] == today]
    current_water = today_df['amount_ml'].sum()

goal = settings.DEFAULT_WATER_GOAL
progress = min(current_water / goal, 1.0)

st.metric("Total Hoy", f"{current_water} ml", f"Meta: {goal} ml")
st.progress(progress)

if current_water >= goal:
    st.balloons()
    st.success("¡Meta diaria alcanzada! 🎉")

st.subheader("Registrar Agua")
c1, c2, c3, c4 = st.columns(4)

def log_water(amount):
    row = {
        "date": str(today),
        "amount_ml": amount,
        "goal_ml": goal
    }
    if sheets.add_row(settings.SHEET_WATER_LOG, row):
        st.toast(f"Añadido {amount}ml")
        st.rerun()

with c1:
    if st.button("+ 250 ml"):
        log_water(250)
with c2:
    if st.button("+ 500 ml"):
        log_water(500)
with c3:
    if st.button("+ 1 Litro"):
        log_water(1000)

with st.expander("Registro Manual"):
    with st.form("water_form"):
        custom_amount = st.number_input("Cantidad (ml)", min_value=0, step=50)
        submitted = st.form_submit_button("Registrar")
        if submitted:
            log_water(custom_amount)

st.divider()
st.subheader("Historial Reciente")
if not df.empty:
    st.dataframe(df.sort_values(by="date", ascending=False).head(10))
