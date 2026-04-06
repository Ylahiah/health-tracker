import google.generativeai as genai
import streamlit as st

@st.cache_data(ttl=3600)
def generate_coach_feedback(phase, adherence_level, weight_change, risk_flags, name):
    """
    Generates a personalized motivational message using Gemini.
    Cached resource to avoid re-generating on every rerun if inputs are same? 
    Streamlit cache usually works on function args.
    """
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        return "Configura tu API Key para recibir feedback inteligente."
        
    genai.configure(api_key=api_key)
    
    # Select model (lightweight is fine for text)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Actúa como un entrenador personal de élite y experto en psicología del comportamiento.
    Tu cliente, {name}, está en un proceso de transformación física.
    
    ESTADO ACTUAL:
    - Fase Fisiológica: {phase}
    - Nivel de Adherencia Semanal: {adherence_level} (Escala: ÉLITE, ALTO, MEDIO, RIESGO)
    - Cambio de Peso Reciente: {weight_change} kg
    - Alertas de Riesgo Detectadas: {', '.join(risk_flags) if risk_flags else 'Ninguna'}
    
    OBJETIVO:
    Genera un mensaje corto (max 2 frases) de feedback.
    
    DIRECTRICES:
    - Si la adherencia es ÉLITE/ALTO: Felicita y refuerza la identidad de ganador.
    - Si es MEDIO: Anima a ajustar tuercas, recuerda el objetivo.
    - Si es RIESGO: Sé empático pero firme. "No te rindas, ajusta hoy".
    - Menciona la fase fisiológica si es relevante para explicar sensaciones (ej. desinflamación = rápido, adaptación = lento).
    - Habla en español, tono motivador y profesional.
    - NO uses saludos genéricos como "Hola". Ve directo al grano.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return "Sigue adelante, cada día cuenta."
