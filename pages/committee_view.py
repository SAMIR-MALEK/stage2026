"""لوحة لجنة الانتقاء"""
import streamlit as st
import pandas as pd
import json
from utils.google_integration import get_all_candidates, update_candidate_status

SCALES = [
    "الكل",
    "الموظفون الإداريون والتقنيون",
    "الإقامة العلمية قصيرة المدى",
    "تربص تحسين المستوى",
    "التربصات قصيرة المدى للباحثين الدائمين",
]

STATUS_OPTIONS = ["قيد المراجعة", "مقبول", "مرفوض", "قائمة الانتظار"]


def show():
    if st.session_state.get("role") not in ["committee", "admin"]:
        st.error("🚫 ليس لديك صلاحية الوصول إلى هذه الصفحة.")
        return

    st.markdown("""
    <div class="gov-header">
        <h1>👥 قائمة المترشحين</h1>
        <p>عرض وتقييم وترتيب المترشحين حسب النقاط</p>
    </div>
    """, unsafe_allow_html=True)

    # ── فلاتر ──────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        scale_filter = st.selectbox("تصفية حسب السلم:", SCALES)
    with col2:
        status_filter = st.selectbox("تصفية حسب الحالة:", ["الكل"] + STATUS_OPTIONS)
    with col3:
        search = st.text_input("🔍 بحث باللقب أو الاسم:")

    # ── تحميل البيانات ─────────────────────────────────────
    with st.spinner("جارٍ تحميل البيانات..."):
        sf = None if scale_filter == "الكل" else scale_filter
        candidates = get_all_candidates(sf)

    if not candidates:
        st.info("📭 لا توجد ملفات مترشحين بعد.")
        _show_demo_data()
        return

    df = pd.DataFrame(candidates)

    # تطبيق الفلاتر
    if status_filter != "الكل" and "الحالة" in df.columns:
        df = df[df["الحالة"] == status_filter]
    if search and "اللقب" in df.columns:
        mask = df["اللقب"].str.contains(search, case=False, na=False) | \
               df["الاسم"].str.contains(search, case=False, na=False)
        df = df[mask]

    # ترتيب حسب النقاط
    if "النقاط_الإجمالية" in df.columns:
        df["النقاط_الإجمالية"] = pd.to_numeric(df["النقاط_الإجمالية"], errors="coerce")
        df = df.sort_values("النقاط_الإجمالية", ascending=False)
        df.insert(0, "الترتيب", range(1, len(df) + 1))

    # ── إحصائيات سريعة ────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><h3>{len(df)}</h3><p>إجمالي المترشحين</p></div>', unsafe_allow_html=True)
    with col2:
        accepted = len(df[df.get("الحالة", pd.Series()) == "مقبول"]) if "الحالة" in df.columns else 0
        st.markdown(f'<div class="metric-card green"><h3>{accepted}</h3><p>مقبولون</p></div>', unsafe_allow_html=True)
    with col3:
        pending = len(df[df.get("الحالة", pd.Series()) == "قيد المراجعة"]) if "الحالة" in df.columns else len(df)
        st.markdown(f'<div class="metric-card gold"><h3>{pending}</h3><p>قيد المراجعة</p></div>', unsafe_allow_html=True)
    with col4:
        avg = df["النقاط_الإجمالية"].mean() if "النقاط_الإجمالية" in df.columns else 0
        st.markdown(f'<div class="metric-card"><h3>{avg:.1f}</h3><p>متوسط النقاط</p></div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── جدول المترشحين ────────────────────────────────────
    display_cols = [c for c in ["الترتيب", "رقم_الملف", "اللقب", "الاسم", "السلم",
                                 "المؤسسة", "النقاط_الإجمالية", "الحالة"] if c in df.columns]
    st.dataframe(df[display_cols], use_container_width=True, hide_index=True)

    # ── تحديث حالة مترشح ──────────────────────────────────
    if st.session_state.get("role") in ["committee", "admin"]:
        st.markdown("---")
        st.markdown("**تحديث حالة مترشح:**")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            file_num = st.text_input("رقم الملف")
        with c2:
            new_status = st.selectbox("الحالة الجديدة", STATUS_OPTIONS)
        with c3:
            notes = st.text_input("ملاحظات (اختياري)")
        with c4:
            st.write("")
            st.write("")
            if st.button("💾 حفظ التغيير"):
                if file_num:
                    ok = update_candidate_status(file_num, new_status, notes)
                    if ok:
                        st.success("✅ تم التحديث")
                    else:
                        st.error("❌ فشل التحديث")

    # ── تصدير Excel ───────────────────────────────────────
    st.markdown("---")
    if st.button("📥 تصدير القائمة (CSV)"):
        csv = df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            "⬇️ تحميل الملف",
            data=csv.encode("utf-8-sig"),
            file_name="قائمة_المترشحين.csv",
            mime="text/csv"
        )


def _show_demo_data():
    """بيانات تجريبية للعرض"""
    st.markdown("**📊 عرض تجريبي (بيانات نموذجية):**")
    demo = pd.DataFrame([
        {"الترتيب": 1, "اللقب": "بن علي", "الاسم": "محمد", "السلم": "تربص تحسين المستوى",
         "المؤسسة": "جامعة سطيف 1", "النقاط_الإجمالية": 87.5, "الحالة": "قيد المراجعة"},
        {"الترتيب": 2, "اللقب": "حمدي", "الاسم": "فاطمة", "السلم": "الإقامة العلمية قصيرة المدى",
         "المؤسسة": "جامعة قسنطينة 1", "النقاط_الإجمالية": 72.0, "الحالة": "قيد المراجعة"},
        {"الترتيب": 3, "اللقب": "معمر", "الاسم": "خالد", "السلم": "الموظفون الإداريون والتقنيون",
         "المؤسسة": "جامعة وهران 1", "النقاط_الإجمالية": 45.0, "الحالة": "قيد المراجعة"},
    ])
    st.dataframe(demo, use_container_width=True, hide_index=True)


def show_reports():
    """صفحة التقارير"""
    if st.session_state.get("role") not in ["committee", "admin"]:
        st.error("🚫 ليس لديك صلاحية الوصول.")
        return

    st.markdown("""
    <div class="gov-header">
        <h1>📊 التقارير والإحصائيات</h1>
    </div>
    """, unsafe_allow_html=True)

    candidates = get_all_candidates()
    if not candidates:
        st.info("لا توجد بيانات كافية لإنشاء التقارير.")
        return

    df = pd.DataFrame(candidates)
    if "النقاط_الإجمالية" in df.columns:
        df["النقاط_الإجمالية"] = pd.to_numeric(df["النقاط_الإجمالية"], errors="coerce")

    col1, col2 = st.columns(2)
    with col1:
        if "السلم" in df.columns:
            scale_counts = df["السلم"].value_counts()
            st.bar_chart(scale_counts)
            st.caption("توزيع المترشحين حسب السلم")
    with col2:
        if "النقاط_الإجمالية" in df.columns:
            st.bar_chart(df["النقاط_الإجمالية"].dropna())
            st.caption("توزيع النقاط")
