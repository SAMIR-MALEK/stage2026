"""تسجيل الدخول — منع التسجيل المزدوج بشكل صارم"""
import streamlit as st
import pandas as pd
from pathlib import Path

USERS_FILE = Path("data/users.xlsx")

SILK_TO_SUBMITTED = {
    "أساتذة محاضرون":  "submitted_form1",
    "أساتذة مساعدون":  "submitted_form2",
    "طلبة دكتوراه":    "submitted_form3",
    "إداريون وتقنيون": "submitted_form4",
}

_DEMO = {
    ("admin",    "Adm@2026"): {"name":"مدير المنصة",       "role":"admin",     "silk":"إداريون وتقنيون","rank":"مدير",                 "grade":1, "years":25,"status":"active"},
    ("comite1",  "Com@2026"): {"name":"لجنة الانتقاء",     "role":"committee", "silk":"أساتذة محاضرون", "rank":"أستاذ التعليم العالي", "grade":1, "years":20,"status":"active"},
    ("benali",   "Bjb@2026"): {"name":"أ.د. محمد بن علي",  "role":"employee",  "silk":"أساتذة محاضرون", "rank":"أستاذ التعليم العالي", "grade":1, "years":15,"status":"active"},
    ("maamri",   "Bjb@1234"): {"name":"أ. سارة معمري",     "role":"employee",  "silk":"أساتذة محاضرون", "rank":"أستاذ محاضر قسم أ",    "grade":2, "years":8, "status":"active"},
    ("cherif",   "Bjb@5678"): {"name":"أ. أحمد شريف",      "role":"employee",  "silk":"أساتذة مساعدون", "rank":"أستاذ مساعد قسم أ",    "grade":1, "years":4, "status":"active"},
    ("hamidi",   "Bjb@3456"): {"name":"كريم حميدي",        "role":"employee",  "silk":"طلبة دكتوراه",   "rank":"طالب دكتوراه",         "grade":1, "years":3, "status":"active"},
    ("ferhat",   "Bjb@1111"): {"name":"سليم فرحات",        "role":"employee",  "silk":"إداريون وتقنيون","rank":"مهندس رئيس",           "grade":12,"years":10,"status":"active"},
}


def _load_excel() -> dict:
    if not USERS_FILE.exists():
        return {}
    try:
        df = pd.read_excel(USERS_FILE, sheet_name="المستخدمون", skiprows=1, dtype=str)
        df.columns = df.columns.str.strip()
        users = {}
        for _, r in df.iterrows():
            u = str(r.get("اسم_المستخدم","")).strip().lower()
            p = str(r.get("كلمة_المرور","")).strip()
            if not u or u == "nan": continue
            role_raw = str(r.get("الدور","")).strip()
            role = {"مترشح":"employee","لجنة":"committee","إدارة":"admin"}.get(role_raw,"employee")
            status = str(r.get("الحالة","active")).strip().lower()
            try: years = int(float(str(r.get("سنوات_الخدمة","0"))))
            except: years = 0
            try: grade = int(float(str(r.get("الصنف","0"))))
            except: grade = 0
            users[(u,p)] = {
                "name":   str(r.get("الاسم_الكامل",u)).strip(),
                "role":   role,
                "silk":   str(r.get("السلك","")).strip(),
                "rank":   str(r.get("الرتبة","")).strip(),
                "grade":  grade,
                "years":  years,
                "status": status,
            }
        return users
    except Exception:
        return {}


def _check_submitted(username: str, silk: str):
    """
    تحقق صارم من Google Sheets أولاً ثم المحلي
    إذا وجد تقديماً سابقاً → يضع submitted_key ويحفظ البيانات
    """
    sub_key = SILK_TO_SUBMITTED.get(silk, "")
    if not sub_key:
        return

    # ① من Google Sheets — المصدر الرئيسي
    try:
        from utils.sheets import check_already_submitted
        record = check_already_submitted(username)
        if record:
            st.session_state[sub_key] = True
            st.session_state["submitted_data"] = {
                "total_score": float(record.get("النقاط_الكلية", record.get("النقاط_الجزئية", 0))),
                "breakdown":   str(record.get("تفصيل_النقاط","{}")),
                "drive_links": str(record.get("روابط_الوثائق","{}")),
            }
            return
    except Exception:
        pass

    # ② من الملفات المحلية
    sub_dir = Path("data/submissions")
    if sub_dir.exists():
        for f in sorted(sub_dir.glob(f"{username}_*.json"), reverse=True):
            try:
                import json
                with open(f, encoding="utf-8") as fp:
                    d = json.load(fp)
                st.session_state[sub_key] = True
                st.session_state["submitted_data"] = d
                return
            except Exception:
                pass


def show_login():
    st.markdown("""
    <div class="gov-header">
      <div style="font-size:.74rem;opacity:.6;margin-bottom:.2rem;">
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
            username = st.text_input("اسم المستخدم", placeholder="اسم المستخدم")
            password = st.text_input("كلمة المرور", type="password", placeholder="••••••••")
            ok = st.form_submit_button("دخول  ←", use_container_width=True)

        if ok:
            _handle(username.strip().lower(), password.strip())

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center;color:#6b7f96;font-size:.77rem;margin-top:.8rem;">
          لم تتلقَّ بيانات الدخول؟ تواصل مع إدارة الكلية
        </div>
        """, unsafe_allow_html=True)


def _handle(u: str, p: str):
    if not u or not p:
        st.markdown('<div class="alert al-er">❌ يرجى إدخال اسم المستخدم وكلمة المرور.</div>',
                    unsafe_allow_html=True)
        return

    user = _load_excel().get((u,p)) or _DEMO.get((u,p))

    if not user:
        st.markdown('<div class="alert al-er">❌ بيانات الدخول غير صحيحة.</div>',
                    unsafe_allow_html=True)
        return

    if user.get("status","active") != "active":
        st.markdown('<div class="alert al-er">🚫 الحساب معطّل — تواصل مع الإدارة.</div>',
                    unsafe_allow_html=True)
        return

    # حفظ الجلسة
    st.session_state.logged_in = True
    st.session_state.role      = user["role"]
    st.session_state.user_name = user["name"]
    st.session_state.username  = u
    st.session_state.silk      = user.get("silk","")
    st.session_state.rank      = user.get("rank","")
    st.session_state.grade     = user.get("grade", 0)
    st.session_state.years     = user.get("years", 0)
    # حساب نقاط الرتبة حسب السلك
    silk  = user.get("silk","")
    grade = int(user.get("grade", 0))
    rank  = user.get("rank","")
    
    if silk == "إداريون وتقنيون":
        # حسب الصنف
        GRADE_S4 = {10:8.0,11:8.5,12:9.0,13:9.5,14:10.0,15:10.5,16:11.0,17:11.5}
        rank_pts = GRADE_S4.get(grade, 12.0 if grade > 17 else 8.0)
    elif silk == "أساتذة محاضرون":
        # حسب الرتبة
        RANK_S1 = {"أستاذ التعليم العالي":7.0,"أستاذ محاضر قسم أ":5.0,"أستاذ محاضر قسم ب":3.0}
        rank_pts = RANK_S1.get(rank, float(grade))
    else:
        # صيغة 2 و3: لا توجد نقاط رتبة
        rank_pts = 0.0
    
    st.session_state.rank_pts = rank_pts

    # تحقق صارم من التقديم السابق قبل أي شيء
    if user["role"] == "employee":
        with st.spinner("جارٍ التحقق من حالة ملفك..."):
            _check_submitted(u, user.get("silk",""))

    st.rerun()
