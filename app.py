import streamlit as st

st.set_page_config(
    page_title="منصة الانتقاء | جامعة برج بوعريريج",
    page_icon="🎓", layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap');
*{font-family:'Tajawal',sans-serif!important;direction:rtl;}
[data-testid="stSidebar"],[data-testid="collapsedControl"],
#MainMenu,footer,header,.stDeployButton{display:none!important;}
.main .block-container{padding:1.5rem 2rem 3rem;max-width:960px;margin:auto;}
:root{--pr:#1a3a5c;--gd:#c8973a;--bd:#dce3ee;}
.gov-header{background:linear-gradient(135deg,#0d1f35,#1a3a5c,#2a5298);color:white;
  padding:1.4rem 2rem;border-radius:14px;margin-bottom:1.5rem;
  border-bottom:4px solid #c8973a;text-align:center;}
.gov-header h1{font-size:1.5rem;font-weight:800;margin:0;}
.gov-header p{font-size:.85rem;opacity:.8;margin:.3rem 0 0;}
.card{background:white;border-radius:12px;padding:1.3rem 1.5rem;
  box-shadow:0 2px 10px rgba(26,58,92,.07);border:1px solid var(--bd);margin-bottom:1rem;}
.card-title{font-size:1rem;font-weight:700;color:var(--pr);
  border-bottom:2px solid var(--gd);padding-bottom:.45rem;margin-bottom:1rem;}
.score-row{display:flex;justify-content:space-between;align-items:center;
  padding:.4rem .6rem;border-radius:6px;margin-bottom:4px;background:#f8f9fa;font-size:.92rem;}
.total-box{text-align:center;padding:1.4rem;border-radius:12px;margin-top:.5rem;
  background:linear-gradient(135deg,#0d1f35,#1a3a5c);}
.total-num{font-size:3rem;font-weight:800;}
.badge{display:inline-block;padding:2px 10px;border-radius:50px;font-size:.78rem;font-weight:600;margin:2px;}
.b-blue{background:#e6f1fb;color:#185fa5;}.b-gold{background:#fef9ec;color:#7d6010;}
.b-green{background:#e8f8f0;color:#1a7a4a;}.b-red{background:#fdecea;color:#a93226;}
.alert{padding:.85rem 1.1rem;border-radius:10px;margin:.7rem 0;font-size:.9rem;}
.al-ok{background:#e8f8f0;border:1.5px solid #27ae60;color:#1a7a4a;}
.al-er{background:#fdecea;border:1.5px solid #e74c3c;color:#a93226;}
.al-in{background:#e6f1fb;border:1.5px solid #378add;color:#185fa5;}
.al-wn{background:#fef9ec;border:1.5px solid #c8973a;color:#7d6010;}
.item-block{background:#f8fafd;border:1px solid var(--bd);border-radius:10px;
  padding:1rem 1.2rem;margin-bottom:.7rem;}
.stButton>button{background:linear-gradient(135deg,#1a3a5c,#2a5298)!important;
  color:white!important;border:none!important;border-radius:10px!important;
  font-weight:700!important;font-size:.95rem!important;}
</style>
""", unsafe_allow_html=True)

for k,v in {"logged_in":False,"role":None,"user_name":"","username":"",
             "grade":"","years":0,"position":"","scale":""}.items():
    if k not in st.session_state: st.session_state[k]=v

if not st.session_state.logged_in:
    from utils.login import show_login
    show_login()
else:
    role  = st.session_state.role
    scale = st.session_state.scale

    if role == "committee":
        from utils.committee import show_committee
        show_committee()

    elif role == "admin":
        from utils.admin import show_admin
        show_admin()

    elif role == "employee":
        # ── توجيه حسب السلم ──────────────────────────
        if scale == "الموظفون الإداريون والتقنيون":
            from utils.form_admin_staff import show_form
            show_form()

        elif scale == "تربص تحسين المستوى":
            from utils.form_training import show_form
            show_form()

        elif scale == "الإقامة العلمية قصيرة المدى":
            # قريباً
            st.markdown('<div class="gov-header"><h1>🔜 الإقامة العلمية قصيرة المدى</h1><p>هذا النموذج قيد الإعداد</p></div>',
                        unsafe_allow_html=True)

        elif scale == "الباحثون الدائمون":
            # قريباً
            st.markdown('<div class="gov-header"><h1>🔜 الباحثون الدائمون</h1><p>هذا النموذج قيد الإعداد</p></div>',
                        unsafe_allow_html=True)

        else:
            st.error(f"السلم '{scale}' غير معروف — تواصل مع الإدارة.")
