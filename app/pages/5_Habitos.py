import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import streamlit as st
import pandas as pd
from datetime import datetime
from app.services import google_sheets_service as sheets
from app.config import settings

st.set_page_config(page_title="Hábitos Élite", page_icon="🔥")

st.title("🔥 Sistema de Hábitos: MODO ÉLITE")

# Date Selector
selected_date = st.date_input("Fecha", datetime.now())
selected_date_str = str(selected_date)

# Load existing data for this date
existing_data = {}
df = sheets.load_data(settings.SHEET_HABITS_LOG)

if not df.empty:
    # Ensure date column is string for comparison
    df['date'] = df['date'].astype(str)
    day_records = df[df['date'] == selected_date_str]
    
    for index, row in day_records.iterrows():
        habit_name = row['habit_name']
        status = row['status']
        # Map "Completado" to True
        existing_data[habit_name] = (status == "Completado")

st.subheader(f"✅ Checklist Diario: {selected_date}")

# Calculate current score based on existing data
current_score = sum(1 for h in settings.ELITE_HABITS if existing_data.get(h, False))

def get_score_message(score):
    if score == 5:
        return "🔥 5/5 Día Perfecto"
    elif score == 4:
        return "✅ 4/5 Día Efectivo (Pérdida de grasa)"
    elif score == 3:
        return "⚠️ 3/5 Aún Funcional"
    else:
        return f"❌ {score}/5 Día a Corregir (Ajustar sin culpa)"

st.info(f"Puntuación Actual: **{get_score_message(current_score)}**")

with st.form("habits_form"):
    st.markdown("### 🎯 Tu día es GANADO si cumples 4 de 5")
    
    status_dict = {}
    for habit in settings.ELITE_HABITS:
        # Pre-fill with existing status if available, else False
        default_val = existing_data.get(habit, False)
        status_dict[habit] = st.checkbox(habit, value=default_val)
        
    notes_val = ""
    # Try to find existing notes (usually attached to first habit or any)
    if not df.empty:
        day_records = df[df['date'] == selected_date_str]
        if not day_records.empty:
            # Get first non-empty note
            possible_notes = day_records[day_records['notes'] != ""]['notes'].values
            if len(possible_notes) > 0:
                notes_val = possible_notes[0]

    notes = st.text_area("Notas del día", value=notes_val)
    
    submitted = st.form_submit_button("Guardar Puntuación")
    
    if submitted:
        success_count = 0
        for habit, status in status_dict.items():
            row = {
                "date": selected_date_str,
                "habit_name": habit,
                "status": "Completado" if status else "Pendiente",
                "notes": notes if habit == settings.ELITE_HABITS[0] else "" 
            }
            if sheets.add_row(settings.SHEET_HABITS_LOG, row):
                success_count += 1
        
        if success_count == len(settings.ELITE_HABITS):
            st.success("¡Progreso registrado!")
            st.rerun()
        else:
            st.warning(f"Se guardaron {success_count} de {len(settings.ELITE_HABITS)} hábitos.")

st.divider()

st.header("📊 Historial de Puntuación")

if not df.empty:
    # Process data to show daily scores
    # Group by date
    df['status_bool'] = df['status'].apply(lambda x: 1 if x == "Completado" else 0)
    
    # Filter only Elite habits if mixed with old ones
    df_elite = df[df['habit_name'].isin(settings.ELITE_HABITS)]
    
    if not df_elite.empty:
        # Sort by date (implicit row order usually chronological in sheets)
        # Drop duplicates keeping last
        df_dedup = df_elite.drop_duplicates(subset=['date', 'habit_name'], keep='last')
        
        daily_scores = df_dedup.groupby('date')['status_bool'].sum().reset_index()
        daily_scores.columns = ['Fecha', 'Puntuación']
        
        st.dataframe(daily_scores.sort_values(by="Fecha", ascending=False), use_container_width=True)
        
        # Chart
        st.bar_chart(daily_scores.set_index('Fecha'))
    else:
        st.info("Aún no hay registros con el nuevo sistema Élite.")
