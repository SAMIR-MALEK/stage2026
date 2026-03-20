"""
Google Drive — رفع وثائق المترشحين
كل مترشح له مجلد خاص: وثائق_المترشحين / اسم_المستخدم /
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

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]


def _get_drive_service():
    if not DRIVE_OK:
        return None
    try:
        creds = Credentials.from_service_account_info(
            dict(st.secrets["google_credentials"]), scopes=SCOPES
        )
        return build("drive", "v3", credentials=creds)
    except Exception:
        return None


def _get_or_create_folder(service, name: str, parent_id: str = None) -> str | None:
    """الحصول على مجلد أو إنشاؤه"""
    try:
        q = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            q += f" and '{parent_id}' in parents"
        res = service.files().list(q=q, fields="files(id)").execute()
        files = res.get("files", [])
        if files:
            return files[0]["id"]
        # إنشاء مجلد جديد
        meta = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
        if parent_id:
            meta["parents"] = [parent_id]
        folder = service.files().create(body=meta, fields="id").execute()
        return folder.get("id")
    except Exception:
        return None


def upload_file(file_obj, filename: str, username: str, mime_type: str = "application/pdf") -> str:
    """
    رفع ملف على Drive داخل مجلد المترشح
    يعيد رابط الملف أو "" إذا فشل
    """
    service = _get_drive_service()
    if not service:
        return ""

    try:
        # الحصول على المجلد الجذر من Secrets أو إنشاؤه
        root_id = st.secrets.get("drive_folder_id", None)
        if not root_id:
            root_id = _get_or_create_folder(service, "وثائق_المترشحين_BJB_2026")

        # مجلد خاص بالمترشح
        user_folder_id = _get_or_create_folder(service, username, root_id)

        # رفع الملف
        if hasattr(file_obj, "read"):
            content = file_obj.read()
        else:
            content = file_obj

        media = MediaIoBaseUpload(io.BytesIO(content), mimetype=mime_type, resumable=False)
        meta  = {"name": filename, "parents": [user_folder_id] if user_folder_id else []}
        uploaded = service.files().create(body=meta, media_body=media, fields="id,webViewLink").execute()

        # منح صلاحية عرض للجميع (اللجنة تقدر تشوف)
        service.permissions().create(
            fileId=uploaded["id"],
            body={"type": "anyone", "role": "reader"}
        ).execute()

        return uploaded.get("webViewLink", "")
    except Exception as e:
        return ""


def upload_multiple(files_dict: dict, username: str) -> dict:
    """
    رفع عدة ملفات
    files_dict = {"اسم_الوثيقة": file_object, ...}
    يعيد {"اسم_الوثيقة": "رابط", ...}
    """
    links = {}
    for doc_name, file_obj in files_dict.items():
        if file_obj is None:
            continue
        ext = getattr(file_obj, "name", "file").rsplit(".", 1)[-1].lower()
        mime = {
            "pdf":  "application/pdf",
            "jpg":  "image/jpeg",
            "jpeg": "image/jpeg",
            "png":  "image/png",
        }.get(ext, "application/octet-stream")
        filename = f"{username}_{doc_name}.{ext}"
        link = upload_file(file_obj, filename, username, mime)
        if link:
            links[doc_name] = link
    return links
