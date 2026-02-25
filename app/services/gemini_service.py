import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# Try to configure Gemini if key is present
API_KEY = st.secrets.get("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

def analyze_image_with_gemini(image):
    """
    Sends the image to Google Gemini Flash to identify food and estimate nutrition.
    Returns a list of dictionaries with food details.
    """
    if not API_KEY:
        st.error("⚠️ Falta la GOOGLE_API_KEY en los secretos.")
        return [], None

    # Try multiple models in order of preference and stability
    # Using specific models available for this user's API key
    models_to_try = [
        'gemini-2.5-flash',
        'gemini-2.0-flash',
        'gemini-1.5-flash',
        'gemini-1.5-pro'
    ]

    last_error = None

    for model_name in models_to_try:
        try:
            # For some older accounts or regions, we might need to be explicit about the generation config or API version
            # But genai library handles most of it.
            # Let's try to list models first if this loop fails completely, but for now just try the model.
            
            # Use the model name directly
            model = genai.GenerativeModel(model_name)
            
            prompt = """
            You are a professional nutritionist. Analyze this image of food.
            Identify the distinct food items present.
            For each item, estimate the weight in grams and the nutritional content (calories, protein, carbs, fats) based on that weight.
            
            Return ONLY a raw JSON list of objects. Do not use markdown code blocks.
            Format:
            [
                {
                    "name": "Grilled Chicken Breast",
                    "estimated_grams": 150,
                    "calories": 250,
                    "protein": 45,
                    "carbs": 0,
                    "fats": 5
                },
                ...
            ]
            If the image is not food, return an empty list [].
            """
            
            response = model.generate_content([prompt, image])
            
            # Clean response text (remove markdown if present)
            text_response = response.text.strip()
            if text_response.startswith("```json"):
                text_response = text_response[7:]
            if text_response.endswith("```"):
                text_response = text_response[:-3]
                
            return json.loads(text_response), image
            
        except Exception as e:
            last_error = str(e)
            continue # Try next model

    # If all models failed, try to list available models to debug
    try:
        st.error(f"Error analizando con Gemini (se probaron varios modelos). Último error: {last_error}")
        st.warning("Intentando listar modelos disponibles para tu clave API...")
        
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
                
        if available_models:
            st.info(f"Modelos disponibles encontrados: {', '.join(available_models)}")
            # Try the first available vision model
            for m_name in available_models:
                if 'vision' in m_name or 'flash' in m_name or 'pro' in m_name:
                    st.success(f"Intentando con modelo descubierto: {m_name}")
                    model = genai.GenerativeModel(m_name)
                    response = model.generate_content([prompt, image])
                    # Clean response text (remove markdown if present)
                    text_response = response.text.strip()
                    if text_response.startswith("```json"):
                        text_response = text_response[7:]
                    if text_response.endswith("```"):
                        text_response = text_response[:-3]
                    return json.loads(text_response), image
        else:
            st.error("No se encontraron modelos compatibles con 'generateContent' para tu API Key.")
            
    except Exception as e_debug:
        st.error(f"Error al listar modelos: {str(e_debug)}")

    return [], image
