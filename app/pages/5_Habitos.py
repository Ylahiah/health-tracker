import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import streamlit as st
from datetime import datetime
from app.services import google_sheets_service as sheets
from app.config import settings

st.set_page_config(page_title="Hábitos", page_icon="✅")

st.title("✅ Sistema de Hábitos")

# Define default habits (could be moved to settings or sheet)
DEFAULT_HABITS = [
    "Dormir 7+ horas",
    "Leer 10 páginas",
    "Sin azúcar añadido",
    "Caminar 30 min",
    "Meditación 5 min"
]

date = st.date_input("Fecha", datetime.now())

st.subheader(f"Checklist para {date}")

with st.form("habits_form"):
    status_dict = {}
    for habit in DEFAULT_HABITS:
        status_dict[habit] = st.checkbox(habit)
        
    notes = st.text_area("Notas del día")
    
    submitted = st.form_submit_button("Guardar Hábitos")
    
    if submitted:
        # We save each habit as a row or aggregate?
        # The schema suggests "habit_name", "status", "notes"
        # Let's save one row per habit per day
        
        success = True
        for habit, status in status_dict.items():
            row = {
                "date": str(date),
                "habit_name": habit,
                "status": "Completado" if status else "Pendiente",
                "notes": notes if habit == DEFAULT_HABITS[0] else "" # Attach notes to first habit to avoid duplication or logic
            }
            if not sheets.add_row(settings.SHEET_HABITS_LOG, row):
                success = False
        
        if success:
            st.success("Hábitos guardados!")
            st.balloons()
        else:
            st.error("Error al guardar algunos hábitos.")

st.divider()

st.header("Rachas y Cumplimiento")
df = sheets.load_data(settings.SHEET_HABITS_LOG)

if not df.empty:
    # Calculate completion rate
    total_checks = len(df)
    completed_checks = len(df[df['status'] == "Completado"])
    rate = (completed_checks / total_checks) * 100 if total_checks > 0 else 0
    
    st.metric("Tasa de Cumplimiento Global", f"{rate:.1f}%")
    
    # Show history table
    st.dataframe(df.sort_values(by="date", ascending=False))
