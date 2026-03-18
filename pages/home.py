"""الصفحة الرئيسية"""
import streamlit as st
from datetime import datetime


def show():
    # ── Header ─────────────────────────────────────────────
    st.markdown("""
    <div class="gov-header">
        <div style="font-size:0.85rem; opacity:0.7; margin-bottom:0.3rem;">
            الجمهورية الجزائرية الديمقراطية الشعبية
        </div>
        <h1>🎓 منصة الانتقاء لبرنامج تحسين المستوى في الخارج</h1>
        <p>وزارة التعليم العالي والبحث العلمي</p>
        <div class="badge">القرار رقم 3/ك.ب/3 — المؤرخ في 09 مارس 2026</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Metrics ────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="metric-card gold">
            <h3>4</h3>
            <p>سلالم تقييم</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card green">
            <h3>📋</h3>
            <p>تقديم إلكتروني آمن</p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>☁️</h3>
            <p>حفظ على Google Drive</p>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-card red">
            <h3>🏆</h3>
            <p>ترتيب تلقائي للمترشحين</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Programme Description ──────────────────────────────
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("""
        <div class="form-section">
            <div class="form-section-title">📌 حول المنصة</div>
            <p style='color:#2a3a4a; line-height:2;'>
            تتيح هذه المنصة الإلكترونية للموظفين والأساتذة والباحثين التقدم لبرنامج 
            تحسين المستوى في الخارج وفق معايير القرار الوزاري المعتمد.
            يمكن للمترشح إدخال بياناته، حساب نقاطه تلقائياً، ورفع وثائقه مباشرة.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="form-section">
            <div class="form-section-title">📂 السلالم الأربعة للتقييم</div>
        """, unsafe_allow_html=True)

        scales = [
            ("1️⃣", "الموظفون الإداريون والتقنيون",
             "خاص بالموظفين الإداريين والتقنيين بالمؤسسات الجامعية والمدارس"),
            ("2️⃣", "الإقامة العلمية قصيرة المدى",
             "للأساتذة: مميز، محاضر أ/ب، مساعد — إقامة بحثية متخصصة"),
            ("3️⃣", "تربص تحسين المستوى",
             "للأساتذة والباحثين: تربص تأهيلي في الخارج"),
            ("4️⃣", "التربصات قصيرة المدى للباحثين الدائمين",
             "خاص بالباحثين المسجلين في الدكتوراه"),
        ]
        for icon, title, desc in scales:
            st.markdown(f"""
            <div style='display:flex;gap:0.8rem;align-items:flex-start;margin-bottom:0.8rem;
                        padding:0.8rem;background:#f4f7fb;border-radius:10px;'>
                <span style='font-size:1.5rem;'>{icon}</span>
                <div>
                    <strong style='color:#1a3a5c;'>{title}</strong>
                    <p style='margin:0;font-size:0.85rem;color:#6b7f96;'>{desc}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div class="form-section">
            <div class="form-section-title">🚀 كيفية التقديم</div>
        """, unsafe_allow_html=True)

        steps = [
            ("1", "إنشاء حساب أو تسجيل الدخول", "🔐"),
            ("2", "اختيار السلم المناسب لوضعيتك", "📋"),
            ("3", "إدخال بياناتك ومعاييرك", "✏️"),
            ("4", "رفع الوثائق المطلوبة", "📎"),
            ("5", "مراجعة نقاطك وتقديم الملف", "✅"),
            ("6", "متابعة حالة ملفك", "🔍"),
        ]
        for num, step, icon in steps:
            st.markdown(f"""
            <div style='display:flex;gap:0.8rem;align-items:center;margin-bottom:0.6rem;'>
                <div style='background:#1a3a5c;color:white;border-radius:50%;
                            width:28px;height:28px;display:flex;align-items:center;
                            justify-content:center;font-weight:700;font-size:0.85rem;
                            flex-shrink:0;'>{num}</div>
                <span style='font-size:0.95rem;color:#2a3a4a;'>{icon} {step}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Important Notes
        st.markdown("""
        <div class="form-section" style='border:2px solid #fef9ec; background:#fef9ec;'>
            <div class="form-section-title" style='color:#7d6010;'>⚠️ ملاحظات هامة</div>
            <ul style='color:#5a4510; font-size:0.9rem; line-height:2; padding-right:1.2rem;'>
                <li>لا يمكن أن يكون عضو لجنة الانتقاء مترشحاً</li>
                <li>يتم تنفيذ التربص قصير المدى حصراً في إطار الاتفاقيات الدولية المبرمة</li>
                <li>يجب أن يكون الرفض مبرراً</li>
                <li>المنشور الذي يظهر في Scopus و WOS معاً يُحسب مرة واحدة</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # ── Quick Action Buttons ───────────────────────────────
    st.markdown("---")
    st.markdown("<h3 style='text-align:center;color:#1a3a5c;'>ابدأ الآن</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📋 تقديم جديد", use_container_width=True):
            st.session_state.page = "form"
            st.rerun()
    with col2:
        if st.button("🔐 تسجيل الدخول", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
    with col3:
        if st.button("📖 دليل الإعداد", use_container_width=True):
            st.session_state.page = "setup"
            st.rerun()

    st.markdown("""
    <div class="app-version">
        النسخة 1.0 — 2026 | وزارة التعليم العالي والبحث العلمي
    </div>
    """, unsafe_allow_html=True)
