import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import streamlit as st
from datetime import datetime
from app.services import google_sheets_service as sheets
from app.services import vision_service
from app.config import settings
from app.components import charts
import pandas as pd

st.set_page_config(page_title="Nutrición IA", page_icon="🍎")

st.title("🍎 Nutrición Inteligente")

tab1, tab2 = st.tabs(["📸 Escáner IA", "📝 Manual"])

with tab1:
    st.header("Escanear Alimento")
    st.info("Sube una foto o usa la cámara para detectar alimentos automáticamente.")
    
    img_file = st.file_uploader("Subir imagen", type=['jpg', 'png', 'jpeg'])
    camera_file = st.camera_input("Tomar foto")
    
    file_to_process = img_file if img_file else camera_file
    
    if file_to_process:
        # Show spinner while processing
        with st.spinner("Analizando imagen con IA..."):
            detected_items, annotated_img = vision_service.detect_food(file_to_process)
            
        if annotated_img is not None:
            st.image(annotated_img, caption="Detección IA", use_container_width=True)
        
        if detected_items:
            st.success(f"Se detectaron {len(detected_items)} alimentos.")
            
            with st.form("ai_log_form"):
                total_cal = 0
                total_pro = 0
                total_carb = 0
                total_fat = 0
                
                final_items = []
                
                for i, item in enumerate(detected_items):
                    st.subheader(f"🍽️ {item['name'].title()}")
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        grams = st.number_input(
                            f"Gramos ({item['name']})", 
                            value=item['estimated_grams'], 
                            key=f"g_{i}"
                        )
                    
                    # Recalculate based on grams
                    ratio = grams / 100.0
                    cal = item['info']['calories'] * ratio
                    pro = item['info']['protein'] * ratio
                    carb = item['info']['carbs'] * ratio
                    fat = item['info']['fats'] * ratio
                    
                    with col2:
                        st.caption(f"Aprox: {int(cal)} kcal | P: {pro:.1f}g | C: {carb:.1f}g | G: {fat:.1f}g")
                    
                    total_cal += cal
                    total_pro += pro
                    total_carb += carb
                    total_fat += fat
                    
                    final_items.append(f"{item['name']} ({grams}g)")

                st.divider()
                st.metric("Total Calculado", f"{int(total_cal)} kcal")
                
                notes = st.text_input("Notas adicionales", value=", ".join(final_items))
                
                if st.form_submit_button("Guardar Todo"):
                    row = {
                        "date": str(datetime.now().date()),
                        "calories": int(total_cal),
                        "protein": round(total_pro, 1),
                        "carbs": round(total_carb, 1),
                        "fats": round(total_fat, 1),
                        "notes": f"[IA] {notes}"
                    }
                    if sheets.add_row(settings.SHEET_NUTRITION_LOG, row):
                        st.success("¡Registrado con éxito!")
                        st.balloons()
        elif annotated_img is not None:
            st.warning("No se detectaron alimentos conocidos en la imagen. Intenta registrarlo manualmente.")

with tab2:
    st.header("Registro Manual")
    with st.form("nutrition_form"):
        date = st.date_input("Fecha", datetime.now())
        calories = st.number_input("Calorías (kcal)", min_value=0, step=10)
        protein = st.number_input("Proteína (g)", min_value=0.0, step=0.1)
        carbs = st.number_input("Carbohidratos (g)", min_value=0.0, step=0.1)
        fats = st.number_input("Grasas (g)", min_value=0.0, step=0.1)
        notes = st.text_input("Notas (Ej: Almuerzo)")
        
        submitted = st.form_submit_button("Agregar Registro")
        
        if submitted:
            row = {
                "date": str(date),
                "calories": calories,
                "protein": protein,
                "carbs": carbs,
                "fats": fats,
                "notes": notes
            }
            if sheets.add_row(settings.SHEET_NUTRITION_LOG, row):
                st.success("Comida registrada!")
            else:
                st.error("Error al registrar.")

st.divider()
    
# Daily Summary (Common for both)
st.subheader("Resumen de Hoy")
df = sheets.load_data(settings.SHEET_NUTRITION_LOG)
if not df.empty:
    today = datetime.now().date()
    today_df = df[df['date'] == today]
    
    if not today_df.empty:
        total_cal = today_df['calories'].sum()
        total_pro = today_df['protein'].sum()
        total_carb = today_df['carbs'].sum()
        total_fat = today_df['fats'].sum()
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Calorías", total_cal, f"{settings.DEFAULT_CALORIE_GOAL - total_cal} left")
        c2.metric("Proteína", f"{total_pro}g")
        c3.metric("Carbs", f"{total_carb}g")
        c4.metric("Grasas", f"{total_fat}g")
        
        # Motivation logic check
        if total_cal > settings.DEFAULT_CALORIE_GOAL:
            st.warning("⚠️ Has excedido tu meta calórica de hoy. ¡Intenta compensar mañana!")
    else:
        st.info("No hay registros para hoy. ¡Sube una foto de tu desayuno!")

    # Calories Trend
    fig_cal = charts.plot_calories_vs_goal(df, settings.DEFAULT_CALORIE_GOAL)
    if fig_cal:
        st.plotly_chart(fig_cal, use_container_width=True)
        
    # Average Macros
    avg_pro = df['protein'].mean()
    avg_carb = df['carbs'].mean()
    avg_fat = df['fats'].mean()
    
    st.subheader("Distribución Promedio de Macros")
    fig_pie = charts.plot_macronutrients(avg_pro, avg_carb, avg_fat)
    if fig_pie:
        st.plotly_chart(fig_pie, use_container_width=True)
        
    st.dataframe(df.sort_values(by="date", ascending=False))
