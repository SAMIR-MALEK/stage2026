"""نموذج التقديم — سلم التربصات قصيرة المدى للباحثين الدائمين"""
import streamlit as st
from utils._shared import smart_upload, score_line, item_pts, do_submit, show_submitted

ARTICLE_PTS = {"A+": 20, "A": 15, "B": 10, "C (وطني)": 5}
INTERV_PTS  = {"دولية مفهرسة (Scopus/WOS)": 4, "دولية غير مفهرسة": 2, "وطنية": 1}
PROJECT_PTS = {"دولي (Erasmus+, PRIMA, Horizon...)": 10, "وطني (PNR, PRFU...)": 5}
SUPERV_PTS  = {"مشرف رئيسي": 5, "مشرف مشارك": 3, "عضو لجنة مناقشة": 1}
SUBMITTED_KEY = "submitted_researcher"
SCALE_NAME    = "التربصات قصيرة المدى للباحثين الدائمين"


def _logout():
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

def _header():
    st.markdown(f"""
    <div class="gov-header">
      <div style="font-size:.74rem;opacity:.6;margin-bottom:.2rem;">
        الجمهورية الجزائرية الديمقراطية الشعبية — وزارة التعليم العالي والبحث العلمي
      </div>
      <h1>📋 طلب الانتقاء — التربصات قصيرة المدى للباحثين الدائمين</h1>
      <p>كلية الحقوق والعلوم السياسية — جامعة محمد البشير الإبراهيمي برج بوعريريج</p>
      <div style="margin-top:.5rem;">
        <span class="badge b-blue">{st.session_state.user_name}</span>
        <span class="badge b-gold">{st.session_state.get('grade','')}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    _, c2 = st.columns([5,1])
    with c2:
        if st.button("🚪 خروج", use_container_width=True): _logout()

def _sec(num, title, info=None):
    st.markdown(f'<div class="card"><div class="card-title">{num} {title}</div>', unsafe_allow_html=True)
    if info:
        st.markdown(f'<div class="alert al-in">{info}</div>', unsafe_allow_html=True)

def _add_btn(key):
    _, c = st.columns([5,1])
    with c:
        return st.button("➕ إضافة", key=key, use_container_width=True)


def show_form():
    _header()

    if st.session_state.get(SUBMITTED_KEY):
        show_submitted()
        return

    for lst in ["tr_articles","tr_interventions","tr_patents","tr_projects","tr_supervisions"]:
        if lst not in st.session_state: st.session_state[lst] = []

    scores = {}

    # ① الرتبة
    _sec("①", "الرتبة العلمية", "ارفع وثيقة آخر ترقية — اللجنة تحدد نقاطك (3–9 نقاط).")
    rank_ok = smart_upload("وثيقة آخر ترقية في الرتبة", "tr_rank", required=True)
    st.markdown('<div class="alert al-wn" style="font-size:.85rem;">⏳ نقاط الرتبة تُحدَّد من اللجنة.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["① الرتبة العلمية"] = None

    # ② التسجيل المنتظم
    _sec("②", "التسجيل المنتظم", "2 نقطة لكل سنة تسجيل.")
    c1, c2 = st.columns(2)
    with c1:
        reg = st.number_input("عدد سنوات التسجيل", 0, 10, 0, key="tr_reg")
    with c2:
        smart_upload("وثيقة التسجيل", "tr_reg_doc", required=reg > 0)
    reg_pts = reg * 2.0
    score_line("نقاط التسجيل", reg_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["② التسجيل المنتظم"] = reg_pts

    # ③ الاستفادات السابقة
    _sec("③", "الاستفادات السابقة", "يُخصم 5 نقاط لكل استفادة في آخر 6 سنوات.")
    prev_n   = st.number_input("عدد الاستفادات السابقة", 0, 15, 0, key="tr_prev")
    prev_pts = float(prev_n * -5)
    if prev_pts < 0:
        st.markdown(f'<div class="alert al-wn">سيُخصم: {abs(prev_pts):.0f} نقطة</div>', unsafe_allow_html=True)
    score_line("خصم الاستفادات", prev_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["③ الاستفادات السابقة"] = prev_pts

    # ④ الجوائز
    _sec("④", "الجوائز الوطنية والدولية", "5 نقاط — وثيقة إلزامية.")
    award_ok  = st.checkbox("حصلت على جائزة — 5 نقطة", key="tr_award")
    award_pts = 0.0
    if award_ok:
        if smart_upload("وثيقة الجائزة", "tr_award_doc", required=True):
            award_pts = 5.0
        else:
            st.markdown('<div class="alert al-wn" style="font-size:.82rem;">⚠️ لن تُحتسب بدون وثيقة.</div>', unsafe_allow_html=True)
    score_line("نقاط الجوائز", award_pts, 5)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["④ الجوائز"] = award_pts

    # ⑤ المقالات
    _sec("⑤", "المقالات العلمية المنشورة", "رابط DOI إلزامي لكل مقال.")
    if _add_btn("tr_add_art"): st.session_state.tr_articles.append({}); st.rerun()
    art_pts = 0.0; del_art = []
    for i, _ in enumerate(st.session_state.tr_articles):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"عنوان المقال {i+1}", key=f"tr_art_title_{i}", placeholder="عنوان المقال")
            st.text_input(f"اسم المجلة {i+1}", key=f"tr_art_journal_{i}", placeholder="اسم المجلة")
        with c2:
            scope = st.selectbox("النطاق", ["دولي","وطني"], key=f"tr_art_scope_{i}")
            cats  = list(ARTICLE_PTS.keys()) if scope == "دولي" else ["C (وطني)"]
            cat   = st.selectbox("التصنيف", cats, key=f"tr_art_cat_{i}")
            doi   = st.text_input(f"رابط DOI", key=f"tr_art_doi_{i}", placeholder="https://doi.org/...")
        with c3:
            smart_upload(f"PDF {i+1}", f"tr_art_pdf_{i}", required=False)
            pts = ARTICLE_PTS.get(cat, 0) if doi else 0
            item_pts(pts)
            if st.button("🗑️", key=f"tr_del_art_{i}"): del_art.append(i)
        art_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_art): st.session_state.tr_articles.pop(i); st.rerun()
    score_line("مجموع نقاط المقالات", art_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑤ المقالات"] = art_pts

    # ⑥ المداخلات
    _sec("⑥", "المداخلات في المؤتمرات", "شهادة المشاركة إلزامية.")
    if _add_btn("tr_add_int"): st.session_state.tr_interventions.append({}); st.rerun()
    int_pts = 0.0; del_int = []
    for i, _ in enumerate(st.session_state.tr_interventions):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"عنوان المداخلة {i+1}", key=f"tr_int_title_{i}", placeholder="عنوان الورقة")
            st.text_input(f"اسم المؤتمر {i+1}", key=f"tr_int_conf_{i}", placeholder="اسم المؤتمر")
        with c2:
            int_type = st.selectbox("نوع المداخلة", list(INTERV_PTS.keys()), key=f"tr_int_type_{i}")
            st.date_input("تاريخ المداخلة", key=f"tr_int_date_{i}")
        with c3:
            has = smart_upload(f"شهادة {i+1}", f"tr_int_cert_{i}", required=True)
            pts = INTERV_PTS.get(int_type, 0) if has else 0
            item_pts(pts)
            if st.button("🗑️", key=f"tr_del_int_{i}"): del_int.append(i)
            int_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_int): st.session_state.tr_interventions.pop(i); st.rerun()
    score_line("مجموع نقاط المداخلات", int_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑥ المداخلات"] = int_pts

    # ⑦ براءات الاختراع
    _sec("⑦", "براءات الاختراع", "15 نقطة / براءة — حد أقصى 45 نقطة.")
    if _add_btn("tr_add_pat"): st.session_state.tr_patents.append({}); st.rerun()
    pat_pts = 0.0; del_pat = []
    for i, _ in enumerate(st.session_state.tr_patents):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"عنوان البراءة {i+1}", key=f"tr_pat_title_{i}", placeholder="عنوان الاختراع")
            st.text_input(f"رقم البراءة", key=f"tr_pat_num_{i}", placeholder="رقم الشهادة")
        with c2:
            st.date_input("تاريخ الحصول", key=f"tr_pat_date_{i}")
        with c3:
            has = smart_upload(f"شهادة {i+1}", f"tr_pat_cert_{i}", required=True)
            pts = 15 if has else 0
            item_pts(pts)
            if st.button("🗑️", key=f"tr_del_pat_{i}"): del_pat.append(i)
            pat_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_pat): st.session_state.tr_patents.pop(i); st.rerun()
    pat_pts = min(pat_pts, 45.0)
    score_line("نقاط براءات الاختراع", pat_pts, 45)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑦ براءات الاختراع"] = pat_pts

    # ⑧ المشاريع
    _sec("⑧", "المشاريع البحثية", "وثيقة إثبات إلزامية.")
    if _add_btn("tr_add_proj"): st.session_state.tr_projects.append({}); st.rerun()
    proj_pts = 0.0; del_proj = []
    for i, _ in enumerate(st.session_state.tr_projects):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"عنوان المشروع {i+1}", key=f"tr_proj_title_{i}", placeholder="عنوان المشروع")
        with c2:
            ptype = st.selectbox("نوع المشروع", list(PROJECT_PTS.keys()), key=f"tr_proj_type_{i}")
            st.date_input("تاريخ البداية", key=f"tr_proj_date_{i}")
        with c3:
            has = smart_upload(f"وثيقة {i+1}", f"tr_proj_cert_{i}", required=True)
            pts = PROJECT_PTS.get(ptype, 0) if has else 0
            item_pts(pts)
            if st.button("🗑️", key=f"tr_del_proj_{i}"): del_proj.append(i)
            proj_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_proj): st.session_state.tr_projects.pop(i); st.rerun()
    score_line("مجموع نقاط المشاريع", proj_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑧ المشاريع"] = proj_pts

    # ⑨ الإشراف
    _sec("⑨", "الإشراف على الدكتوراه", "محضر المناقشة إلزامي.")
    if _add_btn("tr_add_sup"): st.session_state.tr_supervisions.append({}); st.rerun()
    sup_pts = 0.0; jury_n = 0; del_sup = []
    for i, _ in enumerate(st.session_state.tr_supervisions):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"اسم الطالب {i+1}", key=f"tr_sup_stud_{i}", placeholder="اسم الطالب")
            st.text_input(f"عنوان الأطروحة {i+1}", key=f"tr_sup_thesis_{i}", placeholder="عنوان الأطروحة")
        with c2:
            stype = st.selectbox("الصفة", list(SUPERV_PTS.keys()), key=f"tr_sup_type_{i}")
            st.date_input("تاريخ المناقشة", key=f"tr_sup_date_{i}")
        with c3:
            has = smart_upload(f"محضر {i+1}", f"tr_sup_cert_{i}", required=True)
            if stype == "عضو لجنة مناقشة":
                jury_n += 1
                pts = SUPERV_PTS["عضو لجنة مناقشة"] if (has and jury_n <= 2) else 0
                if jury_n > 2:
                    st.markdown('<div style="font-size:.72rem;color:#e74c3c;">تجاوز الحد (2)</div>', unsafe_allow_html=True)
            else:
                pts = SUPERV_PTS.get(stype, 0) if has else 0
            item_pts(pts)
            if st.button("🗑️", key=f"tr_del_sup_{i}"): del_sup.append(i)
            sup_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_sup): st.session_state.tr_supervisions.pop(i); st.rerun()
    score_line("مجموع نقاط الإشراف", sup_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑨ الإشراف على الدكتوراه"] = sup_pts

    # ⑩ تأطير الماستر والليسانس
    _sec("⑩", "تأطير الماستر والليسانس", "ماستر: 1 ن/مذكرة (حد 3) — ليسانس: 0.5 ن/موضوع (حد 3).")
    c1, c2 = st.columns(2)
    with c1:
        master_n   = st.number_input("عدد مذكرات الماستر", 0, 50, 0, key="tr_master")
        master_pts = min(master_n * 1.0, 3.0)
        score_line("نقاط الماستر", master_pts, 3)
    with c2:
        lic_n   = st.number_input("عدد مواضيع الليسانس", 0, 100, 0, key="tr_lic")
        lic_pts = min(lic_n * 0.5, 3.0)
        score_line("نقاط الليسانس", lic_pts, 3)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑩ تأطير الماستر"]   = master_pts
    scores["⑩ تأطير الليسانس"] = lic_pts

    # ⑪⑫ أنشطة إضافية
    _sec("⑪⑫", "أنشطة إضافية")
    c1, c2 = st.columns(2)
    with c1:
        high_ok  = st.checkbox("المنصب العالي — 2 نقطة", key="tr_high")
        high_pts = 0.0
        if high_ok:
            if smart_upload("وثيقة إثبات المنصب", "tr_high_doc", required=True):
                high_pts = 2.0
            else:
                st.markdown('<div class="alert al-wn" style="font-size:.82rem;">⚠️ لن تُحتسب بدون وثيقة.</div>', unsafe_allow_html=True)
        score_line("المنصب العالي", high_pts, 2)
    with c2:
        shared_ok  = st.checkbox("التدريس في جذع مشترك — 4 نقاط", key="tr_shared")
        shared_pts = 4.0 if shared_ok else 0.0
        score_line("الجذع المشترك", shared_pts, 4)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑪ المنصب العالي"]         = high_pts
    scores["⑫ التدريس في جذع مشترك"] = shared_pts

    # ══ ملخص ══
    partial = sum(v for v in scores.values() if v is not None)

    st.markdown('<div class="card"><div class="card-title">🏆 ملخص النقاط</div>', unsafe_allow_html=True)
    for label, pts in scores.items():
        if pts is None:
            st.markdown(f'<div class="score-row"><span>{label}</span><span style="color:#c8973a;font-size:.82rem;">⏳ اللجنة (3–9 ن)</span></div>', unsafe_allow_html=True)
        else:
            col = "#e74c3c" if pts < 0 else "#1a3a5c"
            st.markdown(f'<div class="score-row"><span>{label}</span><span style="font-weight:700;color:{col};">{pts:+.1f} ن</span></div>', unsafe_allow_html=True)

    color = "#27ae60" if partial >= 30 else "#c8973a" if partial >= 0 else "#e74c3c"
    st.markdown(f"""
    <div class="total-box" style="margin-top:.8rem;">
      <div style="color:rgba(255,255,255,.65);font-size:.82rem;">مجموع النقاط الجزئية</div>
      <div class="total-num" style="color:{color};">{partial:.1f}</div>
      <div style="color:rgba(255,255,255,.5);font-size:.78rem;">+ نقاط الرتبة تُضاف من اللجنة</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    if not rank_ok:
        st.markdown('<div class="alert al-er">❌ لا يمكن التقديم بدون رفع وثيقة آخر ترقية.</div>', unsafe_allow_html=True)
    decl = st.checkbox("أُقرّ بأن جميع المعلومات المُدرجة صحيحة وكاملة وأتحمل المسؤولية الكاملة.")
    if st.button("📤 تقديم الملف النهائي", disabled=not (decl and rank_ok), use_container_width=True):
        do_submit(partial, scores, SCALE_NAME, SUBMITTED_KEY)
    st.markdown('</div>', unsafe_allow_html=True)
