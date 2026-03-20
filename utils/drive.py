"""
Google Drive — رفع وثائق المترشحين
مع تسجيل كامل للأخطاء في session_state
"""
import io
import streamlit as st

try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    DRIVE_OK = True
except ImportError:
    DRIVE_OK = False

SCOPES = ["https://www.googleapis.com/auth/drive"]


def _log(msg):
    """تسجيل رسائل للتشخيص"""
    if "drive_logs" not in st.session_state:
        st.session_state.drive_logs = []
    st.session_state.drive_logs.append(msg)


def _get_service():
    if not DRIVE_OK:
        _log("❌ مكتبات Google غير مثبتة")
        return None
    try:
        creds_info = {
            "type":                        str(st.secrets["google_credentials"]["type"]),
            "project_id":                  str(st.secrets["google_credentials"]["project_id"]),
            "private_key_id":              str(st.secrets["google_credentials"]["private_key_id"]),
            "private_key":                 str(st.secrets["google_credentials"]["private_key"]),
            "client_email":                str(st.secrets["google_credentials"]["client_email"]),
            "client_id":                   str(st.secrets["google_credentials"]["client_id"]),
            "auth_uri":                    str(st.secrets["google_credentials"]["auth_uri"]),
            "token_uri":                   str(st.secrets["google_credentials"]["token_uri"]),
            "auth_provider_x509_cert_url": str(st.secrets["google_credentials"]["auth_provider_x509_cert_url"]),
            "client_x509_cert_url":        str(st.secrets["google_credentials"]["client_x509_cert_url"]),
        }
        creds   = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
        service = build("drive", "v3", credentials=creds)
        _log("✅ اتصال Drive ناجح")
        return service
    except Exception as e:
        _log(f"❌ خطأ في الاتصال: {type(e).__name__}: {e}")
        return None


def _get_or_create_folder(service, name: str, parent_id: str = None) -> str | None:
    try:
        q = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            q += f" and '{parent_id}' in parents"
        res   = service.files().list(q=q, fields="files(id,name)").execute()
        files = res.get("files", [])
        if files:
            _log(f"📁 مجلد موجود: {name}")
            return files[0]["id"]
        meta = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
        if parent_id:
            meta["parents"] = [parent_id]
        folder = service.files().create(body=meta, fields="id").execute()
        _log(f"📁 مجلد جديد: {name} — ID: {folder.get('id')}")
        return folder.get("id")
    except Exception as e:
        _log(f"❌ خطأ في إنشاء المجلد {name}: {e}")
        return None


def upload_file(content: bytes, filename: str, username: str, mime_type: str = "application/pdf") -> str:
    """رفع ملف واحد — يعيد رابط الملف أو فارغ"""
    service = _get_service()
    if not service:
        return ""

    try:
        # المجلد الجذر
        try:
            root_id = str(st.secrets["drive_folder_id"]).strip()
            _log(f"📂 المجلد الجذر من Secrets: {root_id}")
        except Exception:
            root_id = _get_or_create_folder(service, "وثائق_المترشحين_BJB_2026")
            _log(f"📂 المجلد الجذر أُنشئ: {root_id}")

        # مجلد المترشح
        user_folder_id = _get_or_create_folder(service, username, root_id)
        if not user_folder_id:
            _log(f"❌ فشل إنشاء مجلد المترشح: {username}")
            return ""

        # رفع الملف
        if not content:
            _log(f"❌ محتوى الملف فارغ: {filename}")
            return ""

        media = MediaIoBaseUpload(
            io.BytesIO(content),
            mimetype=mime_type,
            resumable=False
        )
        meta = {
            "name":    filename,
            "parents": [user_folder_id],
        }
        _log(f"⬆️ جارٍ رفع: {filename} ({len(content)} bytes)")
        uploaded = service.files().create(
            body=meta, media_body=media, fields="id,webViewLink"
        ).execute()

        file_id = uploaded.get("id", "")
        link    = uploaded.get("webViewLink", "")
        _log(f"✅ رُفع بنجاح: {filename} — ID: {file_id}")

        # صلاحية القراءة
        service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"}
        ).execute()

        return link

    except Exception as e:
        _log(f"❌ خطأ في رفع {filename}: {type(e).__name__}: {e}")
        return ""


def upload_all_from_session(username: str) -> dict:
    """
    رفع كل الملفات المحفوظة في session_state
    يعيد قاموس {اسم_الوثيقة: رابط}
    """
    drive_links = {}
    files_found = 0

    for key, val in list(st.session_state.items()):
        if not key.startswith("file_"):
            continue
        if not isinstance(val, dict):
            continue
        if "content" not in val:
            continue
        if not val["content"]:
            _log(f"⚠️ محتوى فارغ: {key}")
            continue

        files_found += 1
        doc_name = key.replace("file_", "")
        ext      = val["name"].rsplit(".", 1)[-1] if "." in val["name"] else "pdf"
        mime     = val.get("mime", "application/pdf")
        filename = f"{username}_{doc_name}.{ext}"

        link = upload_file(
            content   = val["content"],
            filename  = filename,
            username  = username,
            mime_type = mime,
        )
        if link:
            drive_links[doc_name] = link

    _log(f"📊 ملفات في session: {files_found} — مرفوعة: {len(drive_links)}")
    return drive_links
