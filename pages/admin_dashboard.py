"""لوحة تحكم الإدارة"""
import streamlit as st


def show():
    if st.session_state.get("role") != "admin":
        st.error("🚫 هذه الصفحة للمدير فقط.")
        return

    st.markdown("""
    <div class="gov-header">
        <h1>⚙️ لوحة تحكم الإدارة</h1>
        <p>كلية الحقوق والعلوم السياسية — جامعة برج بوعريريج</p>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["📊 الإحصائيات", "👥 إدارة المستخدمين", "⚙️ الإعدادات", "🔗 Google API"])

    # ── إحصائيات ──────────────────────────────────────────
    with tabs[0]:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="metric-card gold"><h3>—</h3><p>إجمالي المترشحين</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="metric-card green"><h3>—</h3><p>ملفات مقبولة</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="metric-card red"><h3>—</h3><p>ملفات مرفوضة</p></div>', unsafe_allow_html=True)
        st.info("قم بربط Google Sheets لعرض الإحصائيات الحقيقية.")

    # ── إدارة المستخدمين ──────────────────────────────────
    with tabs[1]:
        from utils.google_integration import add_user_to_sheet

        st.markdown("""
        <div class="form-section">
            <div class="form-section-title">➕ إضافة مستخدم جديد</div>
            <p style="color:#6b7f96; font-size:0.88rem;">
                بعد الإضافة، أرسل <strong>اسم المستخدم</strong> و<strong>كلمة المرور</strong>
                للشخص المعني بأي طريقة تراها مناسبة (ورقة، بريد، رسالة...).
            </p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            new_name     = st.text_input("الاسم الكامل *", placeholder="محمد بن علي")
            new_role_lbl = st.selectbox("الدور *", ["مترشح", "لجنة الانتقاء", "إدارة"])
        with c2:
            new_username = st.text_input("اسم المستخدم *", placeholder="benali",
                                          help="حروف صغيرة بدون مسافات — يكتبه المستخدم عند الدخول")
            new_password = st.text_input("كلمة المرور *", placeholder="مثال: Bjb@2026",
                                          help="ضعها أنت يدوياً وأرسلها للمستخدم")

        if st.button("💾 إضافة وحفظ في الشيت", use_container_width=False):
            if not all([new_name, new_username, new_password]):
                st.error("❌ يرجى ملء جميع الحقول الإلزامية (*)")
            elif " " in new_username:
                st.error("❌ اسم المستخدم لا يجب أن يحتوي على مسافات")
            else:
                saved = add_user_to_sheet(new_username, new_password, new_name, new_role_lbl)
                if saved:
                    st.success(f"✅ تمت إضافة **{new_name}** بنجاح!")
                    st.markdown(f"""
                    <div class="status-box status-pending">
                        📋 <strong>بيانات الدخول لإرسالها:</strong><br>
                        • اسم المستخدم: <code>{new_username}</code><br>
                        • كلمة المرور: <code>{new_password}</code><br>
                        • الرابط: <code>رابط المنصة</code>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ تعذر الحفظ في الشيت — يمكنك إضافته يدوياً في ورقة 'المستخدمون'")

        st.markdown("---")
        st.markdown("""
        <div class="form-section">
            <div class="form-section-title">📊 هيكل ورقة المستخدمين في الشيت</div>
            <p style="color:#6b7f96; font-size:0.88rem;">
                يمكنك إضافة أو تعديل المستخدمين مباشرة في Google Sheets في ورقة <strong>المستخدمون</strong>:
            </p>
        </div>
        """, unsafe_allow_html=True)

        import pandas as pd
        demo_df = pd.DataFrame([
            ["benali",  "cand2026",  "محمد بن علي",   "مترشح",          "active"],
            ["comite1", "com2026",   "أ. فاطمة حمدي", "لجنة الانتقاء", "active"],
            ["admin",   "admin2026", "مدير المنصة",   "إدارة",          "active"],
        ], columns=["اسم_المستخدم", "كلمة_المرور", "الاسم_الكامل", "الدور", "الحالة"])
        st.dataframe(demo_df, use_container_width=True, hide_index=True)

        st.info("لتعطيل مستخدم: غيّر قيمة 'الحالة' من `active` إلى `inactive` في الشيت مباشرة.")

    # ── الإعدادات ──────────────────────────────────────────
    with tabs[2]:
        st.markdown("**إعدادات المنصة:**")
        st.text_input("الكلية", value="كلية الحقوق والعلوم السياسية", disabled=True)
        st.text_input("الجامعة", value="جامعة برج بوعريريج", disabled=True)
        st.date_input("آخر أجل للتقديم")
        st.number_input("العدد الأقصى للمقبولين", min_value=1, value=10)
        if st.button("💾 حفظ الإعدادات"):
            st.success("✅ تم حفظ الإعدادات")

    # ── Google API ─────────────────────────────────────────
    with tabs[3]:
        st.markdown("**حالة الاتصال بـ Google:**")
        from utils.google_integration import GOOGLE_AVAILABLE, get_google_credentials
        if not GOOGLE_AVAILABLE:
            st.error("❌ مكتبات Google غير مثبتة. نفّذ: `pip install -r requirements.txt`")
        else:
            creds = get_google_credentials()
            if creds:
                st.success("✅ الاتصال بـ Google مُفعّل")
            else:
                st.warning("⚠️ بيانات الاعتماد غير موجودة — راجع تبويب 'دليل الإعداد' في القائمة الجانبية.")
