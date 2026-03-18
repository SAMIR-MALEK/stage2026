"""
التكامل مع Google Sheets و Google Drive
"""

import json
import os
from datetime import datetime
from pathlib import Path

import streamlit as st

# ─── التحقق من توفر مكتبات Google ─────────────────────────
try:
    import gspread
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
    import io
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

# ─── النطاقات المطلوبة ────────────────────────────────────
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]

# ─── أسماء الأعمدة في الشيت ──────────────────────────────
SHEET_COLUMNS = [
    "رقم_الملف", "التاريخ", "اللقب", "الاسم", "السلم",
    "الرتبة_الوظيفية", "المؤسسة", "البريد_الإلكتروني",
    "الهاتف", "النقاط_الإجمالية", "تفصيل_النقاط",
    "روابط_الوثائق", "الحالة", "ملاحظات_اللجنة"
]

# ═══════════════════════════════════════════════════════════
# الاتصال بـ Google
# ═══════════════════════════════════════════════════════════

def get_google_credentials():
    """الحصول على بيانات الاعتماد من Streamlit secrets أو ملف JSON"""
    if not GOOGLE_AVAILABLE:
        return None

    try:
        # من Streamlit secrets (للنشر)
        if "google_credentials" in st.secrets:
            creds_dict = dict(st.secrets["google_credentials"])
            creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
            return creds

        # من ملف محلي (للتطوير)
        creds_file = Path("config/google_credentials.json")
        if creds_file.exists():
            creds = Credentials.from_service_account_file(str(creds_file), scopes=SCOPES)
            return creds

    except Exception as e:
        st.error(f"خطأ في بيانات الاعتماد: {e}")

    return None


@st.cache_resource(ttl=300)
def get_sheets_client():
    """الاتصال بـ Google Sheets"""
    creds = get_google_credentials()
    if creds:
        return gspread.authorize(creds)
    return None


def get_drive_service():
    """الاتصال بـ Google Drive"""
    creds = get_google_credentials()
    if creds:
        return build("drive", "v3", credentials=creds)
    return None


# ═══════════════════════════════════════════════════════════
# عمليات Google Sheets
# ═══════════════════════════════════════════════════════════

def get_or_create_spreadsheet(name: str = "منصة_الانتقاء_2026"):
    """الحصول على الشيت أو إنشاؤه"""
    client = get_sheets_client()
    if not client:
        return None

    try:
        return client.open(name)
    except gspread.SpreadsheetNotFound:
        # إنشاء شيت جديد
        sheet = client.create(name)
        _initialize_spreadsheet(sheet)
        return sheet
    except Exception as e:
        st.error(f"خطأ في الشيت: {e}")
        return None


def _initialize_spreadsheet(spreadsheet):
    """تهيئة الشيت بالأعمدة والتنسيق"""
    worksheets_config = [
        ("الموظفون الإداريون والتقنيون", SHEET_COLUMNS),
        ("الإقامة العلمية قصيرة المدى", SHEET_COLUMNS),
        ("تربص تحسين المستوى", SHEET_COLUMNS),
        ("الباحثون الدائمون", SHEET_COLUMNS),
        ("الكل", SHEET_COLUMNS),
    ]

    # الشيت الافتراضية
    first = True
    for ws_name, cols in worksheets_config:
        if first:
            ws = spreadsheet.sheet1
            ws.update_title(ws_name)
            first = False
        else:
            ws = spreadsheet.add_worksheet(title=ws_name, rows=1000, cols=20)

        ws.append_row(cols)
        # تنسيق الرأس (لون أزرق غامق)
        ws.format("A1:N1", {
            "backgroundColor": {"red": 0.1, "green": 0.23, "blue": 0.36},
            "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
            "horizontalAlignment": "CENTER"
        })


def save_candidate_to_sheet(candidate_data: dict, score_result: dict) -> bool:
    """حفظ بيانات المترشح في الشيت"""
    try:
        spreadsheet = get_or_create_spreadsheet()
        if not spreadsheet:
            return _save_locally(candidate_data, score_result)

        scale = score_result.get("scale", "غير محدد")
        ws_name_map = {
            "الموظفون الإداريون والتقنيون": "الموظفون الإداريون والتقنيون",
            "الإقامة العلمية قصيرة المدى": "الإقامة العلمية قصيرة المدى",
            "تربص تحسين المستوى": "تربص تحسين المستوى",
            "التربصات قصيرة المدى للباحثين الدائمين": "الباحثون الدائمون",
        }

        ws_name = ws_name_map.get(scale, "الكل")

        try:
            ws = spreadsheet.worksheet(ws_name)
        except gspread.WorksheetNotFound:
            ws = spreadsheet.sheet1

        all_ws = spreadsheet.worksheet("الكل") if "الكل" in [w.title for w in spreadsheet.worksheets()] else None

        # توليد رقم الملف
        existing = ws.get_all_values()
        file_number = f"DZ-{datetime.now().year}-{len(existing):04d}"

        row = [
            file_number,
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            candidate_data.get("last_name", ""),
            candidate_data.get("first_name", ""),
            scale,
            candidate_data.get("rank", ""),
            candidate_data.get("institution", ""),
            candidate_data.get("email", ""),
            candidate_data.get("phone", ""),
            score_result.get("total", 0),
            json.dumps(score_result.get("breakdown", {}), ensure_ascii=False),
            candidate_data.get("drive_links", ""),
            "قيد المراجعة",
            ""
        ]

        ws.append_row(row)
        if all_ws:
            all_ws.append_row(row)

        return True

    except Exception as e:
        st.warning(f"تعذر الحفظ على Google Sheets، يتم الحفظ محلياً: {e}")
        return _save_locally(candidate_data, score_result)


