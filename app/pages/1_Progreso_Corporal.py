import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import streamlit as st
from datetime import datetime
from app.services import google_sheets_service as sheets
from app.services import analytics_service as analytics
from app.config import settings
from app.components import charts

st.set_page_config(page_title="Progreso Corporal", page_icon="⚖️")

st.title("⚖️ Progreso Corporal")

tab1, tab2 = st.tabs(["Registrar", "Histórico"])

with tab1:
    st.header("Nuevo Registro")
    with st.form("body_metrics_form"):
        date = st.date_input("Fecha", datetime.now())
        weight = st.number_input("Peso (kg)", min_value=0.0, step=0.1, format="%.1f")
        body_fat = st.number_input("% Grasa Corporal (Opcional)", min_value=0.0, step=0.1, format="%.1f")
        
        st.subheader("Medidas (cm)")
        c1, c2 = st.columns(2)
        with c1:
            waist = st.number_input("Cintura", min_value=0.0, step=0.1)
            hip = st.number_input("Cadera", min_value=0.0, step=0.1)
        with c2:
            chest = st.number_input("Pecho", min_value=0.0, step=0.1)
            thighs = st.number_input("Muslos", min_value=0.0, step=0.1)
            
        notes = st.text_area("Notas")
        
        submitted = st.form_submit_button("Guardar Registro")
        
        if submitted:
            row = {
                "date": str(date),
                "weight": weight,
                "body_fat_percentage": body_fat,
                "waist": waist,
                "hip": hip,
                "chest": chest,
                "arms": 0, # Placeholder if not used
                "thighs": thighs,
                "notes": notes
            }
            if sheets.add_row(settings.SHEET_BODY_METRICS, row):
                st.success("Registro guardado exitosamente!")
            else:
                st.error("Error al guardar el registro.")

with tab2:
    st.header("Historial y Análisis")
    df = sheets.load_data(settings.SHEET_BODY_METRICS)
    
    if not df.empty:
        # Metrics
        latest = df.iloc[-1]
        bmi = analytics.calculate_bmi(latest['weight'], 175) # TODO: Get height from user profile
        st.metric("IMC Actual", bmi)
        
        # Chart
        fig = charts.plot_weight_history(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            
        st.dataframe(df.sort_values(by="date", ascending=False), use_container_width=True)
    else:
        st.info("No hay registros aún.")
