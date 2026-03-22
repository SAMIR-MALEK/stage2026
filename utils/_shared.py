"""دوال مشتركة بين جميع نماذج التقديم"""
import streamlit as st

# قاموس أسماء الوثائق الواضحة
DOC_LABELS = {
    # سلم الموظفين
    "rank_doc":       "وثيقة_الرتبة_الوظيفية",
    "sen_doc":        "وثيقة_الخدمة",
    "lang_doc":       "وثيقة_لغة_التكوين",
    "eng_doc":        "شهادة_الإنجليزية",
    "min_doc":        "وثيقة_المشروع_الوزاري",
    "high_doc":       "وثيقة_المنصب_العالي",
    # سلم الأساتذة
    "tr_rank":        "وثيقة_الرتبة_العلمية",
    "tr_reg_doc":     "وثيقة_التسجيل",
    "tr_award_doc":   "وثيقة_الجائزة",
    "tr_high_doc":    "وثيقة_المنصب_العالي",
    # مقالات
    "tr_art_pdf_0":   "مقال_1",
    "tr_art_pdf_1":   "مقال_2",
    "tr_art_pdf_2":   "مقال_3",
    "sc_art_pdf_0":   "مقال_1",
    "sc_art_pdf_1":   "مقال_2",
    # مداخلات
    "tr_int_cert_0":  "شهادة_مداخلة_1",
    "tr_int_cert_1":  "شهادة_مداخلة_2",
    "tr_int_cert_2":  "شهادة_مداخلة_3",
    "sc_int_cert_0":  "شهادة_مداخلة_1",
    "sc_int_cert_1":  "شهادة_مداخلة_2",
    # براءات
    "tr_pat_cert_0":  "براءة_اختراع_1",
    "tr_pat_cert_1":  "براءة_اختراع_2",
    "sc_lbl_cert_0":  "وسم_مشروع_1",
    # مشاريع
    "tr_proj_cert_0": "وثيقة_مشروع_1",
    "tr_proj_cert_1": "وثيقة_مشروع_2",
    "sc_proj_cert_0": "وثيقة_مشروع_1",
    # إشراف
    "tr_sup_cert_0":  "محضر_دكتوراه_1",
    "tr_sup_cert_1":  "محضر_دكتوراه_2",
    "sc_sup_cert_0":  "محضر_دكتوراه_1",
    "sc_law_cert_0":  "وثيقة_قرار_1275_1",
    # دراسات
    "sc_natl_cert_0": "دراسة_وطنية_1",
    "sc_intl_cert_0": "دراسة_دولية_1",
    # هيئات
    "body_cert_0":    "شهادة_هيئة_1",
    "body_cert_1":    "شهادة_هيئة_2",
    "iproj_cert_0":   "شهادة_مشروع_دولي_1",
    # باحثون
    "rs_rank":        "وثيقة_الرتبة",
    "rs_phd_doc":     "وثيقة_تسجيل_دكتوراه",
    "rs_award_doc":   "وثيقة_الجائزة",
    "rs_pat_cert_0":  "براءة_اختراع_1",
    "rs_int_cert_0":  "شهادة_مداخلة_1",
    "rs_proj_cert_0": "وثيقة_مشروع_1",
    "rs_natl_cert_0": "دراسة_وطنية_1",
    "rs_intl_cert_0": "دراسة_دولية_1",
}

def get_doc_label(skey: str) -> str:
    """إعادة اسم واضح للوثيقة"""
    return DOC_LABELS.get(skey, skey.replace("_", " "))

import json
from datetime import datetime
from pathlib import Path


def smart_upload(label, skey, required=True):
    """رفع ذكي — يحفظ bytes في session_state فور الرفع"""
    marker   = " *" if required else " (اختياري)"
    uploaded = st.file_uploader(
        f"📎 {label}{marker}",
        type=["pdf", "jpg", "jpeg", "png"],
        key=f"uploader_{skey}"
    )
    if uploaded is not None:
        data = uploaded.read()
        st.session_state[f"file_{skey}"] = {
            "name":    uploaded.name,
            "label":   get_doc_label(skey),
            "content": data,
            "mime":    uploaded.type,
            "size":    len(data),
        }

    has = f"file_{skey}" in st.session_state and \
          bool(st.session_state[f"file_{skey}"].get("content"))

    if has:
        info = st.session_state[f"file_{skey}"]
        size_kb = info["size"] // 1024
        st.markdown(
            f'<div style="font-size:.78rem;color:#1a7a4a;margin-top:-6px;">'
            f'✅ {info["name"]} ({size_kb} KB)</div>',
            unsafe_allow_html=True)
    elif required:
        st.markdown(
            '<div style="font-size:.78rem;color:#e74c3c;margin-top:-6px;">'
            '⚠️ الوثيقة مطلوبة</div>',
            unsafe_allow_html=True)
    return has


