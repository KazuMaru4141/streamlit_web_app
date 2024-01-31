import streamlit as st
import gspread
from google.oauth2 import service_account

class GspreadCtrl:
    def connect_gspread(key):
        
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets', 
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = service_account.Credentials.from_service_account_info( 
                                                                            st.secrets["gcp_service_account"], 
                                                                            scopes=scopes)
        gc = gspread.authorize(credentials)
                
        SPREADSHEET_KEY = key
        workbook = gc.open_by_key(key)
        worksheet = gc.open_by_key(key).sheet1
        
        SpreadInfo = worksheet.get_all_records()
        
        return worksheet, workbook, SpreadInfo
