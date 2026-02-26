from datetime import datetime
import pandas as pd

def determine_phase(start_date_str):
    """
    Calculates the current physiological phase based on start date.
    
    SEMANA 1–2 → desinflamación
    SEMANA 3–4 → adaptación visual
    SEMANA 5–8 → reducción de cintura
    SEMANA 9+ → definición progresiva
    """
    try:
        start_date = pd.to_datetime(start_date_str).date()
    except:
        start_date = datetime.now().date()
        
    today = datetime.now().date()
    days_diff = (today - start_date).days
    weeks = days_diff / 7.0
    
    if weeks <= 2:
        return "Desinflamación", "Tu cuerpo está eliminando retención de líquidos. El peso bajará rápido, pero no te confíes."
    elif weeks <= 4:
        return "Adaptación Visual", "Tu cuerpo empieza a oxidar grasa real. La ropa te quedará mejor aunque la báscula se frene."
    elif weeks <= 8:
        return "Reducción de Cintura", "Fase crítica de adherencia. Los cambios hormonales están jugando a tu favor."
    else:
        return "Definición Progresiva", "Estás en ritmo de crucero. La constancia ahora es lo único que importa."
