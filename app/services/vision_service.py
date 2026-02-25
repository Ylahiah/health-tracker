import streamlit as st
from PIL import Image
import numpy as np
from app.services import nutrition_db

try:
    from ultralytics import YOLO
    VISION_AVAILABLE = True
    IMPORT_ERROR = None
except Exception as e:
    VISION_AVAILABLE = False
    IMPORT_ERROR = str(e)

@st.cache_resource
def load_model():
    """
    Loads the YOLOv8n model.
    Uses st.cache_resource to load only once.
    """
    if not VISION_AVAILABLE:
        raise ImportError(f"La librería de IA no está disponible: {IMPORT_ERROR}")
        
    # 'yolov8n.pt' will be downloaded automatically if not present
    model = YOLO('yolov8n.pt')
    return model

def detect_food(image_file):
    """
    Runs inference on the uploaded image.
    Returns a list of detected food items with their nutritional info.
    """
    if not VISION_AVAILABLE:
        st.error(f"⚠️ Error de sistema: No se pudo cargar el modelo de IA.\nDetalle: {IMPORT_ERROR}")
        return [], None

    model = load_model()
    
    # Convert uploaded file to Image
    if isinstance(image_file, (str, np.ndarray)):
        img = image_file
    else:
        img = Image.open(image_file)

    # Run inference
    results = model(img)
    
    detected_items = []
    
    # Process results
    for result in results:
        boxes = result.boxes
        for box in boxes:
            # Get class ID and confidence
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            
            # Get class name
            class_name = model.names[cls_id]
            
            # Check if it's a food item in our DB
            food_info = nutrition_db.get_food_info(class_name)
            
            if food_info and conf > 0.3: # Filter by confidence and if it is food
                item = {
                    "name": class_name,
                    "confidence": conf,
                    "info": food_info,
                    "estimated_grams": food_info["default_g"]
                }
                detected_items.append(item)
                
    return detected_items, results[0].plot() # Return items and annotated image
