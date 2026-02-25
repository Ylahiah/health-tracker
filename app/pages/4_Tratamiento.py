import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.express as px
from app.services import google_sheets_service as sheets
from app.config import settings

st.set_page_config(page_title="Tratamiento", page_icon="💊")

st.title("💊 Control de Tratamiento (Fentermina)")

tab1, tab2 = st.tabs(["Registro Diario", "Monitoreo"])

with tab1:
    st.header("Registro Diario")
    with st.form("meds_form"):
        date = st.date_input("Fecha", datetime.now())
        dose = st.number_input("Dosis (mg)", min_value=0.0, step=0.5, value=37.5)
        time_taken = st.time_input("Hora de toma", datetime.now().time())
        
        st.subheader("Síntomas y Efectos")
        c1, c2 = st.columns(2)
        with c1:
            appetite = st.slider("Nivel de Apetito (1-10)", 1, 10, 5, help="1=Sin hambre, 10=Mucha hambre")
            energy = st.slider("Nivel de Energía (1-10)", 1, 10, 5)
        with c2:
            sleep = st.slider("Calidad del Sueño (1-5)", 1, 5, 3)
            adherence = st.checkbox("¿Tomó la medicación?", value=True)
            
        st.subheader("Signos Vitales")
        hr = st.number_input("Frecuencia Cardiaca (bpm)", min_value=40, max_value=200, value=70)
        bp = st.text_input("Presión Arterial (Ej: 120/80)")
        
        side_effects = st.text_area("Efectos Secundarios / Notas")
        
        submitted = st.form_submit_button("Guardar Registro")
        
        if submitted:
            row = {
                "date": str(date),
                "dose_mg": dose,
                "time_taken": str(time_taken),
                "appetite_level": appetite,
                "energy_level": energy,
                "heart_rate": hr,
                "blood_pressure": bp,
                "sleep_quality": sleep,
                "side_effects": side_effects,
                "adherence": adherence,
                "notes": ""
            }
            if sheets.add_row(settings.SHEET_MEDICATION_LOG, row):
                st.success("Registro guardado exitosamente!")
            else:
                st.error("Error al guardar el registro.")

with tab2:
    st.header("Monitoreo de Efectos")
    df = sheets.load_data(settings.SHEET_MEDICATION_LOG)
    
    if not df.empty:
        # Appetite vs Time
        fig_app = px.line(df, x="date", y="appetite_level", title="Evolución del Apetito", markers=True)
        st.plotly_chart(fig_app, use_container_width=True)
        
        # Energy vs Time
        fig_en = px.line(df, x="date", y="energy_level", title="Niveles de Energía", markers=True)
        st.plotly_chart(fig_en, use_container_width=True)
        
        # Sleep vs Time
        fig_sleep = px.line(df, x="date", y="sleep_quality", title="Calidad del Sueño", markers=True)
        st.plotly_chart(fig_sleep, use_container_width=True)
        
        # HR Monitor
        st.subheader("Monitoreo Cardiaco")
        avg_hr = df['heart_rate'].mean()
        st.metric("FC Promedio", f"{int(avg_hr)} bpm")
        
        fig_hr = px.line(df, x="date", y="heart_rate", title="Frecuencia Cardiaca", markers=True)
        # Add alert line
        fig_hr.add_hline(y=100, line_dash="dot", annotation_text="Alerta Taquicardia (100 bpm)", annotation_position="bottom right")
        st.plotly_chart(fig_hr, use_container_width=True)
        
        st.dataframe(df.sort_values(by="date", ascending=False))
    else:
        st.info("No hay datos de tratamiento aún.")