def _save_locally(candidate_data: dict, score_result: dict) -> bool:
    """حفظ محلي احتياطي (CSV)"""
    import csv
    backup_file = Path("data/candidates_backup.csv")
    backup_file.parent.mkdir(exist_ok=True)

    file_exists = backup_file.exists()
    with open(backup_file, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=SHEET_COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "رقم_الملف": f"LOCAL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "اللقب": candidate_data.get("last_name", ""),
            "الاسم": candidate_data.get("first_name", ""),
            "السلم": score_result.get("scale", ""),
            "الرتبة_الوظيفية": candidate_data.get("rank", ""),
            "المؤسسة": candidate_data.get("institution", ""),
            "البريد_الإلكتروني": candidate_data.get("email", ""),
            "الهاتف": candidate_data.get("phone", ""),
            "النقاط_الإجمالية": score_result.get("total", 0),
            "تفصيل_النقاط": json.dumps(score_result.get("breakdown", {}), ensure_ascii=False),
            "روابط_الوثائق": "",
            "الحالة": "قيد المراجعة",
            "ملاحظات_اللجنة": ""
        })
    return True


def get_all_candidates(scale_filter: str = None):
    """جلب جميع المترشحين من الشيت"""
    try:
        spreadsheet = get_or_create_spreadsheet()
        if not spreadsheet:
            return _load_local_candidates()

        ws_name = "الكل"
        if scale_filter:
            ws_map = {
                "الموظفون الإداريون والتقنيون": "الموظفون الإداريون والتقنيون",
                "الإقامة العلمية قصيرة المدى": "الإقامة العلمية قصيرة المدى",
                "تربص تحسين المستوى": "تربص تحسين المستوى",
                "الباحثون الدائمون": "الباحثون الدائمون",
            }
            ws_name = ws_map.get(scale_filter, "الكل")

        ws = spreadsheet.worksheet(ws_name)
        records = ws.get_all_records()
        return records

    except Exception as e:
        return _load_local_candidates()


