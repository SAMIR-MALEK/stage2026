"""صفحة نقاطي للمترشح"""
import streamlit as st
import json


def show():
    st.markdown("""
    <div class="gov-header">
        <h1>📊 نقاطي ووضعية ملفي</h1>
        <p>تتبع حالة ملفك ونقاطك في الوقت الفعلي</p>
    </div>
    """, unsafe_allow_html=True)

    name = st.session_state.get("user_name", "المترشح")

    if "last_score" not in st.session_state:
        st.markdown(f"""
        <div class="status-box status-pending">
            <strong>👋 مرحباً {name}</strong><br>
            لم تُقدّم ملفك بعد. اذهب إلى "نموذج التقديم" لتقديم ملفك.
        </div>
        """, unsafe_allow_html=True)
        if st.button("📋 تقديم ملف جديد", use_container_width=False):
            st.rerun()
        return

    score_data = st.session_state.get("last_score", {})
    total = score_data.get("total", 0)
    breakdown = score_data.get("breakdown", {})
    scale = score_data.get("scale", "")

    col1, col2 = st.columns([1, 2])
    with col1:
        color = "#2ecc71" if total >= 30 else "#c8973a" if total >= 15 else "#e74c3c"
        st.markdown(f"""
        <div class="score-display">
            <div class="score-label">السلم</div>
            <div style='font-size:0.9rem; margin:0.3rem 0;'>{scale}</div>
            <div class="score-label">مجموع النقاط</div>
            <div class="score-number" style='color:{color};'>{total:.1f}</div>
            <div class="score-label">نقطة</div>
        </div>
        <div class="status-box status-pending" style='margin-top:1rem; text-align:center;'>
            ⏳ <strong>قيد المراجعة</strong>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("**تفصيل النقاط:**")
        for criterion, pts in breakdown.items():
            icon = "✅" if pts > 0 else ("❌" if pts < 0 else "➖")
            color_pt = "green" if pts > 0 else ("red" if pts < 0 else "gray")
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;padding:0.4rem 0.5rem;"
                f"background:#f8f9fa;border-radius:6px;margin-bottom:4px;'>"
                f"<span>{icon} {criterion}</span>"
                f"<strong style='color:{color_pt};'>{pts:+.1f}</strong></div>",
                unsafe_allow_html=True
            )
