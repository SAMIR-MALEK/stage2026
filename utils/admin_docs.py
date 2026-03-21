"""
الوثائق الإدارية لكل صيغة
لا تدخل في التنقيط — فقط تحميل وملء ورفع
"""
import streamlit as st
from utils._shared import smart_upload

# روابط النماذج الفارغة
DOCS = {
    "مشروع_العمل":    "https://docs.google.com/document/d/1t6pA-dSzEVTXPBMRzdeuXRNXjKbBI8xL/edit?usp=drive_link&ouid=105750279229933306445&rtpof=true&sd=true",
    "التعهد":          "https://docs.google.com/document/d/1r_YndFUta_Qt-C-_vNJaDvJi519w5uvA/edit?usp=drive_link&ouid=105750279229933306445&rtpof=true&sd=true",
    "استمارة_ترشح_1":  "https://docs.google.com/document/d/13zjo2gqsrauXZkcNlbz3BIiosm5XBQn_/edit?usp=drive_link&ouid=105750279229933306445&rtpof=true&sd=true",
    "استمارة_ترشح_2":  "https://docs.google.com/document/d/19AuOB3FBoDjfZDRQx1YgdN51GOLM4aeB/edit?usp=drive_link&ouid=105750279229933306445&rtpof=true&sd=true",
    "استمارة_ترشح_3":  "https://docs.google.com/document/d/1vndTjhEYf-rIScWoYbgMRXwRE_Q6wUy2/edit?usp=drive_link&ouid=105750279229933306445&rtpof=true&sd=true",
    "استمارة_ترشح_4":  "https://docs.google.com/document/d/1I5XKoVZEM0P9xRcOWqupuk_5gzAd_Sak/edit?usp=drive_link&ouid=105750279229933306445&rtpof=true&sd=true",
    "التصريح_الشرفي":  "https://docs.google.com/document/d/1ERj0fSvlL9i8fxq8muD62D6NFtSK8S-S/edit?usp=drive_link&ouid=105750279229933306445&rtpof=true&sd=true",
}

# الوثائق المطلوبة لكل صيغة
REQUIRED_DOCS = {
    "form1": [  # أساتذة محاضرون
        ("استمارة الترشح",                    "استمارة_ترشح_1", "adm_f1_istimara"),
        ("مشروع العمل",                       "مشروع_العمل",    "adm_f1_mashrou3"),
        ("التعهد",                            "التعهد",         "adm_f1_ta3ahod"),
    ],
    "form2": [  # أساتذة مساعدون
        ("استمارة الترشح",                    "استمارة_ترشح_2", "adm_f2_istimara"),
        ("مشروع العمل",                       "مشروع_العمل",    "adm_f2_mashrou3"),
        ("التعهد",                            "التعهد",         "adm_f2_ta3ahod"),
    ],
    "form3": [  # طلبة دكتوراه
        ("استمارة الترشح",                    "استمارة_ترشح_3", "adm_f3_istimara"),
        ("مشروع العمل",                       "مشروع_العمل",    "adm_f3_mashrou3"),
        ("التعهد",                            "التعهد",         "adm_f3_ta3ahod"),
        ("التصريح الشرفي (مصادق عليه)",       "التصريح_الشرفي", "adm_f3_tasrih"),
    ],
    "form4": [  # إداريون وتقنيون
        ("استمارة الترشح",                    "استمارة_ترشح_4", "adm_f4_istimara"),
        ("مشروع العمل",                       "مشروع_العمل",    "adm_f4_mashrou3"),
        ("التعهد",                            "التعهد",         "adm_f4_ta3ahod"),
    ],
}


def show_admin_docs(form_key: str) -> bool:
    """
    عرض قسم الوثائق الإدارية
    يعيد True إذا رُفعت كل الوثائق الإلزامية
    """
    docs = REQUIRED_DOCS.get(form_key, [])
    if not docs:
        return True

    st.markdown("""
    <div class="card">
      <div class="card-title">📋 الوثائق الإدارية المطلوبة</div>
      <div class="alert al-in">
        ① حمّل كل نموذج &nbsp;→&nbsp; ② املأه &nbsp;→&nbsp; ③ ارفعه
        <br>
        <small>هذه الوثائق إلزامية للتقديم ولا تدخل في حساب النقاط.</small>
      </div>
    </div>
    """, unsafe_allow_html=True)

    all_uploaded = True

    for label, doc_key, skey in docs:
        link = DOCS.get(doc_key, "")
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3, 1.5, 2])
        with c1:
            st.markdown(f"**📄 {label}**")
        with c2:
            if link:
                st.link_button("⬇️ تحميل النموذج", link, use_container_width=True)
        with c3:
            has = smart_upload(f"رفع {label} بعد التعبئة", skey, required=True)
            if not has:
                all_uploaded = False
        st.markdown('</div>', unsafe_allow_html=True)

    if not all_uploaded:
        st.markdown("""
        <div class="alert al-er">
          ❌ يجب رفع جميع الوثائق الإدارية قبل التقديم.
        </div>
        """, unsafe_allow_html=True)

    return all_uploaded
