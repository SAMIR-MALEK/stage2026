"""
منصة الانتقاء لبرنامج تحسين المستوى في الخارج
وزارة التعليم العالي والبحث العلمي - الجمهورية الجزائرية الديمقراطية الشعبية
"""

import streamlit as st
from pathlib import Path

# ─── إعداد الصفحة ─────────────────────────────────────────
st.set_page_config(
    page_title="منصة الانتقاء | وزارة التعليم العالي",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── تحميل CSS المخصص ─────────────────────────────────────
def load_css():
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&family=Cairo:wght@300;400;600;700&display=swap');

    :root {
        --primary:   #1a3a5c;
        --secondary: #c8973a;
        --accent:    #2ecc71;
        --danger:    #e74c3c;
        --light:     #f4f7fb;
        --dark:      #0d1f35;
        --card-bg:   #ffffff;
        --border:    #dce3ee;
        --text:      #1a2a3a;
        --muted:     #6b7f96;
        --shadow:    0 4px 24px rgba(26,58,92,0.10);
    }

    * { font-family: 'Tajawal', 'Cairo', sans-serif !important; direction: rtl; }

    .main { background: var(--light); }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(160deg, var(--dark) 0%, var(--primary) 100%);
        border-left: 4px solid var(--secondary);
    }
    section[data-testid="stSidebar"] * { color: white !important; }
    section[data-testid="stSidebar"] .stRadio label { 
        font-size: 1.05rem; padding: 0.4rem 0.2rem; 
    }

    /* Header Banner */
    .gov-header {
        background: linear-gradient(135deg, var(--dark) 0%, var(--primary) 60%, #2a5298 100%);
        color: white;
        padding: 1.8rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        border-bottom: 4px solid var(--secondary);
        box-shadow: var(--shadow);
        text-align: center;
    }
    .gov-header h1 { font-size: 1.8rem; font-weight: 800; margin: 0; letter-spacing: -0.5px; }
    .gov-header p  { font-size: 1rem; opacity: 0.85; margin: 0.4rem 0 0; }
    .gov-header .badge {
        display: inline-block;
        background: var(--secondary);
        color: var(--dark);
        font-weight: 700;
        font-size: 0.8rem;
        padding: 0.2rem 0.8rem;
        border-radius: 50px;
        margin-top: 0.6rem;
    }

    /* Cards */
    .metric-card {
        background: var(--card-bg);
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        box-shadow: var(--shadow);
        border-right: 5px solid var(--primary);
        margin-bottom: 1rem;
    }
    .metric-card.gold  { border-right-color: var(--secondary); }
    .metric-card.green { border-right-color: var(--accent); }
    .metric-card.red   { border-right-color: var(--danger); }

    .metric-card h3 { font-size: 2rem; font-weight: 800; color: var(--primary); margin: 0; }
    .metric-card p  { font-size: 0.9rem; color: var(--muted); margin: 0.2rem 0 0; }

    /* Score Display */
    .score-display {
        background: linear-gradient(135deg, var(--primary), #2a5298);
        color: white;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(26,58,92,0.25);
    }
    .score-display .score-number { font-size: 4rem; font-weight: 800; color: var(--secondary); }
    .score-display .score-label  { font-size: 1rem; opacity: 0.8; }

    /* Form Sections */
    .form-section {
        background: white;
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 12px rgba(26,58,92,0.07);
        border: 1px solid var(--border);
    }
    .form-section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--primary);
        border-bottom: 2px solid var(--secondary);
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary), #2a5298) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 15px rgba(26,58,92,0.3) !important;
        transition: all 0.3s !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(26,58,92,0.4) !important;
    }

    /* Tables */
    .stDataFrame { border-radius: 12px; overflow: hidden; }

    /* Success/Warning/Error boxes */
    .status-box {
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 600;
    }
    .status-accepted { background:#e8f8f0; border:2px solid var(--accent); color:#1a7a4a; }
    .status-rejected { background:#fdecea; border:2px solid var(--danger); color:#a93226; }
    .status-pending  { background:#fef9ec; border:2px solid var(--secondary); color:#7d6010; }

    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--primary) !important;
        border-bottom: 3px solid var(--secondary) !important;
    }

    /* Input fields */
    .stTextInput input, .stSelectbox select, .stNumberInput input {
        border-radius: 8px !important;
        border: 1.5px solid var(--border) !important;
        font-family: 'Tajawal', sans-serif !important;
    }
    .stTextInput input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 2px rgba(26,58,92,0.1) !important;
    }

    /* Sidebar nav items */
    .nav-item {
        display: flex; align-items: center; gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.3rem;
        cursor: pointer;
        transition: background 0.2s;
    }
    .nav-item:hover { background: rgba(255,255,255,0.1); }
    .nav-item.active { background: rgba(200,151,58,0.3); }

    /* Progress bar */
    .progress-section {
        background: white;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        box-shadow: var(--shadow);
        margin-bottom: 1rem;
    }

    /* Divider */
    hr { border: none; border-top: 2px solid var(--border); margin: 1.5rem 0; }

    /* Hide Streamlit default elements */
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
    header    { visibility: hidden; }

    /* Watermark / signature */
    .app-version {
        text-align: center;
        color: var(--muted);
        font-size: 0.75rem;
        margin-top: 2rem;
        padding: 1rem;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

load_css()

# ─── Session State Initialization ────────────────────────
if "role" not in st.session_state:
    st.session_state.role = None
if "page" not in st.session_state:
    st.session_state.page = "home"
if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {}

# ─── Import pages ─────────────────────────────────────────
from pages import (
    home, login, candidate_form, my_scores,
    admin_dashboard, committee_view, setup_guide
)

# ─── Sidebar Navigation ───────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0;'>
        <div style='font-size:2.5rem;'>🎓</div>
        <div style='font-weight:800; font-size:1.1rem; color:white;'>منصة الانتقاء</div>
        <div style='font-size:0.75rem; opacity:0.7; color:white;'>وزارة التعليم العالي</div>
        <hr style='border-color:rgba(255,255,255,0.2); margin:0.8rem 0;'>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.role is None:
        page = st.radio(
            "القائمة",
            ["🏠 الرئيسية", "🔐 تسجيل الدخول", "📋 تقديم جديد", "📖 دليل الإعداد"],
            label_visibility="collapsed"
        )
    elif st.session_state.role == "candidate":
        page = st.radio(
            "القائمة",
            ["🏠 الرئيسية", "📋 نموذج التقديم", "📊 نقاطي", "🔓 خروج"],
            label_visibility="collapsed"
        )
    elif st.session_state.role == "committee":
        page = st.radio(
            "القائمة",
            ["🏠 الرئيسية", "👥 قائمة المترشحين", "📊 التقارير", "🔓 خروج"],
            label_visibility="collapsed"
        )
    elif st.session_state.role == "admin":
        page = st.radio(
            "القائمة",
            ["🏠 الرئيسية", "⚙️ لوحة التحكم", "👥 إدارة المترشحين", "📊 التقارير", "🔓 خروج"],
            label_visibility="collapsed"
        )

    st.markdown("---")
    st.markdown("""
    <div style='color:rgba(255,255,255,0.5); font-size:0.75rem; text-align:center;'>
        القرار رقم 3/ك.ب/3 المؤرخ في 09 مارس 2026
    </div>
    """, unsafe_allow_html=True)

# ─── Page Routing ─────────────────────────────────────────
if "خروج" in page:
    st.session_state.role = None
    st.session_state.candidate_data = {}
    st.rerun()

elif "الرئيسية" in page:
    home.show()

elif "تسجيل الدخول" in page:
    login.show()

elif "نموذج التقديم" in page or "تقديم جديد" in page:
    candidate_form.show()

elif "نقاطي" in page:
    my_scores.show()

elif "لوحة التحكم" in page:
    admin_dashboard.show()

elif "قائمة المترشحين" in page or "إدارة المترشحين" in page:
    committee_view.show()

elif "دليل الإعداد" in page:
    setup_guide.show()

elif "التقارير" in page:
    committee_view.show_reports()
