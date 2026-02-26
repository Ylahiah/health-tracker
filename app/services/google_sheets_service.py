import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd
from app.config import settings

def get_client():
    """
    Authenticates with Google Sheets using secrets.
    """
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    # Load credentials from Streamlit secrets
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client

def init_sheets():
    """
    Initializes the Google Sheet and required worksheets if they don't exist.
    """
    client = get_client()
    try:
        # Try to open existing sheet
        sheet_name = st.secrets["spreadsheet"]["name"]
        sh = client.open(sheet_name)
    except gspread.SpreadsheetNotFound:
        st.error(f"Spreadsheet '{sheet_name}' not found. Please create it and share with service account email.")
        return

    # Define required worksheets and their columns
    required_sheets = {
        settings.SHEET_BODY_METRICS: settings.COLS_BODY,
        settings.SHEET_NUTRITION_LOG: settings.COLS_NUTRITION,
        settings.SHEET_WATER_LOG: settings.COLS_WATER,
        settings.SHEET_MEDICATION_LOG: settings.COLS_MEDS,
        settings.SHEET_HABITS_LOG: settings.COLS_HABITS,
        settings.SHEET_GOALS: settings.COLS_GOALS,
        settings.SHEET_PROFILE: settings.COLS_PROFILE
    }

    existing_titles = [ws.title for ws in sh.worksheets()]

    for title, cols in required_sheets.items():
        if title not in existing_titles:
            ws = sh.add_worksheet(title=title, rows=100, cols=len(cols))
            ws.append_row(cols)
            # st.toast(f"Created worksheet: {title}")

@st.cache_data(ttl=60)
def load_data(worksheet_name):
    """
    Loads data from a specific worksheet into a pandas DataFrame.
    Cached for 60 seconds to optimize Cloud Run performance.
    """
    client = get_client()
    try:
        sheet_name = st.secrets["spreadsheet"]["name"]
        sh = client.open(sheet_name)
        ws = sh.worksheet(worksheet_name)
        data = ws.get_all_records()
        return pd.DataFrame(data)
    except gspread.WorksheetNotFound:
        # st.warning(f"Worksheet {worksheet_name} not found.")
        return pd.DataFrame()
    except Exception as e:
        # st.error(f"Error loading {worksheet_name}: {e}")
        return pd.DataFrame()

def add_row(worksheet_name, row_data):
    """
    Appends a row to the specified worksheet.
    row_data: dict where keys match column names
    """
    client = get_client()
    try:
        sheet_name = st.secrets["spreadsheet"]["name"]
        sh = client.open(sheet_name)
        ws = sh.worksheet(worksheet_name)
        
        # Get headers to ensure correct order
        headers = ws.row_values(1)
        
        # Prepare row values in order
        row_values = []
        for col in headers:
            row_values.append(row_data.get(col, ""))
            
        ws.append_row(row_values)
        
        # Invalidate cache for this worksheet so UI updates immediately
        load_data.clear()
        
        return True
    except Exception as e:
        st.error(f"Error adding row to {worksheet_name}: {e}")
        return False
