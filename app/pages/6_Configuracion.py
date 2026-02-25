import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import streamlit as st
from app.services import google_sheets_service as sheets
from app.config import settings

st.set_page_config(page_title="Configuración", page_icon="⚙️")

st.title("⚙️ Configuración")

st.header("Metas Personales")
st.caption("Estas metas se usan para calcular tus progresos diarios.")

# TODO: Load these from a 'goals' sheet if implemented fully, 
# for now we use session state or defaults, but let's simulate saving to the goals sheet.

with st.form("goals_form"):
    weight_goal = st.number_input("Meta de Peso (kg)", min_value=40.0, max_value=200.0, value=70.0)
    calorie_goal = st.number_input("Meta de Calorías Diarias", min_value=1200, max_value=4000, value=settings.DEFAULT_CALORIE_GOAL)
    water_goal = st.number_input("Meta de Agua (ml)", min_value=1000, max_value=5000, value=settings.DEFAULT_WATER_GOAL)
    
    submitted = st.form_submit_button("Actualizar Metas")
    
    if submitted:
        # Save to Goals Sheet
        # Schema: category, metric, target_value, start_date, target_date, status
        
        # Weight Goal
        sheets.add_row(settings.SHEET_GOALS, {
            "category": "Body",
            "metric": "Weight",
            "target_value": weight_goal,
            "start_date": str(st.session_state.get("start_date", "2023-01-01")),
            "target_date": "",
            "status": "Active"
        })
        
        # Calorie Goal
        sheets.add_row(settings.SHEET_GOALS, {
            "category": "Nutrition",
            "metric": "Calories",
            "target_value": calorie_goal,
            "start_date": str(st.session_state.get("start_date", "2023-01-01")),
            "target_date": "",
            "status": "Active"
        })
        
        st.success("Metas actualizadas (Guardadas en historial de metas)")

st.divider()

st.header("Gestión de Datos")
if st.button("Limpiar Caché"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.success("Caché limpiada!")

with st.expander("Ver Datos Crudos"):
    sheet_option = st.selectbox("Seleccionar Hoja", settings.ALL_SHEETS)
    if st.button("Cargar Datos"):
        df = sheets.load_data(sheet_option)
        st.dataframe(df)
