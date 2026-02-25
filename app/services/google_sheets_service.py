import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials
from datetime import datetime
from app.config import settings

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

@st.cache_resource
def get_gspread_client():
    """
    Returns a gspread client using credentials from Streamlit secrets.
    """
    try:
        # Check if secrets are available
        if "gcp_service_account" in st.secrets:
            creds_dict = st.secrets["gcp_service_account"]
            credentials = Credentials.from_service_account_info(
                creds_dict, scopes=SCOPE
            )
            return gspread.authorize(credentials)
        else:
            st.error("Google Cloud Credentials not found in secrets.")
            return None
    except Exception as e:
        st.error(f"Error authenticating with Google Sheets: {e}")
        return None

def get_spreadsheet():
    """
    Opens the spreadsheet defined in secrets.
    """
    client = get_gspread_client()
    if not client:
        return None
    
    try:
        sheet_name = st.secrets["spreadsheet"]["name"]
        return client.open(sheet_name)
    except Exception as e:
        st.error(f"Error opening spreadsheet: {e}")
        return None

def init_sheets():
    """
    Ensures all required worksheets exist and have the correct headers.
    """
    sh = get_spreadsheet()
    if not sh:
        return

    existing_titles = [ws.title for ws in sh.worksheets()]

    # Define schema map
    schema_map = {
        settings.SHEET_BODY_METRICS: settings.COLS_BODY,
        settings.SHEET_NUTRITION_LOG: settings.COLS_NUTRITION,
        settings.SHEET_WATER_LOG: settings.COLS_WATER,
        settings.SHEET_MEDICATION_LOG: settings.COLS_MEDS,
        settings.SHEET_HABITS_LOG: settings.COLS_HABITS,
        settings.SHEET_GOALS: settings.COLS_GOALS,
    }

    for sheet_name, cols in schema_map.items():
        if sheet_name not in existing_titles:
            try:
                ws = sh.add_worksheet(title=sheet_name, rows=100, cols=len(cols))
                ws.append_row(cols)
                st.toast(f"Created sheet: {sheet_name}")
            except Exception as e:
                st.error(f"Failed to create sheet {sheet_name}: {e}")
        else:
            # Optional: Check headers?
            pass

@st.cache_data(ttl=60)
def load_data(sheet_name):
    """
    Loads data from a specific sheet into a Pandas DataFrame.
    """
    sh = get_spreadsheet()
    if not sh:
        return pd.DataFrame()
    
    try:
        ws = sh.worksheet(sheet_name)
        data = ws.get_all_records()
        df = pd.DataFrame(data)
        
        # Ensure date column is datetime if it exists
        if "date" in df.columns and not df.empty:
             df["date"] = pd.to_datetime(df["date"], errors='coerce').dt.date
             
        return df
    except gspread.exceptions.WorksheetNotFound:
        st.error(f"Worksheet {sheet_name} not found.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data from {sheet_name}: {e}")
        return pd.DataFrame()

def add_row(sheet_name, row_data):
    """
    Appends a row to the specified sheet.
    Clears cache after update.
    """
    sh = get_spreadsheet()
    if not sh:
        return False
    
    try:
        ws = sh.worksheet(sheet_name)
        # Ensure row_data matches the column order
        # For simplicity, we assume row_data is a list in correct order 
        # OR a dict that we map to columns.
        
        # If dict, map to columns
        if isinstance(row_data, dict):
            # Get columns from settings
            if sheet_name == settings.SHEET_BODY_METRICS: cols = settings.COLS_BODY
            elif sheet_name == settings.SHEET_NUTRITION_LOG: cols = settings.COLS_NUTRITION
            elif sheet_name == settings.SHEET_WATER_LOG: cols = settings.COLS_WATER
            elif sheet_name == settings.SHEET_MEDICATION_LOG: cols = settings.COLS_MEDS
            elif sheet_name == settings.SHEET_HABITS_LOG: cols = settings.COLS_HABITS
            elif sheet_name == settings.SHEET_GOALS: cols = settings.COLS_GOALS
            else: return False
            
            row_values = [row_data.get(c, "") for c in cols]
            # Convert dates to string if needed
            row_values = [str(v) if isinstance(v, (datetime, pd.Timestamp)) else v for v in row_values]
        else:
            row_values = row_data

        ws.append_row(row_values)
        load_data.clear() # Invalidate cache
        return True
    except Exception as e:
        st.error(f"Error adding row to {sheet_name}: {e}")
        return False