def _load_local_candidates():
    """تحميل البيانات المحلية"""
    import csv
    backup_file = Path("data/candidates_backup.csv")
    if not backup_file.exists():
        return []

    with open(backup_file, "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


# ═══════════════════════════════════════════════════════════
# نظام الدخول — اسم المستخدم + كلمة المرور من الشيت
# المؤسسة ثابتة: كلية الحقوق والعلوم السياسية / جامعة برج بوعريريج
# ═══════════════════════════════════════════════════════════

USERS_SHEET_NAME = "المستخدمون"

USERS_COLUMNS = [
    "اسم_المستخدم",   # username
    "كلمة_المرور",    # password (نص عادي — الإدارة تضعه يدوياً)
    "الاسم_الكامل",   # يُعرض بعد الدخول
    "الدور",           # مترشح / لجنة الانتقاء / إدارة
    "الحالة",          # active / inactive
    "تاريخ_الإنشاء",
]

ROLE_MAP = {
    "إدارة":          "admin",
    "لجنة":           "committee",
    "لجنة الانتقاء": "committee",
    "مترشح":          "candidate",
    "admin":          "admin",
    "committee":      "committee",
    "candidate":      "candidate",
}


def verify_credentials(username: str, password: str) -> dict | None:
    """التحقق من اسم المستخدم وكلمة المرور من ورقة المستخدمين"""
    try:
        spreadsheet = get_or_create_spreadsheet()
        if not spreadsheet:
            return None
        try:
            ws = spreadsheet.worksheet(USERS_SHEET_NAME)
        except gspread.WorksheetNotFound:
            ws = _create_users_sheet(spreadsheet)

        for row in ws.get_all_records():
            row_user = str(row.get("اسم_المستخدم", "")).strip().lower()
            row_pass = str(row.get("كلمة_المرور", "")).strip()
            if row_user == username.lower() and row_pass == password:
                role_raw = str(row.get("الدور", "")).strip()
                return {
                    "name":   row.get("الاسم_الكامل", username),
                    "role":   ROLE_MAP.get(role_raw, "candidate"),
                    "status": str(row.get("الحالة", "active")).strip().lower(),
                }
        return None
    except Exception:
        return None


def _create_users_sheet(spreadsheet):
    """إنشاء ورقة المستخدمين مع بيانات تجريبية أولية"""
    ws = spreadsheet.add_worksheet(title=USERS_SHEET_NAME, rows=500, cols=8)
    ws.append_row(USERS_COLUMNS)
    ws.format("A1:F1", {
        "backgroundColor": {"red": 0.1, "green": 0.23, "blue": 0.36},
        "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
        "horizontalAlignment": "CENTER"
    })
    today = datetime.now().strftime("%Y-%m-%d")
    demo = [
        ["admin",   "admin2026", "مدير المنصة",   "إدارة",          "active", today],
        ["comite1", "com2026",   "أ. فاطمة حمدي", "لجنة الانتقاء", "active", today],
        ["benali",  "cand2026",  "محمد بن علي",   "مترشح",          "active", today],
        ["maamri",  "cand1234",  "سارة معمري",    "مترشح",          "active", today],
    ]
    for row in demo:
        ws.append_row(row)
    return ws


def add_user_to_sheet(username: str, password: str, name: str, role: str) -> bool:
    """إضافة مستخدم جديد من لوحة الإدارة"""
    try:
        spreadsheet = get_or_create_spreadsheet()
        if not spreadsheet:
            return False
        try:
            ws = spreadsheet.worksheet(USERS_SHEET_NAME)
        except gspread.WorksheetNotFound:
            ws = _create_users_sheet(spreadsheet)
        ws.append_row([
            username.lower(), password, name, role,
            "active", datetime.now().strftime("%Y-%m-%d")
        ])
        return True
    except Exception:
        return False


def update_candidate_status(file_number: str, status: str, notes: str = ""):
    """تحديث حالة المترشح"""
    try:
        spreadsheet = get_or_create_spreadsheet()
        if not spreadsheet:
            return False

        for ws in spreadsheet.worksheets():
            cell = ws.find(file_number)
            if cell:
                row = cell.row
                # الحالة في العمود 13، الملاحظات في 14
                ws.update_cell(row, 13, status)
                if notes:
                    ws.update_cell(row, 14, notes)
        return True
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════
# عمليات Google Drive
# ═══════════════════════════════════════════════════════════

def get_or_create_drive_folder(folder_name: str, parent_id: str = None) -> str | None:
    """إنشاء مجلد على Drive أو الحصول عليه"""
    service = get_drive_service()
    if not service:
        return None

    try:
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get("files", [])

        if files:
            return files[0]["id"]

        # إنشاء مجلد جديد
        metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id:
            metadata["parents"] = [parent_id]

        folder = service.files().create(body=metadata, fields="id").execute()
        return folder.get("id")

    except Exception as e:
        st.error(f"خطأ في إنشاء المجلد: {e}")
        return None


def upload_file_to_drive(file_obj, filename: str, candidate_name: str, mime_type: str = "application/pdf") -> str | None:
    """رفع ملف على Google Drive"""
    service = get_drive_service()
    if not service:
        return None

    try:
        # إنشاء هيكل المجلدات: منصة_الانتقاء / اسم_المترشح /
        root_folder_id = get_or_create_drive_folder("منصة_الانتقاء_2026")
        candidate_folder_id = get_or_create_drive_folder(candidate_name, root_folder_id)

        file_metadata = {
            "name": filename,
            "parents": [candidate_folder_id] if candidate_folder_id else [],
        }

        if hasattr(file_obj, "read"):
            content = file_obj.read()
        else:
            content = file_obj

        media = MediaIoBaseUpload(
            io.BytesIO(content),
            mimetype=mime_type,
            resumable=True
        )

        uploaded = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink"
        ).execute()

        # منح صلاحية القراءة
        service.permissions().create(
            fileId=uploaded["id"],
            body={"type": "anyone", "role": "reader"}
        ).execute()

        return uploaded.get("webViewLink", "")

    except Exception as e:
        st.error(f"خطأ في رفع الملف: {e}")
        return None


def upload_multiple_files(files: list, candidate_name: str) -> dict:
    """رفع عدة ملفات ورجوع روابطها"""
    links = {}
    doc_names = {
        "cv": "السيرة الذاتية",
        "degree": "الشهادة العلمية",
        "rank_cert": "شهادة الرتبة",
        "work_cert": "شهادة العمل",
        "supervisor_eval": "تقييم المسؤول",
        "articles": "المقالات العلمية",
        "projects": "المشاريع",
        "other": "وثائق أخرى",
    }

    for key, file_obj in files:
        if file_obj is not None:
            name = doc_names.get(key, key)
            ext = getattr(file_obj, "name", "file").split(".")[-1]
            filename = f"{candidate_name}_{name}.{ext}"
            mime = "application/pdf" if ext == "pdf" else "image/jpeg"
            link = upload_file_to_drive(file_obj, filename, candidate_name, mime)
            if link:
                links[name] = link

    return links