def item_pts(pts):
    st.markdown(
        f'<div style="font-weight:700;color:#1a3a5c;text-align:center;font-size:1rem;">{pts}ن</div>',
        unsafe_allow_html=True)


def score_line(label, pts, max_pts=None):
    mx  = f" / {max_pts}" if max_pts else ""
    col = "#e74c3c" if pts < 0 else "#1a3a5c"
    val = f"{pts:+.1f}" if pts < 0 else f"{pts:.1f}"
    st.markdown(
        f'<div class="score-row"><span>{label}</span>'
        f'<span style="font-weight:700;color:{col};">{val}{mx} ن</span></div>',
        unsafe_allow_html=True)


def do_submit(partial, scores, scale_name, submitted_key):
    """التقديم: رفع الوثائق + حفظ في Sheets"""
    with st.spinner("⏳ جارٍ رفع الوثائق وحفظ الملف..."):

        # عد الملفات قبل الرفع
        files_in_session = [
            k for k, v in st.session_state.items()
            if k.startswith("file_") and isinstance(v, dict) and v.get("content")
        ]

        # رفع الوثائق
        drive_links = {}
        try:
            from utils.drive import upload_all_from_session
            drive_links = upload_all_from_session(st.session_state.username)
        except Exception as e:
            st.session_state.setdefault("drive_logs", []).append(f"❌ استثناء: {e}")

        # حفظ في Sheets
        data = {
            "username":    st.session_state.username,
            "name":        st.session_state.user_name,
            "grade":       "مرفوعة — بانتظار اللجنة",
            "position":    st.session_state.get('rank',''),
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
            with open(fname,"w",encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        st.session_state[submitted_key]    = True
        st.session_state["submitted_data"] = data
        st.session_state["files_submitted"] = len(files_in_session)
        st.session_state["files_uploaded"]  = len(drive_links)

    st.rerun()


def show_submitted():
    """عرض الملف المقدَّم بدون تعديل"""
    data       = st.session_state.get("submitted_data", {})
    drive_logs = st.session_state.get("drive_logs", [])

    total = 0.0
    try:
        total = float(data.get("total_score", 0))
    except Exception:
        pass

    st.markdown(f"""
    <div class="alert al-ok">
      ✅ <strong>تم تقديم ملفك بنجاح — لا يمكن التعديل بعد التقديم.</strong><br>
      مجموع نقاطك الجزئية: <strong>{total:.1f} نقطة</strong>
    </div>
    """, unsafe_allow_html=True)

    # تفصيل النقاط
    st.markdown('<div class="card"><div class="card-title">📋 ملخص ما قدّمته</div>', unsafe_allow_html=True)
    try:
        for label, pts in json.loads(data.get("breakdown","{}")).items():
            if pts is None:
                st.markdown(f'<div class="score-row"><span>{label}</span><span style="color:#c8973a;">⏳ اللجنة</span></div>', unsafe_allow_html=True)
            else:
                col = "#e74c3c" if float(pts) < 0 else "#1a3a5c"
                st.markdown(f'<div class="score-row"><span>{label}</span><span style="font-weight:700;color:{col};">{float(pts):+.1f} ن</span></div>', unsafe_allow_html=True)
    except Exception:
        pass
    st.markdown('</div>', unsafe_allow_html=True)

    # روابط Drive
    links = {}
    try: links = json.loads(data.get("drive_links","{}"))
    except Exception: pass
    if links:
        st.markdown('<div class="card"><div class="card-title">📎 وثائقك على Google Drive</div>', unsafe_allow_html=True)
        for name, link in links.items():
            st.markdown(f"• [{name}]({link})")
        st.markdown('</div>', unsafe_allow_html=True)


