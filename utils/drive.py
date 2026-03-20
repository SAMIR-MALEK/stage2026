"""
Google Drive — رفع وثائق المترشحين
الإصلاح: قراءة secrets بالطريقة الصحيحة + معالجة BytesIO
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
        creds_dict = {
            "type":                        st.secrets["google_credentials"]["type"],
            "project_id":                  st.secrets["google_credentials"]["project_id"],
            "private_key_id":              st.secrets["google_credentials"]["private_key_id"],
            "private_key":                 st.secrets["google_credentials"]["private_key"],
            "client_email":                st.secrets["google_credentials"]["client_email"],
            "client_id":                   st.secrets["google_credentials"]["client_id"],
            "auth_uri":                    st.secrets["google_credentials"]["auth_uri"],
            "token_uri":                   st.secrets["google_credentials"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["google_credentials"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url":        st.secrets["google_credentials"]["client_x509_cert_url"],
        }
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        return build("drive", "v3", credentials=creds)
    except Exception as e:
        return None


def _get_or_create_folder(service, name: str, parent_id: str = None) -> str | None:
    try:
        q = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            q += f" and '{parent_id}' in parents"
        res   = service.files().list(q=q, fields="files(id)").execute()
        files = res.get("files", [])
        if files:
            return files[0]["id"]
        meta = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
        if parent_id:
            meta["parents"] = [parent_id]
        folder = service.files().create(body=meta, fields="id").execute()
        return folder.get("id")
    except Exception:
        return None


def upload_file(content: bytes, filename: str, username: str, mime_type: str = "application/pdf") -> str:
    """
    رفع ملف على Drive — يقبل bytes مباشرة
    """
    service = _get_drive_service()
    if not service:
        return ""
    try:
        # المجلد الجذر
        try:
            root_id = st.secrets["drive_folder_id"]
        except Exception:
            root_id = _get_or_create_folder(service, "وثائق_المترشحين_BJB_2026")

        # مجلد المترشح
        user_folder_id = _get_or_create_folder(service, username, root_id)
        if not user_folder_id:
            return ""

        # رفع الملف
        media = MediaIoBaseUpload(
            io.BytesIO(content),
            mimetype=mime_type,
            resumable=False
        )
        meta = {
            "name":    filename,
            "parents": [user_folder_id],
        }
        uploaded = service.files().create(
            body=meta, media_body=media, fields="id,webViewLink"
        ).execute()

        # منح صلاحية القراءة للجميع
        service.permissions().create(
            fileId=uploaded["id"],
            body={"type": "anyone", "role": "reader"}
        ).execute()

        return uploaded.get("webViewLink", "")
    except Exception:
        return ""
