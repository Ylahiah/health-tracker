# Simple local database for demonstration
# In a real app, this could be a larger database or API

FOOD_DB = {
    # COCO Class Names (YOLOv8n standard classes)
    "apple": {"calories": 52, "protein": 0.3, "carbs": 14, "fats": 0.2, "default_g": 150},
    "banana": {"calories": 89, "protein": 1.1, "carbs": 22.8, "fats": 0.3, "default_g": 120},
    "orange": {"calories": 47, "protein": 0.9, "carbs": 11.8, "fats": 0.1, "default_g": 130},
    "broccoli": {"calories": 34, "protein": 2.8, "carbs": 6.6, "fats": 0.4, "default_g": 100},
    "carrot": {"calories": 41, "protein": 0.9, "carbs": 9.6, "fats": 0.2, "default_g": 60},
    "hot dog": {"calories": 290, "protein": 10, "carbs": 25, "fats": 15, "default_g": 100},
    "pizza": {"calories": 266, "protein": 11, "carbs": 33, "fats": 10, "default_g": 100},
    "donut": {"calories": 452, "protein": 4.9, "carbs": 51, "fats": 25, "default_g": 60},
    "cake": {"calories": 371, "protein": 5.5, "carbs": 53, "fats": 15, "default_g": 100},
    "sandwich": {"calories": 250, "protein": 12, "carbs": 30, "fats": 10, "default_g": 150},
    
    # Fallback / Generic
    "unknown": {"calories": 0, "protein": 0, "carbs": 0, "fats": 0, "default_g": 100}
}

def get_food_info(class_name):
    """Returns nutritional info per 100g and default portion size"""
    return FOOD_DB.get(class_name.lower(), None)
