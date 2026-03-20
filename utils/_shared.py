"""
دوال مشتركة بين جميع نماذج التقديم
"""
import streamlit as st
import json
import io
from datetime import datetime
from pathlib import Path


def smart_upload(label, skey, required=True):
    """رفع ملف ذكي — يحفظ المحتوى في session_state فور الرفع"""
    marker = " *" if required else " (اختياري)"
    uploaded = st.file_uploader(
        f"📎 {label}{marker}",
        type=["pdf", "jpg", "jpeg", "png"],
        key=f"uploader_{skey}"
    )
    if uploaded is not None:
        st.session_state[f"file_{skey}"] = {
            "name":    uploaded.name,
            "content": uploaded.read(),
            "mime":    uploaded.type,
        }
    has = f"file_{skey}" in st.session_state
    if has:
        fname = st.session_state[f"file_{skey}"]["name"]
        st.markdown(
            f'<div style="font-size:.78rem;color:#1a7a4a;margin-top:-6px;">✅ {fname}</div>',
            unsafe_allow_html=True)
    elif required:
        st.markdown(
            '<div style="font-size:.78rem;color:#e74c3c;margin-top:-6px;">⚠️ الوثيقة مطلوبة</div>',
            unsafe_allow_html=True)
    return has


def item_pts(pts):
    """عرض نقاط عنصر"""
    st.markdown(
        f'<div style="font-weight:700;color:#1a3a5c;text-align:center;font-size:1rem;">{pts}ن</div>',
        unsafe_allow_html=True)


def score_line(label, pts, max_pts=None):
    """عرض سطر نقاط"""
    mx  = f" / {max_pts}" if max_pts else ""
    col = "#e74c3c" if pts < 0 else "#1a3a5c"
    val = f"{pts:+.1f}" if pts < 0 else f"{pts:.1f}"
    st.markdown(
        f'<div class="score-row"><span>{label}</span>'
        f'<span style="font-weight:700;color:{col};">{val}{mx} ن</span></div>',
        unsafe_allow_html=True)


def do_submit(partial, scores, scale_name, submitted_key):
    """دالة التقديم الموحدة — ترفع الوثائق وتحفظ في Sheets"""
    with st.spinner("⏳ جارٍ رفع الوثائق وحفظ الملف..."):

        # رفع الوثائق على Drive
        drive_links = {}
        try:
            from utils.drive import upload_file
            username = st.session_state.username
            for key, val in st.session_state.items():
                if key.startswith("file_") and isinstance(val, dict) and "content" in val:
                    doc_name = key.replace("file_", "")
                    ext      = val["name"].rsplit(".", 1)[-1]
                    link = upload_file(
                        content   = val["content"],
                        filename  = f"{username}_{doc_name}.{ext}",
                        username  = username,
                        mime_type = val["mime"],
                    )
                    if link:
                        drive_links[doc_name] = link
        except Exception:
            pass

        # حفظ في Sheets
        data = {
            "username":    st.session_state.username,
            "name":        st.session_state.user_name,
            "grade":       "مرفوعة — بانتظار اللجنة",
            "position":    st.session_state.get("department", "") or st.session_state.get("position", ""),
            "scale":       scale_name,
            "total_score": partial,
            "breakdown":   json.dumps(scores, ensure_ascii=False),
            "drive_links": json.dumps(drive_links, ensure_ascii=False),
            "status":      "قيد المراجعة",
        }
        saved = False
        try:
            from utils.sheets import save_application
            saved = save_application(data)
        except Exception:
            pass
        if not saved:
            Path("data/submissions").mkdir(parents=True, exist_ok=True)
            fname = f"data/submissions/{st.session_state.username}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            with open(fname, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        st.session_state[submitted_key]    = True
        st.session_state["submitted_data"] = data

    st.rerun()


def show_submitted():
    """صفحة عرض الملف المقدَّم — بدون تعديل"""
    data = st.session_state.get("submitted_data", {})
    st.markdown(f"""
    <div class="alert al-ok">
      ✅ <strong>تم تقديم ملفك بنجاح — لا يمكن التعديل بعد التقديم.</strong><br>
      مجموع نقاطك الجزئية: <strong>{data.get('total_score', 0):.1f} نقطة</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-title">📋 ملخص ما قدّمته</div>',
                unsafe_allow_html=True)
    try:
        breakdown = json.loads(data.get("breakdown", "{}"))
        for label, pts in breakdown.items():
            if pts is None:
                st.markdown(
                    f'<div class="score-row"><span>{label}</span>'
                    f'<span style="color:#c8973a;">⏳ اللجنة</span></div>',
                    unsafe_allow_html=True)
            else:
                col = "#e74c3c" if float(pts) < 0 else "#1a3a5c"
                st.markdown(
                    f'<div class="score-row"><span>{label}</span>'
                    f'<span style="font-weight:700;color:{col};">{float(pts):+.1f} ن</span></div>',
                    unsafe_allow_html=True)
    except Exception:
        pass
    st.markdown('</div>', unsafe_allow_html=True)

    links = {}
    try:
        links = json.loads(data.get("drive_links", "{}"))
    except Exception:
        pass
    if links:
        st.markdown('<div class="card"><div class="card-title">📎 وثائقك على Google Drive</div>',
                    unsafe_allow_html=True)
        for name, link in links.items():
            st.markdown(f"• [{name}]({link})")
        st.markdown('</div>', unsafe_allow_html=True)
