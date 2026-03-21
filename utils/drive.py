"""
Google Drive — Shared Drive
يرفع الملفات في Shared Drive BJB2026
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
    if "drive_logs" not in st.session_state:
        st.session_state.drive_logs = []
    st.session_state.drive_logs.append(msg)


def _get_service():
    if not DRIVE_OK:
        _log("❌ مكتبات Google غير مثبتة")
        return None
    try:
        creds_info = {k: str(st.secrets["google_credentials"][k]) for k in [
            "type","project_id","private_key_id","private_key","client_email",
            "client_id","auth_uri","token_uri",
            "auth_provider_x509_cert_url","client_x509_cert_url"
        ]}
        creds   = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
        service = build("drive", "v3", credentials=creds)
        _log("✅ اتصال Drive ناجح")
        return service
    except Exception as e:
        _log(f"❌ خطأ اتصال: {e}")
        return None


def _get_or_create_folder(service, name: str, parent_id: str) -> str | None:
    try:
        q = (f"name='{name}' and mimeType='application/vnd.google-apps.folder' "
             f"and trashed=false and '{parent_id}' in parents")
        res = service.files().list(
            q=q,
            fields="files(id,name)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            corpora="drive",
            driveId=st.secrets["drive_folder_id"],
        ).execute()
        files = res.get("files", [])
        if files:
            _log(f"📁 مجلد موجود: {name}")
            return files[0]["id"]
        meta = {
            "name":     name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents":  [parent_id],
        }
        folder = service.files().create(
            body=meta,
            fields="id",
            supportsAllDrives=True,
        ).execute()
        fid = folder.get("id")
        _log(f"📁 مجلد جديد: {name} — {fid}")
        return fid
    except Exception as e:
        _log(f"❌ خطأ مجلد {name}: {e}")
        return None


def upload_all_from_session(username: str) -> dict:
    files = [
        (k, v) for k, v in st.session_state.items()
        if k.startswith("file_") and isinstance(v, dict) and v.get("content")
    ]
    _log(f"📊 ملفات في session: {len(files)}")

    if not files:
        _log("⚠️ لا توجد ملفات")
        return {}

    service = _get_service()
    if not service:
        return {}

    # نحاول قراءة drive_folder_id من مكانين محتملين
    root_id = ""
    try:
        root_id = str(st.secrets["drive_folder_id"]).strip()
    except Exception:
        pass
    if not root_id:
        try:
            root_id = str(st.secrets["google_credentials"]["drive_folder_id"]).strip()
        except Exception:
            pass
    if not root_id:
        _log("❌ drive_folder_id غير موجود — أضفه في Secrets خارج [google_credentials]")
        return {}
    _log(f"📂 Shared Drive ID: {root_id}")

    # مجلد المترشح داخل Shared Drive
    user_folder_id = _get_or_create_folder(service, username, root_id)
    if not user_folder_id:
        return {}

    saved = {}
    for key, val in files:
        try:
            skey     = key.replace("file_", "")
            label    = val.get("label", skey)   # الاسم الواضح
            content  = val["content"]
            ext      = val["name"].rsplit(".", 1)[-1] if "." in val["name"] else "pdf"
            filename = f"{username}_{label}.{ext}"
            mime     = val.get("mime", "application/pdf")
            doc_name = label

            _log(f"⬆️ رفع: {filename} ({len(content)//1024} KB)")

            media = MediaIoBaseUpload(io.BytesIO(content), mimetype=mime, resumable=False)
            meta  = {
                "name":    filename,
                "parents": [user_folder_id],
            }
            uploaded = service.files().create(
                body=meta,
                media_body=media,
                fields="id,webViewLink",
                supportsAllDrives=True,
            ).execute()

            link = uploaded.get("webViewLink", "")
            saved[doc_name] = link
            _log(f"✅ رُفع: {filename}")

            # صلاحية القراءة
            try:
                service.permissions().create(
                    fileId=uploaded["id"],
                    body={"type": "anyone", "role": "reader"},
                    supportsAllDrives=True,
                ).execute()
            except Exception:
                pass

        except Exception as e:
            _log(f"❌ فشل {val.get('name','?')}: {e}")

    _log(f"📊 مرفوعة: {len(saved)}/{len(files)}")
    return saved


def get_candidate_docs(username: str) -> list[dict]:
    """استرجاع وثائق مترشح من Drive"""
    service = _get_service()
    if not service:
        return []
    try:
        root_id = str(st.secrets["drive_folder_id"]).strip()
        # البحث عن مجلد المترشح
        q = (f"name='{username}' and mimeType='application/vnd.google-apps.folder' "
             f"and trashed=false and '{root_id}' in parents")
        res = service.files().list(
            q=q, fields="files(id)",
            supportsAllDrives=True, includeItemsFromAllDrives=True,
            corpora="drive", driveId=root_id,
        ).execute()
        folders = res.get("files", [])
        if not folders:
            return []
        folder_id = folders[0]["id"]

        # قائمة الملفات
        res2 = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id,name,mimeType,webViewLink,size)",
            supportsAllDrives=True, includeItemsFromAllDrives=True,
        ).execute()
        docs = []
        for f in res2.get("files", []):
            docs.append({
                "name":     f.get("name",""),
                "link":     f.get("webViewLink",""),
                "mime":     f.get("mimeType",""),
                "size_kb":  int(f.get("size",0)) // 1024,
                "file_id":  f.get("id",""),
            })
        return docs
    except Exception as e:
        _log(f"❌ خطأ استرجاع: {e}")
        return []
