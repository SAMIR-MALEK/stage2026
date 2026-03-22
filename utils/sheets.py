"""Google Sheets — حفظ بيانات المترشحين مع عناوين واضحة"""
import streamlit as st
from datetime import datetime

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_OK = True
except ImportError:
    GOOGLE_OK = False

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]
SHEET_NAME = "منصة_الانتقاء_BJB_2026"

HEADERS = [
    "التاريخ",
    "اسم_المستخدم",
    "الاسم_الكامل",
    "السلك",
    "الرتبة",
    "الصنف",
    "سنوات_الخدمة",
    "الصيغة",
    "النقاط_الجزئية",
    "نقاط_الرتبة",
    "النقاط_الكلية",
    "تفصيل_النقاط",
    "روابط_الوثائق",
    "الحالة",
]

HEADER_FORMAT = {
    "backgroundColor": {"red": 0.1, "green": 0.23, "blue": 0.36},
    "textFormat": {
        "bold": True,
        "foregroundColor": {"red": 1, "green": 1, "blue": 1},
        "fontSize": 11,
    },
    "horizontalAlignment": "CENTER",
    "verticalAlignment": "MIDDLE",
}


def _get_client():
    if not GOOGLE_OK:
        return None
    try:
        creds_info = {k: str(st.secrets["google_credentials"][k]) for k in [
            "type","project_id","private_key_id","private_key","client_email",
            "client_id","auth_uri","token_uri",
            "auth_provider_x509_cert_url","client_x509_cert_url"
        ]}
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
        return gspread.authorize(creds)
    except Exception:
        return None


def _get_or_create_sheet(client):
    try:
        sh = client.open(SHEET_NAME)
        ws = sh.sheet1
        # تحقق من العناوين — إذا فارغ أضفها
        first_row = ws.row_values(1)
        if not first_row or first_row[0] != "التاريخ":
            ws.insert_row(HEADERS, 1)
            ws.format(f"A1:{chr(64+len(HEADERS))}1", HEADER_FORMAT)
            # تجميد الصف الأول
            sh.batch_update({"requests": [{"updateSheetProperties": {
                "properties": {"sheetId": ws.id, "gridProperties": {"frozenRowCount": 1}},
                "fields": "gridProperties.frozenRowCount"
            }}]})
        return sh
    except gspread.SpreadsheetNotFound:
        sh = client.create(SHEET_NAME)
        ws = sh.sheet1
        ws.update_title("الطلبات")
        ws.append_row(HEADERS)
        ws.format(f"A1:{chr(64+len(HEADERS))}1", HEADER_FORMAT)
        return sh


def save_application(data: dict) -> bool:
    client = _get_client()
    if not client:
        return False
    try:
        sh = _get_or_create_sheet(client)
        ws = sh.sheet1
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            data.get("username",      ""),
            data.get("name",          ""),
            data.get("silk",          data.get("position", "")),
            data.get("rank",          data.get("grade", "")),
            data.get("grade_num",     ""),
            data.get("years",         ""),
            data.get("scale",         ""),
            data.get("total_score",   0),
            data.get("rank_pts",      0),
            data.get("total_score",   0),
            data.get("breakdown",     "{}"),
            data.get("drive_links",   "{}"),
            data.get("status",        "قيد المراجعة"),
        ]
        ws.append_row(row)
        # تنسيق الصف الجديد
        last_row = len(ws.get_all_values())
        ws.format(f"A{last_row}:{chr(64+len(HEADERS))}{last_row}", {
            "horizontalAlignment": "CENTER",
            "verticalAlignment": "MIDDLE",
        })
        return True
    except Exception:
        return False


def get_all_records() -> list[dict]:
    client = _get_client()
    if not client:
        return []
    try:
        sh = _get_or_create_sheet(client)
        return sh.sheet1.get_all_records()
    except Exception:
        return []


def check_already_submitted(username: str) -> dict | None:
    """تحقق إذا سبق للمترشح التقديم — يعيد بياناته أو None"""
    records = get_all_records()
    for r in records:
        if str(r.get("اسم_المستخدم", "")).strip() == username:
            return r
    return None
