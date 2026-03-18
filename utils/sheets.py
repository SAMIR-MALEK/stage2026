import streamlit as st
from datetime import datetime
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_OK = True
except ImportError:
    GOOGLE_OK = False

SCOPES=["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive","https://www.googleapis.com/auth/spreadsheets"]
SHEET_NAME="منصة_الانتقاء_BJB_2026"
HEADERS=["التاريخ","اسم_المستخدم","الاسم_الكامل","الرتبة_الوظيفية","المنصب","السلم","النقاط_الإجمالية","تفصيل_النقاط","الحالة"]

def _get_client():
    if not GOOGLE_OK: return None
    try:
        creds=Credentials.from_service_account_info(dict(st.secrets["google_credentials"]),scopes=SCOPES)
        return gspread.authorize(creds)
    except Exception: return None

def save_application(data:dict)->bool:
    c=_get_client()
    if not c: return False
    try:
        try: sh=c.open(SHEET_NAME)
        except gspread.SpreadsheetNotFound:
            sh=c.create(SHEET_NAME); ws=sh.sheet1
            ws.update_title("الطلبات"); ws.append_row(HEADERS)
            ws.format("A1:I1",{"backgroundColor":{"red":0.1,"green":0.23,"blue":0.36},"textFormat":{"bold":True,"foregroundColor":{"red":1,"green":1,"blue":1}}})
        ws=sh.sheet1
        ws.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"),data.get("username",""),data.get("name",""),data.get("grade",""),data.get("position",""),data.get("scale",""),data.get("total_score",0),data.get("breakdown","{}"),data.get("status","قيد المراجعة")])
        return True
    except Exception: return False
