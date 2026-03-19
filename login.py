import streamlit as st
import pandas as pd
from pathlib import Path

USERS_FILE = Path("data/users.xlsx")

RANK_SCORES = {
    "الرتبة 10":8,"الرتبة 11":8.5,"الرتبة 12":9,"الرتبة 13":9.5,
    "الرتبة 14":10,"الرتبة 15":10.5,"الرتبة 16":11,"الرتبة 17":11.5,
    "أعلى من 17":12,
}

# بيانات تجريبية مدمجة
DEMO = {
    ("benali",   "Bjb@2026"): {"name":"محمد بن علي",   "role":"employee","grade":"الرتبة 14","years":8, "position":"مكلف بالمكتبة","scale":"الموظفون الإداريون والتقنيون"},
    ("maamri",   "Bjb@1234"): {"name":"سارة معمري",    "role":"employee","grade":"أستاذ محاضر أ","years":5, "position":"أستاذة محاضرة","scale":"تربص تحسين المستوى"},
    ("cherif",   "Bjb@5678"): {"name":"أحمد شريف",     "role":"employee","grade":"الرتبة 17","years":12,"position":"رئيس مصلحة الموارد","scale":"تربص تحسين المستوى"},
    ("comite1",  "Com@2026"): {"name":"لجنة الانتقاء", "role":"committee","grade":"الرتبة 17","years":15,"position":"رئيس اللجنة"},
    ("admin",    "Adm@2026"): {"name":"مدير المنصة",   "role":"admin",   "grade":"أعلى من 17","years":20,"position":"المدير"},
}

def _load_excel():
    if not USERS_FILE.exists():
        return {}
    try:
        df = pd.read_excel(USERS_FILE, sheet_name="المستخدمون", skiprows=1, dtype=str)
        df.columns = df.columns.str.strip()
        users = {}
        for _, r in df.iterrows():
            u = str(r.get("اسم_المستخدم","")).strip().lower()
            p = str(r.get("كلمة_المرور","")).strip()
            if not u or u=="nan": continue
            role_raw = str(r.get("الدور","")).strip()
            role = {"موظف":"employee","لجنة":"committee","إدارة":"admin"}.get(role_raw,"employee")
            status = str(r.get("الحالة","active")).strip().lower()
            try: years = int(float(str(r.get("سنوات_الخدمة","0"))))
            except: years = 0
            users[(u,p)] = {
                "name":    str(r.get("الاسم_الكامل",u)).strip(),
                "role":    role,
                "grade":   str(r.get("الرتبة_الوظيفية","")).strip(),
                "years":   years,
                "position":str(r.get("المنصب","")).strip(),
                "status":  status,
            }
        return users
    except Exception:
        return {}

def show_login():
    st.markdown("""
    <div class="gov-header">
      <div style="font-size:.75rem;opacity:.65;margin-bottom:.2rem;">
        الجمهورية الجزائرية الديمقراطية الشعبية — وزارة التعليم العالي والبحث العلمي
      </div>
      <h1>🎓 منصة الانتقاء لبرنامج تحسين المستوى في الخارج</h1>
      <p>كلية الحقوق والعلوم السياسية — جامعة محمد البشير الإبراهيمي برج بوعريريج</p>
      <div style="margin-top:.5rem;">
        <span class="badge b-gold">القرار رقم 3/ك.ب/3 — مارس 2026</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.3, 1])
    with col:
        st.markdown('<div class="card" style="padding:2rem 1.8rem;">', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center;margin-bottom:1.3rem;">
          <div style="font-size:2rem;">🔐</div>
          <div style="font-size:1.05rem;font-weight:700;color:#1a3a5c;">تسجيل الدخول</div>
          <div style="font-size:.8rem;color:#6b7f96;margin-top:.25rem;">
            أدخل بيانات الدخول التي سلّمتها لك إدارة الكلية
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("lf"):
            username = st.text_input("اسم المستخدم", placeholder="مثال: benali")
            password = st.text_input("كلمة المرور", type="password", placeholder="••••••••")
            ok = st.form_submit_button("دخول  ←", use_container_width=True)

        if ok:
            u, p = username.strip().lower(), password.strip()
            user = _load_excel().get((u,p)) or DEMO.get((u,p))
            if not user:
                st.markdown('<div class="alert al-er">❌ بيانات الدخول غير صحيحة.</div>', unsafe_allow_html=True)
            elif user.get("status","active") != "active":
                st.markdown('<div class="alert al-er">🚫 الحساب معطّل — تواصل مع الإدارة.</div>', unsafe_allow_html=True)
            else:
                st.session_state.logged_in = True
                st.session_state.role      = user["role"]
                st.session_state.user_name = user["name"]
                st.session_state.username  = u
                st.session_state.grade     = user["grade"]
                st.session_state.scale     = user.get("scale", "")
                st.session_state.years     = user["years"]
                st.session_state.scale     = user.get("scale","")
                st.session_state.position  = user["position"]
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
        with st.expander("🧪 أكواد تجريبية"):
            st.markdown("""
| اسم المستخدم | كلمة المرور | الدور |
|---|---|---|
| `benali` | `Bjb@2026` | موظف |
| `comite1` | `Com@2026` | لجنة |
| `admin` | `Adm@2026` | إدارة |
            """)
        st.markdown('<div style="text-align:center;color:#6b7f96;font-size:.77rem;margin-top:.6rem;">لم تتلقَّ بيانات الدخول؟ تواصل مع إدارة الكلية</div>', unsafe_allow_html=True)
