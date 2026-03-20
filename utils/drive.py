"""
حفظ الوثائق — الحل: Base64 في Google Sheets
بدلاً من Drive (الذي يرفض Service Account بسبب quota)
الوثائق تُحفظ كـ base64 في شيت منفصل
اللجنة تقدر تحمّل كل وثيقة مباشرة
"""
import io
import base64
import streamlit as st

DRIVE_OK = False  # لم نعد نستخدم Drive


def _log(msg):
    if "drive_logs" not in st.session_state:
        st.session_state.drive_logs = []
    st.session_state.drive_logs.append(msg)


def _get_sheets_client():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        SCOPES = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
        ]
        creds_info = {k: str(st.secrets["google_credentials"][k]) for k in [
            "type","project_id","private_key_id","private_key","client_email",
            "client_id","auth_uri","token_uri","auth_provider_x509_cert_url","client_x509_cert_url"
        ]}
        creds  = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        _log(f"❌ خطأ Sheets: {e}")
        return None


def _get_or_create_docs_sheet(client):
    """الحصول على شيت الوثائق أو إنشاؤه"""
    SHEET_NAME = "منصة_الانتقاء_BJB_2026"
    DOCS_SHEET = "الوثائق"
    try:
        sh = client.open(SHEET_NAME)
    except Exception:
        return None
    try:
        return sh.worksheet(DOCS_SHEET)
    except Exception:
        ws = sh.add_worksheet(title=DOCS_SHEET, rows=1000, cols=6)
        ws.append_row(["اسم_المستخدم", "اسم_الوثيقة", "اسم_الملف", "نوع_الملف", "الحجم_KB", "base64"])
        ws.format("A1:F1", {
            "backgroundColor": {"red": 0.1, "green": 0.23, "blue": 0.36},
            "textFormat": {"bold": True, "foregroundColor": {"red":1,"green":1,"blue":1}},
        })
        return ws


def upload_all_from_session(username: str) -> dict:
    """
    حفظ كل الوثائق في شيت الوثائق كـ base64
    يعيد قاموس {اسم_الوثيقة: "محفوظ في Sheets"}
    """
    files = [(k,v) for k,v in st.session_state.items()
             if k.startswith("file_") and isinstance(v,dict) and v.get("content")]
    
    _log(f"📊 ملفات في session: {len(files)}")
    
    if not files:
        _log("⚠️ لا توجد ملفات للرفع")
        return {}

    # حفظ في Sheets
    saved = {}
    try:
        client = _get_sheets_client()
        if client:
            ws = _get_or_create_docs_sheet(client)
            if ws:
                for key, val in files:
                    doc_name = key.replace("file_", "")
                    content  = val["content"]
                    b64      = base64.b64encode(content).decode("utf-8")
                    size_kb  = len(content) // 1024
                    ws.append_row([
                        username,
                        doc_name,
                        val["name"],
                        val.get("mime","application/pdf"),
                        size_kb,
                        b64,
                    ])
                    saved[doc_name] = f"sheets:{doc_name}"
                    _log(f"✅ حُفظ في Sheets: {val['name']} ({size_kb} KB)")
    except Exception as e:
        _log(f"❌ خطأ في الحفظ: {e}")

    # حفظ محلي احتياطي
    if not saved:
        from pathlib import Path
        docs_dir = Path(f"data/docs/{username}")
        docs_dir.mkdir(parents=True, exist_ok=True)
        for key, val in files:
            doc_name = key.replace("file_", "")
            ext      = val["name"].rsplit(".",1)[-1] if "." in val["name"] else "pdf"
            fpath    = docs_dir / f"{doc_name}.{ext}"
            with open(fpath, "wb") as f:
                f.write(val["content"])
            saved[doc_name] = f"local:{fpath}"
            _log(f"✅ حُفظ محلياً: {fpath}")

    _log(f"📊 مرفوعة: {len(saved)}")
    return saved


def get_candidate_docs(username: str) -> list[dict]:
    """
    استرجاع وثائق مترشح من Sheets
    يعيد قائمة من dict: {name, filename, mime, size_kb, content_b64}
    """
    docs = []
    try:
        client = _get_sheets_client()
        if not client:
            return []
        ws = _get_or_create_docs_sheet(client)
        if not ws:
            return []
        records = ws.get_all_records()
        for r in records:
            if str(r.get("اسم_المستخدم","")).strip() == username:
                docs.append({
                    "name":        r.get("اسم_الوثيقة",""),
                    "filename":    r.get("اسم_الملف",""),
                    "mime":        r.get("نوع_الملف","application/pdf"),
                    "size_kb":     r.get("الحجم_KB", 0),
                    "content_b64": r.get("base64",""),
                })
    except Exception as e:
        _log(f"❌ خطأ في استرجاع الوثائق: {e}")
    return docs
