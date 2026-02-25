import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import streamlit as st
from datetime import datetime
from app.services import google_sheets_service as sheets
from app.services import gemini_service
from app.config import settings
from app.components import charts
import pandas as pd
from PIL import Image

st.set_page_config(page_title="Nutrición IA", page_icon="🍎")

# Ensure sheets are initialized
if 'sheets_initialized' not in st.session_state:
    try:
        sheets.init_sheets()
        st.session_state['sheets_initialized'] = True
    except Exception as e:
        st.error(f"Error conectando a la base de datos: {e}")

st.title("🍎 Nutrición Inteligente (Gemini AI)")

tab1, tab2 = st.tabs(["📸 Escáner Avanzado", "📝 Manual"])

with tab1:
    st.header("Analizar Plato Completo")
    st.info("Usa la potencia de Google Gemini para detectar ingredientes complejos (carne, quesos, guisos).")
    
    # Check for API Key
    if not st.secrets.get("GOOGLE_API_KEY"):
        st.warning("⚠️ Necesitas configurar tu GOOGLE_API_KEY en los secretos para usar esta función.")
        st.markdown("[Obtener API Key Gratis](https://aistudio.google.com/app/apikey)")
    
    img_file = st.file_uploader("Subir foto de comida", type=['jpg', 'png', 'jpeg'])
    camera_file = st.camera_input("O tomar foto ahora")
    
    file_to_process = img_file if img_file else camera_file
    
    if file_to_process:
        image = Image.open(file_to_process)
        st.image(image, caption="Tu Foto", use_container_width=True)
        
        # User context input
        user_context = st.text_input("Contexto adicional (opcional)", placeholder="Ej: Es frito, cocinado con aceite de oliva, sin piel...")
        
        if st.button("✨ Analizar Calorías con IA"):
            with st.spinner("La IA está analizando tu plato..."):
                detected_items, _ = gemini_service.analyze_image_with_gemini(image, user_context)
                
            if detected_items:
                st.success(f"¡He encontrado {len(detected_items)} ingredientes!")
                st.session_state['detected_items'] = detected_items # Persist for form interaction
            else:
                st.error("No pude identificar comida en la imagen. Intenta con otra foto.")

        # If items are in session state (from this run or previous), show the form
        if 'detected_items' in st.session_state:
            detected_items = st.session_state['detected_items']
            
            with st.form("gemini_log_form"):
                total_cal = 0
                total_pro = 0
                total_carb = 0
                total_fat = 0
                
                final_items = []
                
                for i, item in enumerate(detected_items):
                    st.subheader(f"🍽️ {item['name']}")
                    
                    c1, c2, c3 = st.columns([1, 1, 2])
                    
                    with c1:
                        grams = st.number_input(f"Gramos", value=item['estimated_grams'], key=f"g_{i}")
                    
                    # Recalculate based on grams change
                    original_grams = item['estimated_grams'] if item['estimated_grams'] > 0 else 1
                    ratio = grams / original_grams
                    
                    cal = item['calories'] * ratio
                    pro = item['protein'] * ratio
                    carb = item['carbs'] * ratio
                    fat = item['fats'] * ratio
                    
                    with c2:
                        st.metric("Calorías", f"{int(cal)}")
                    
                    with c3:
                        st.caption(f"P: {pro:.1f}g | C: {carb:.1f}g | G: {fat:.1f}g")
                    
                    total_cal += cal
                    total_pro += pro
                    total_carb += carb
                    total_fat += fat
                    final_items.append(f"{item['name']} ({grams}g)")
                
                st.divider()
                st.metric("TOTAL PLATO", f"{int(total_cal)} kcal", f"P:{int(total_pro)} C:{int(total_carb)} F:{int(total_fat)}")
                
                notes = st.text_input("Notas", value=", ".join(final_items))
                
                if st.form_submit_button("Guardar en mi Diario"):
                    row = {
                        "date": str(datetime.now().date()),
                        "calories": int(total_cal),
                        "protein": round(total_pro, 1),
                        "carbs": round(total_carb, 1),
                        "fats": round(total_fat, 1),
                        "notes": f"[IA] {notes}"
                    }
                    if sheets.add_row(settings.SHEET_NUTRITION_LOG, row):
                        st.success("¡Guardado en Google Sheets correctamente!")
                        st.balloons()
                        # Clear session state to reset
                        del st.session_state['detected_items']
                        st.rerun()
                    else:
                        st.error("Hubo un problema al guardar en Google Sheets. Revisa la configuración.")

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
                st.success("¡Comida registrada en la base de datos!")
            else:
                st.error("Error al registrar en Google Sheets.")

st.divider()
    
# Daily Summary
st.subheader("Resumen de Hoy")
df = sheets.load_data(settings.SHEET_NUTRITION_LOG)
if not df.empty:
    today = datetime.now().date()
    # Safe date conversion
    df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date
    today_df = df[df['date'] == today]
    
    if not today_df.empty:
        total_cal = today_df['calories'].sum()
        total_pro = today_df['protein'].sum()
        total_carb = today_df['carbs'].sum()
        total_fat = today_df['fats'].sum()
        
        # Get goals from session or settings
        cal_goal = st.session_state.get('user_profile', {}).get('daily_calories', settings.DEFAULT_CALORIE_GOAL)
        
        c1, c2, c3, c4 = st.columns(4)
        remaining = cal_goal - total_cal
        c1.metric("Calorías", total_cal, f"{remaining} restantes", delta_color="normal" if remaining > 0 else "inverse")
        c2.metric("Proteína", f"{int(total_pro)}g")
        c3.metric("Carbs", f"{int(total_carb)}g")
        c4.metric("Grasas", f"{int(total_fat)}g")
        
        if total_cal > cal_goal:
            st.warning(f"⚠️ Has excedido tu meta de {cal_goal} kcal.")
            
        # Daily History Chart
        st.subheader("Historial Diario")
        daily_summary = df.groupby('date')['calories'].sum().reset_index()
        fig = charts.plot_calories_trend(daily_summary, cal_goal)
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("No hay registros para hoy.")
