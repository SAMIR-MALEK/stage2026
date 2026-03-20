"""
حفظ الوثائق في Google Sheets كـ base64
يستخدم نفس client من sheets.py
"""
import base64
import streamlit as st


def _log(msg):
    if "drive_logs" not in st.session_state:
        st.session_state.drive_logs = []
    st.session_state.drive_logs.append(msg)


def _get_docs_sheet():
    """الحصول على ورقة الوثائق من نفس Spreadsheet"""
    try:
        from utils.sheets import _get_client, SHEET_NAME
        client = _get_client()
        if not client:
            _log("❌ client فارغ")
            return None
        sh = client.open(SHEET_NAME)
        try:
            ws = sh.worksheet("الوثائق")
            _log("✅ ورقة الوثائق موجودة")
            return ws
        except Exception:
            _log("📋 إنشاء ورقة الوثائق...")
            ws = sh.add_worksheet(title="الوثائق", rows=2000, cols=6)
            ws.append_row(["اسم_المستخدم","اسم_الوثيقة","اسم_الملف","نوع_الملف","الحجم_KB","base64"])
            ws.format("A1:F1", {
                "backgroundColor": {"red":0.1,"green":0.23,"blue":0.36},
                "textFormat": {"bold":True,"foregroundColor":{"red":1,"green":1,"blue":1}},
            })
            _log("✅ ورقة الوثائق أُنشئت")
            return ws
    except Exception as e:
        _log(f"❌ خطأ في الاتصال بـ Sheets: {type(e).__name__}: {e}")
        return None


def upload_all_from_session(username: str) -> dict:
    """حفظ كل ملفات session_state في شيت الوثائق"""
    files = [
        (k, v) for k, v in st.session_state.items()
        if k.startswith("file_") and isinstance(v, dict) and v.get("content")
    ]
    _log(f"📊 ملفات في session: {len(files)}")

    if not files:
        _log("⚠️ لا توجد ملفات")
        return {}

    ws = _get_docs_sheet()
    if not ws:
        _log("❌ تعذر الوصول لورقة الوثائق")
        return _save_locally(username, files)

    saved = {}
    for key, val in files:
        try:
            doc_name = key.replace("file_", "")
            content  = val["content"]
            b64      = base64.b64encode(content).decode("utf-8")
            size_kb  = len(content) // 1024

            ws.append_row([
                username,
                doc_name,
                val["name"],
                val.get("mime", "application/pdf"),
                size_kb,
                b64,
            ])
            saved[doc_name] = f"✅ محفوظ ({size_kb} KB)"
            _log(f"✅ حُفظ: {val['name']} ({size_kb} KB)")
        except Exception as e:
            _log(f"❌ خطأ في حفظ {val.get('name','?')}: {e}")

    _log(f"📊 مرفوعة: {len(saved)}/{len(files)}")
    return saved


def _save_locally(username: str, files: list) -> dict:
    """حفظ احتياطي محلي"""
    from pathlib import Path
    saved = {}
    docs_dir = Path(f"data/docs/{username}")
    docs_dir.mkdir(parents=True, exist_ok=True)
    for key, val in files:
        doc_name = key.replace("file_", "")
        ext = val["name"].rsplit(".", 1)[-1] if "." in val["name"] else "pdf"
        fpath = docs_dir / f"{doc_name}.{ext}"
        with open(fpath, "wb") as f:
            f.write(val["content"])
        saved[doc_name] = f"local:{fpath}"
        _log(f"💾 حُفظ محلياً: {fpath}")
    return saved


def get_candidate_docs(username: str) -> list[dict]:
    """استرجاع وثائق مترشح من شيت الوثائق"""
    docs = []
    try:
        ws = _get_docs_sheet()
        if not ws:
            return []
        records = ws.get_all_records()
        for r in records:
            if str(r.get("اسم_المستخدم", "")).strip() == username:
                docs.append({
                    "name":        r.get("اسم_الوثيقة", ""),
                    "filename":    r.get("اسم_الملف", ""),
                    "mime":        r.get("نوع_الملف", "application/pdf"),
                    "size_kb":     r.get("الحجم_KB", 0),
                    "content_b64": r.get("base64", ""),
                })
    except Exception as e:
        _log(f"❌ خطأ في استرجاع الوثائق: {e}")
    return docs
