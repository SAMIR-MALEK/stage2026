import streamlit as st, pandas as pd

def show_admin():
    st.markdown('<div class="gov-header"><h1>⚙️ لوحة الإدارة</h1><p>كلية الحقوق والعلوم السياسية — جامعة برج بوعريريج</p></div>',unsafe_allow_html=True)
    c1,c2=st.columns([5,1])
    with c2:
        if st.button("🚪 خروج",use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()
    t1,t2,t3=st.tabs(["📊 الطلبات","👥 المستخدمون","🔗 Google API"])
    with t1: st.info("يتطلب ربط Google Sheets — راجع التبويب الثالث.")
    with t2:
        st.markdown("**عدّل ملف `data/users.xlsx` لإضافة أو تعديل المستخدمين ثم أعد رفعه على GitHub.**")
        try:
            df=pd.read_excel("data/users.xlsx",sheet_name="المستخدمون",skiprows=1,dtype=str)
            st.dataframe(df,use_container_width=True,hide_index=True)
        except: st.warning("ملف المستخدمين غير موجود.")
    with t3:
        from utils.sheets import GOOGLE_OK,_get_client
        if not GOOGLE_OK: st.error("❌ `pip install -r requirements.txt`")
        else:
            c=_get_client()
            if c: st.success("✅ Google Sheets متصل")
            else: st.warning("⚠️ أضف بيانات الاعتماد في Streamlit Secrets — راجع ملف secrets.toml.example")
