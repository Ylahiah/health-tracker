import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from app.services import google_sheets_service as sheets
from app.services import profile_service
from app.config import settings

st.set_page_config(page_title="Configuración", page_icon="⚙️")

# Ensure sheets are initialized
if 'sheets_initialized' not in st.session_state:
    try:
        sheets.init_sheets()
        st.session_state['sheets_initialized'] = True
    except Exception as e:
        st.error(f"Error conectando a la base de datos: {e}")

st.title("⚙️ Configuración y Perfil")

# --- User Profile Section ---
st.header("👤 Perfil de Usuario")

# Load existing profile
current_profile = profile_service.get_user_profile()

with st.form("profile_form"):
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Nombre", value=current_profile['name'])
        age = st.number_input("Edad", value=current_profile['age'], min_value=10, max_value=100)
        gender = st.selectbox("Género", options=['M', 'F'], index=0 if current_profile['gender']=='M' else 1)
        height = st.number_input("Altura (cm)", value=current_profile['height'])
    
    with c2:
        current_weight = st.number_input("Peso Actual (kg)", value=current_profile['current_weight'])
        goal_weight = st.number_input("Peso Meta (kg)", value=current_profile['goal_weight'])
        activity_level = st.selectbox("Nivel de Actividad", 
                                      options=[1.2, 1.375, 1.55, 1.725, 1.9],
                                      format_func=lambda x: {
                                          1.2: "Sedentario (poco o nada ejercicio)",
                                          1.375: "Ligero (ejercicio 1-3 días/sem)",
                                          1.55: "Moderado (ejercicio 3-5 días/sem)",
                                          1.725: "Activo (ejercicio 6-7 días/sem)",
                                          1.9: "Muy Activo (trabajo físico/entreno duro)"
                                      }.get(x))
        calorie_deficit = st.slider("Déficit Calórico Diario (kcal)", 200, 1000, current_profile['calorie_deficit'])

    submitted = st.form_submit_button("Guardar Perfil y Calcular Metas")
    
    if submitted:
        new_profile = {
            'name': name,
            'age': age,
            'gender': gender,
            'height': height,
            'current_weight': current_weight,
            'goal_weight': goal_weight,
            'activity_level': activity_level,
            'calorie_deficit': calorie_deficit
        }
        
        # Calculate new targets
        daily_cal, tdee = profile_service.calculate_daily_targets(new_profile)
        new_profile['daily_calories'] = daily_cal
        new_profile['tdee'] = tdee
        
        # Save to sheets
        try:
            if profile_service.save_user_profile(new_profile):
                st.success("¡Perfil guardado en la nube y actualizado!")
                # Force rerun to update session state everywhere
                st.rerun()
            else:
                st.error("Error al guardar en la nube, revisa la conexión.")
        except Exception as e:
            st.error(f"Error crítico al guardar: {e}")
        
        # Show projections
        weekly_loss, weeks = profile_service.project_weight_loss(new_profile)
        st.info(f"🎯 Meta Diaria: **{daily_cal} kcal** (Mantenimiento: {tdee} kcal)")
        st.success(f"📉 Proyección: Bajarás **{weekly_loss} kg/semana**. Llegarás a tu meta en aprox **{weeks} semanas**.")

# Show current goals if set
if 'user_profile' in st.session_state:
    prof = st.session_state['user_profile']
    st.divider()
    st.subheader(f"Tablero de Control: {prof['name']}")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Meta Diaria", f"{prof.get('daily_calories', settings.DEFAULT_CALORIE_GOAL)} kcal")
    col2.metric("Déficit", f"-{prof['calorie_deficit']} kcal")
    col3.metric("Peso a Perder", f"{round(prof['current_weight'] - prof['goal_weight'], 1)} kg")

st.divider()
st.header("🛠️ Configuración Técnica")
st.caption("Ajustes del sistema y base de datos.")

tab1, tab2 = st.tabs(["Base de Datos", "Logs"])

with tab1:
    # Use st.secrets if available, otherwise fallback to generic message
    sheet_name = st.secrets.get("spreadsheet", {}).get("name", "No Configurado")
    st.write(f"Hoja de Cálculo Conectada: `{sheet_name}`")
    if st.button("Probar Conexión (Reiniciar Sheets)"):
        try:
            sheets.init_sheets()
            st.success("Conexión exitosa con Google Sheets")
            st.balloons()
        except Exception as e:
            st.error(f"Error: {e}")

with tab2:
    st.info("Logs del sistema (Próximamente)")
