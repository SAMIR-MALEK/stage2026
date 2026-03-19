import streamlit as st, pandas as pd, json, pathlib

def show_committee():
    st.markdown(f'<div class="gov-header"><h1>👥 لجنة الانتقاء</h1><p>كلية الحقوق والعلوم السياسية — جامعة برج بوعريريج</p><span class="badge b-gold">{st.session_state.user_name}</span></div>',unsafe_allow_html=True)
    c1,c2=st.columns([5,1])
    with c2:
        if st.button("🚪 خروج",use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()
    try:
        from utils.sheets import _get_client, SHEET_NAME
        cl=_get_client(); sh=cl.open(SHEET_NAME); recs=sh.sheet1.get_all_records()
        if recs:
            df=pd.DataFrame(recs); df=df.sort_values("النقاط_الإجمالية",ascending=False)
            df.insert(0,"الترتيب",range(1,len(df)+1))
            st.dataframe(df[["الترتيب","الاسم_الكامل","الرتبة_الوظيفية","المنصب","النقاط_الإجمالية","الحالة"]],use_container_width=True,hide_index=True)
        else: st.info("لا توجد طلبات بعد.")
    except Exception:
        subs=list(pathlib.Path("data/submissions").glob("*.json")) if pathlib.Path("data/submissions").exists() else []
        if subs:
            rows=[]
            for f in subs:
                with open(f) as fp: rows.append(json.load(fp))
            df=pd.DataFrame(rows).sort_values("total_score",ascending=False)
            df.insert(0,"الترتيب",range(1,len(df)+1))
            st.dataframe(df,use_container_width=True)
        else: st.info("لا توجد ملفات بعد.")
