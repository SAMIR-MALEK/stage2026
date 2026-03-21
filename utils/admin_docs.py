"""الوثائق الإدارية — تحميل وملء ورفع — لا تدخل في التنقيط"""
import streamlit as st
from utils._shared import smart_upload

DOCS = {
    "مشروع_العمل":   "https://docs.google.com/document/d/1t6pA-dSzEVTXPBMRzdeuXRNXjKbBI8xL/edit?usp=drive_link&ouid=105750279229933306445&rtpof=true&sd=true",
    "التعهد":         "https://docs.google.com/document/d/1r_YndFUta_Qt-C-_vNJaDvJi519w5uvA/edit?usp=drive_link&ouid=105750279229933306445&rtpof=true&sd=true",
    "استمارة_1":      "https://docs.google.com/document/d/13zjo2gqsrauXZkcNlbz3BIiosm5XBQn_/edit?usp=drive_link&ouid=105750279229933306445&rtpof=true&sd=true",
    "استمارة_2":      "https://docs.google.com/document/d/19AuOB3FBoDjfZDRQx1YgdN51GOLM4aeB/edit?usp=drive_link&ouid=105750279229933306445&rtpof=true&sd=true",
    "استمارة_3":      "https://docs.google.com/document/d/1vndTjhEYf-rIScWoYbgMRXwRE_Q6wUy2/edit?usp=drive_link&ouid=105750279229933306445&rtpof=true&sd=true",
    "استمارة_4":      "https://docs.google.com/document/d/1I5XKoVZEM0P9xRcOWqupuk_5gzAd_Sak/edit?usp=drive_link&ouid=105750279229933306445&rtpof=true&sd=true",
    "التصريح_الشرفي": "https://docs.google.com/document/d/1ERj0fSvlL9i8fxq8muD62D6NFtSK8S-S/edit?usp=drive_link&ouid=105750279229933306445&rtpof=true&sd=true",
}

# (اسم_الوثيقة, مفتاح_النموذج, مفتاح_الرفع)
REQUIRED = {
    "form1": [
        ("استمارة الترشح", "استمارة_1", "adm_f1_istimara"),
        ("مشروع العمل",    "مشروع_العمل","adm_f1_mashrou3"),
        ("التعهد",         "التعهد",     "adm_f1_ta3ahod"),
    ],
    "form2": [
        ("استمارة الترشح", "استمارة_2", "adm_f2_istimara"),
        ("مشروع العمل",    "مشروع_العمل","adm_f2_mashrou3"),
        ("التعهد",         "التعهد",     "adm_f2_ta3ahod"),
    ],
    "form3": [
        ("استمارة الترشح",            "استمارة_3",      "adm_f3_istimara"),
        ("مشروع العمل",               "مشروع_العمل",    "adm_f3_mashrou3"),
        ("التعهد",                    "التعهد",          "adm_f3_ta3ahod"),
        ("التصريح الشرفي (مصادق عليه)","التصريح_الشرفي","adm_f3_tasrih"),
    ],
    "form4": [
        ("استمارة الترشح", "استمارة_4", "adm_f4_istimara"),
        ("مشروع العمل",    "مشروع_العمل","adm_f4_mashrou3"),
        ("التعهد",         "التعهد",     "adm_f4_ta3ahod"),
    ],
}


def show_admin_docs(form_key: str) -> bool:
    """عرض قسم الوثائق الإدارية — يعيد True إذا رُفعت كل الوثائق"""
    docs = REQUIRED.get(form_key, [])
    if not docs:
        return True

    st.markdown('<div class="card"><div class="card-title">📋 الوثائق الإدارية المطلوبة</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="alert al-in">
      الخطوات: <strong>① حمّل النموذج</strong> ← <strong>② املأه</strong> ← <strong>③ ارفعه</strong><br>
      <small>هذه الوثائق إلزامية ولا تدخل في حساب النقاط.</small>
    </div>
    """, unsafe_allow_html=True)

    all_ok = True
    for label, doc_key, skey in docs:
        link = DOCS.get(doc_key, "")
        st.markdown(f'<div class="item-block">', unsafe_allow_html=True)
        c1, c2 = st.columns([3, 3])
        with c1:
            st.markdown(f"**📄 {label}**")
            if link:
                st.markdown(
                    f'<a href="{link}" target="_blank" style="'
                    f'display:inline-block;padding:5px 14px;background:#1a3a5c;color:white;'
                    f'border-radius:6px;font-size:.82rem;text-decoration:none;margin-top:4px;">'
                    f'⬇️ تحميل النموذج الفارغ</a>',
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
