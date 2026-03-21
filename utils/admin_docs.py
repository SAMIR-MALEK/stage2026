"""الوثائق الإدارية — تحميل مباشر من static/ + رفع"""
import streamlit as st
from pathlib import Path
from utils._shared import smart_upload

# مسارات الملفات في مجلد static/
STATIC = Path("static")

FILES = {
    "1": STATIC / "1.docx",  # مشروع العمل
    "2": STATIC / "2.docx",  # التعهد
    "3": STATIC / "3.docx",  # استمارة ترشح صيغة 1
    "4": STATIC / "4.docx",  # استمارة ترشح صيغة 2
    "5": STATIC / "5.docx",  # استمارة ترشح صيغة 3
    "6": STATIC / "6.docx",  # استمارة ترشح صيغة 4
    "7": STATIC / "7.docx",  # التصريح الشرفي
}

FILE_NAMES = {
    "1": "نموذج_مشروع_العمل.docx",
    "2": "نموذج_التعهد.docx",
    "3": "استمارة_ترشح_صيغة1.docx",
    "4": "استمارة_ترشح_صيغة2.docx",
    "5": "استمارة_ترشح_صيغة3.docx",
    "6": "استمارة_ترشح_صيغة4.docx",
    "7": "نموذج_التصريح_الشرفي.docx",
}

# الوثائق المطلوبة لكل صيغة: (اسم_العرض, رقم_الملف, مفتاح_الرفع)
REQUIRED = {
    "form1": [
        ("استمارة الترشح",  "3", "adm_f1_istimara"),
        ("مشروع العمل",     "1", "adm_f1_mashrou3"),
        ("التعهد",          "2", "adm_f1_ta3ahod"),
    ],
    "form2": [
        ("استمارة الترشح",  "4", "adm_f2_istimara"),
        ("مشروع العمل",     "1", "adm_f2_mashrou3"),
        ("التعهد",          "2", "adm_f2_ta3ahod"),
    ],
    "form3": [
        ("استمارة الترشح",              "5", "adm_f3_istimara"),
        ("مشروع العمل",                 "1", "adm_f3_mashrou3"),
        ("التعهد",                      "2", "adm_f3_ta3ahod"),
        ("التصريح الشرفي (مصادق عليه)", "7", "adm_f3_tasrih"),
    ],
    "form4": [
        ("استمارة الترشح",  "6", "adm_f4_istimara"),
        ("مشروع العمل",     "1", "adm_f4_mashrou3"),
        ("التعهد",          "2", "adm_f4_ta3ahod"),
    ],
}

MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def show_admin_docs(form_key: str) -> bool:
    """عرض قسم الوثائق الإدارية — يعيد True إذا رُفعت كل الوثائق"""
    docs = REQUIRED.get(form_key, [])
    if not docs:
        return True

    st.markdown('<div class="card"><div class="card-title">📋 الوثائق الإدارية المطلوبة</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="alert al-in">
      <strong>① حمّل النموذج</strong> ← <strong>② املأه</strong> ← <strong>③ ارفعه</strong><br>
      <small>هذه الوثائق إلزامية ولا تدخل في حساب النقاط.</small>
    </div>
    """, unsafe_allow_html=True)

    all_ok = True
    for label, file_num, skey in docs:
        fpath     = FILES.get(file_num)
        fname     = FILE_NAMES.get(file_num, f"{file_num}.docx")

        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2 = st.columns([3, 3])

        with c1:
            st.markdown(f"**📄 {label}**")
            # زر تحميل مباشر من الملف المحلي
            if fpath and fpath.exists():
                with open(fpath, "rb") as f:
                    st.download_button(
                        label    = "⬇️ تحميل النموذج (.docx)",
                        data     = f.read(),
                        file_name= fname,
                        mime     = MIME,
                        key      = f"dl_{skey}",
                    )
            else:
                st.markdown(
                    f'<span style="color:#e74c3c;font-size:.8rem;">⚠️ الملف غير موجود: static/{file_num}.docx</span>',
                    unsafe_allow_html=True
                )

        with c2:
            has = smart_upload(f"رفع {label} بعد التعبئة", skey, required=True)
            if not has:
                all_ok = False

        st.markdown('</div>', unsafe_allow_html=True)

    if not all_ok:
        st.markdown('<div class="alert al-er">❌ يجب رفع جميع الوثائق الإدارية قبل التقديم.</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert al-ok">✅ جميع الوثائق الإدارية مرفوعة.</div>',
                    unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    return all_ok
