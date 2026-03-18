"""
صفحة الدخول
- اسم مستخدم + كلمة مرور تُعطى يدوياً لكل مستخدم
- التحقق يتم مباشرة من Google Sheets
- المؤسسة ثابتة: كلية الحقوق والعلوم السياسية — جامعة برج بوعريريج
"""
import streamlit as st
import sys
sys.path.insert(0, ".")
from utils.google_integration import verify_credentials

# أكواد تجريبية محلية (تعمل بدون Google Sheets)
DEMO_USERS = {
    ("admin",   "admin2026"):   {"name": "مدير المنصة",    "role": "admin"},
    ("comite1", "com2026"):     {"name": "أ. فاطمة حمدي",  "role": "committee"},
    ("benali",  "cand2026"):    {"name": "محمد بن علي",    "role": "candidate"},
    ("maamri",  "cand1234"):    {"name": "سارة معمري",     "role": "candidate"},
}

ROLE_AR = {
    "admin":     "إدارة",
    "committee": "لجنة الانتقاء",
    "candidate": "مترشح",
}


def show():
    st.markdown("""
    <div class="gov-header">
        <h1>🎓 منصة الانتقاء</h1>
        <p>كلية الحقوق والعلوم السياسية — جامعة برج بوعريريج</p>
        <div class="badge">برنامج تحسين المستوى في الخارج 2026</div>
    </div>
    """, unsafe_allow_html=True)

    # ── بطاقة الدخول مُركزة ───────────────────────────────
    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        st.markdown("""
        <div class="form-section" style="padding:2rem 1.8rem;">
            <div style="text-align:center; margin-bottom:1.5rem;">
                <div style="font-size:2.8rem;">🔐</div>
                <div style="font-size:1.1rem; font-weight:700; color:#1a3a5c;">تسجيل الدخول</div>
                <div style="font-size:0.82rem; color:#6b7f96; margin-top:0.3rem;">
                    أدخل بيانات الدخول التي سلّمتها لك الإدارة
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "اسم المستخدم",
                placeholder="مثال: benali",
                label_visibility="visible",
            )
            password = st.text_input(
                "كلمة المرور",
                type="password",
                placeholder="••••••••",
            )
            st.markdown("<div style='margin:0.4rem 0'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("دخول", use_container_width=True)

        if submitted:
            _do_login(username.strip(), password.strip())

        st.markdown("""
        <div style="text-align:center; margin-top:1.2rem;
                    color:#6b7f96; font-size:0.8rem; line-height:1.8;">
            لم تتلقَّ بيانات الدخول؟<br>
            تواصل مع إدارة الكلية
        </div>
        """, unsafe_allow_html=True)

        # تلميح تجريبي قابل للإخفاء
        with st.expander("🧪 بيانات تجريبية"):
            st.markdown("""
| اسم المستخدم | كلمة المرور | الدور |
|---|---|---|
| `admin` | `admin2026` | إدارة |
| `comite1` | `com2026` | لجنة |
| `benali` | `cand2026` | مترشح |
            """)


def _do_login(username: str, password: str):
    if not username or not password:
        st.error("يرجى إدخال اسم المستخدم وكلمة المرور.")
        return

    # 1️⃣ البحث في Google Sheets أولاً
    user = verify_credentials(username, password)

    # 2️⃣ إذا لم يتصل بـ Sheets بعد → الأكواد التجريبية
    if user is None:
        user = DEMO_USERS.get((username.lower(), password))

    if user is None:
        st.markdown("""
        <div class="status-box status-rejected">
            ❌ اسم المستخدم أو كلمة المرور غير صحيحة.<br>
            <small>تحقق من البيانات أو تواصل مع الإدارة.</small>
        </div>
        """, unsafe_allow_html=True)
        return

    if user.get("status", "active") != "active":
        st.markdown("""
        <div class="status-box status-rejected">
            🚫 هذا الحساب غير مفعّل. تواصل مع الإدارة.
        </div>
        """, unsafe_allow_html=True)
        return

    # ── حفظ الجلسة ───────────────────────────────────────
    st.session_state.role        = user["role"]
    st.session_state.user_name   = user["name"]
    st.session_state.username    = username
    st.session_state.institution = "كلية الحقوق والعلوم السياسية — جامعة برج بوعريريج"

    role_label = ROLE_AR.get(user["role"], "مستخدم")
    st.markdown(f"""
    <div class="status-box status-accepted">
        ✅ <strong>مرحباً {user['name']}</strong><br>
        الدور: <strong>{role_label}</strong>
    </div>
    """, unsafe_allow_html=True)

    import time; time.sleep(0.8)
    st.rerun()
