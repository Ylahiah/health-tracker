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

    try:
        # Using the standard gemini-pro model which often works better for new free-tier accounts
        # Note: 'gemini-pro' also supports images in some regions, but let's try 'gemini-1.5-flash' again without 'latest'
        # If this fails, we will need to list models.
        model = genai.GenerativeModel('gemini-1.5-flash')
        
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
        st.error(f"Error analizando con Gemini: {str(e)}")
        return [], image
