"""نموذج التقديم — صيغة 1: الإقامة العلمية قصيرة المدى (أساتذة محاضرون)"""
import streamlit as st
from utils.admin_docs import show_admin_docs
from utils._shared import smart_upload, score_line, item_pts, do_submit, show_submitted

SUBMITTED_KEY = "submitted_form1"
SCALE_NAME    = "الإقامة العلمية قصيرة المدى"

# نقاط المداخلات
INTERV_PTS = {
    "دولية مصنفة SCOPUS/WOS": 6,
    "دولية مفهرسة":            4,
    "دولية غير مصنفة":         2,
    "وطنية":                   1,
}
PROJECT_PTS = {
    "دولي (Erasmus+, PRIMA, Horizon...)": 10,
    "وطني (PNR, PRFU...)":               5,
}
SUPERV_PTS = {
    "مشرف رئيسي":          5,
    "مشرف مشارك":          3,
    "عضو لجنة مناقشة":     1,
}
REVIEW_PTS = {"A+": 5, "A": 4, "B": 2, "C": 1}
REVIEW_MAX  = {"A+": None, "A": 16, "B": 8, "C": 4}
COUNCIL_PTS = {"عضو":1, "رئيس هيئة":2, "مدير نشر/رئيس تحرير/عضو مختبر":1}

def _logout():
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

def _header():
    st.markdown(f"""
    <div class="gov-header">
      <div style="font-size:.74rem;opacity:.6;margin-bottom:.2rem;">
        الجمهورية الجزائرية الديمقراطية الشعبية — وزارة التعليم العالي والبحث العلمي
      </div>
      <h1>📋 طلب الانتقاء — الإقامة العلمية قصيرة المدى</h1>
      <p>كلية الحقوق والعلوم السياسية — جامعة محمد البشير الإبراهيمي برج بوعريريج</p>
      <div style="margin-top:.5rem;">
        <span class="badge b-blue">{st.session_state.get('user_name','')}</span>
        <span class="badge b-gold">{st.session_state.get('rank','')}</span>
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
        show_submitted(); return

    admin_docs_ok = show_admin_docs("form1")
    st.markdown("---")

    for lst in ["sc_articles","sc_interventions","sc_projects","sc_supervisions",
                "sc_law_proj","sc_label_proj","sc_reviews","sc_councils","sc_bodies"]:
        if lst not in st.session_state: st.session_state[lst] = []

    scores = {}

    # ① نقاط الرتبة
    RANK_S1 = {"أستاذ التعليم العالي":7.0, "أستاذ محاضر قسم أ":5.0, "أستاذ محاضر قسم ب":3.0}
    user_rank    = st.session_state.get("rank","")
    rank_pts_val = RANK_S1.get(user_rank, float(st.session_state.get("grade",0)))
    _sec("①", "نقاط الرتبة العلمية",
         f"رتبتك: <strong>{user_rank}</strong> — نقاطك: <strong>{rank_pts_val:.1f}</strong>")
    rank_ok = smart_upload("وثيقة آخر ترقية في الرتبة", "rank_doc", required=True)
    taheel_pts = 0.0
    if user_rank == "أستاذ محاضر قسم ب":
        st.markdown('<div class="alert al-in">إضافة 4 نقاط لتحضير ملف التأهيل الجامعي</div>', unsafe_allow_html=True)
        if st.checkbox("نعم، سأقوم بتحضير ملف التأهيل الجامعي — 4 نقاط", key="sc_taheel"):
            if smart_upload("تعهد بتحضير ملف التأهيل", "sc_taheel_doc", required=True):
                taheel_pts = 4.0
    rank_pts_input = rank_pts_val + taheel_pts
    score_line("نقاط الرتبة", rank_pts_input)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["① نقاط الرتبة"] = rank_pts_input

    # ② الاستفادات السابقة
    _sec("②", "الاستفادات السابقة", "الصيغة: 3 − n (حد أقصى 3 استفادات)")
    prev_n   = st.number_input("عدد الاستفادات في الثلاث سنوات الأخيرة", 0, 3, 0, key="sc_prev_f1")
    prev_pts = max(3.0 - prev_n, 0.0)
    score_line("نقاط الاستفادات", prev_pts, 3)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["② الاستفادات السابقة"] = prev_pts

    # ③ الجوائز وبراءات الاختراع — معيار واحد
    _sec("③", "الجوائز الدولية/الوطنية وبراءات الاختراع",
         "جوائز مرتبطة بإنجازات علمية أو براءة اختراع — 10 نقاط.")
    award_ok  = st.checkbox("حصلت على جائزة أو براءة اختراع — 10 نقاط", key="sc_award")
    award_pts = 0.0
    if award_ok:
        if smart_upload("وثيقة الجائزة أو شهادة براءة الاختراع", "sc_award_doc", required=True):
            award_pts = 10.0
        else:
            st.markdown('<div class="alert al-wn" style="font-size:.82rem;">⚠️ لن تُحتسب بدون وثيقة.</div>', unsafe_allow_html=True)
    score_line("نقاط الجوائز/براءات الاختراع", award_pts, 10)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["③ الجوائز وبراءات الاختراع"] = award_pts

    # ④ المقالات
    _sec("④", "المقالات العلمية المنشورة",
         "يجب تسمية المؤسسة في المقال. المقالات الوطنية: حد أقصى مقالان.")
    if _add_btn("sc_add_art"): st.session_state.sc_articles.append({}); st.rerun()
    art_pts = 0.0; c_pts = 0.0; del_art = []
    ARTICLE_PTS = {"A+":20, "A":15, "B":10, "C (وطني)":5}
    for i, _ in enumerate(st.session_state.sc_articles):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"عنوان المقال {i+1}", key=f"sc_art_title_{i}", placeholder="عنوان المقال")
            st.text_input(f"اسم المجلة {i+1}", key=f"sc_art_journal_{i}", placeholder="اسم المجلة")
        with c2:
            scope = st.selectbox("النطاق", ["دولي","وطني"], key=f"sc_art_scope_{i}")
            cats  = ["A+","A","B"] if scope=="دولي" else ["C (وطني)"]
            cat   = st.selectbox("التصنيف", cats, key=f"sc_art_cat_{i}")
            doi   = st.text_input(f"رابط DOI", key=f"sc_art_doi_{i}", placeholder="https://doi.org/...")
        with c3:
            smart_upload(f"PDF {i+1}", f"sc_art_pdf_{i}", required=False)
            pts = ARTICLE_PTS.get(cat,0) if doi else 0
            if cat == "C (وطني)":
                if c_pts >= 10:
                    pts = 0
                    st.markdown('<div style="font-size:.72rem;color:#e74c3c;">تجاوز الحد (مقالان)</div>', unsafe_allow_html=True)
                else:
                    c_pts += pts
            item_pts(pts)
            if st.button("🗑️", key=f"sc_del_art_{i}"): del_art.append(i)
        art_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_art): st.session_state.sc_articles.pop(i); st.rerun()
    score_line("مجموع نقاط المقالات", art_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["④ المقالات"] = art_pts

    # ⑤ المداخلات
    _sec("⑤", "المداخلات العلمية",
         "يجب تسمية المؤسسة. حد أقصى 4 مداخلات لكل فئة.")
    if _add_btn("sc_add_int"): st.session_state.sc_interventions.append({}); st.rerun()
    int_pts = 0.0; del_int = []
    int_counts = {}
    for i, _ in enumerate(st.session_state.sc_interventions):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"عنوان المداخلة {i+1}", key=f"sc_int_title_{i}", placeholder="عنوان الورقة")
            st.text_input(f"اسم المؤتمر {i+1}", key=f"sc_int_conf_{i}", placeholder="اسم المؤتمر")
        with c2:
            int_type = st.selectbox("نوع المداخلة", list(INTERV_PTS.keys()), key=f"sc_int_type_{i}")
            st.date_input("تاريخ المداخلة", key=f"sc_int_date_{i}")
        with c3:
            has = smart_upload(f"شهادة {i+1}", f"sc_int_cert_{i}", required=True)
            int_counts[int_type] = int_counts.get(int_type, 0) + 1
            if int_type != "دولية مصنفة SCOPUS/WOS" and int_counts[int_type] > 4:
                pts = 0
                st.markdown('<div style="font-size:.72rem;color:#e74c3c;">تجاوز الحد (4)</div>', unsafe_allow_html=True)
            else:
                pts = INTERV_PTS.get(int_type,0) if has else 0
            item_pts(pts)
            if st.button("🗑️", key=f"sc_del_int_{i}"): del_int.append(i)
            int_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_int): st.session_state.sc_interventions.pop(i); st.rerun()
    score_line("مجموع نقاط المداخلات", int_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑤ المداخلات"] = int_pts

    # ⑥ المشاريع البحثية
    _sec("⑥", "المشاريع البحثية", "وثيقة إثبات المشاركة إلزامية.")
    if _add_btn("sc_add_proj"): st.session_state.sc_projects.append({}); st.rerun()
    proj_pts = 0.0; del_proj = []
    for i, _ in enumerate(st.session_state.sc_projects):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"عنوان المشروع {i+1}", key=f"sc_proj_title_{i}", placeholder="عنوان المشروع")
        with c2:
            ptype = st.selectbox("نوع المشروع", list(PROJECT_PTS.keys()), key=f"sc_proj_type_{i}")
        with c3:
            has = smart_upload(f"وثيقة {i+1}", f"sc_proj_cert_{i}", required=True)
            pts = PROJECT_PTS.get(ptype,0) if has else 0
            item_pts(pts)
            if st.button("🗑️", key=f"sc_del_proj_{i}"): del_proj.append(i)
            proj_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_proj): st.session_state.sc_projects.pop(i); st.rerun()
    score_line("مجموع نقاط المشاريع", proj_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑥ المشاريع البحثية"] = proj_pts

    # ⑦ الإشراف على الدكتوراه
    _sec("⑦", "الإشراف على الدكتوراه", "محضر المناقشة إلزامي. لجان المناقشة: حد أقصى مناقشتان.")
    if _add_btn("sc_add_sup"): st.session_state.sc_supervisions.append({}); st.rerun()
    sup_pts = 0.0; jury_n = 0; del_sup = []
    for i, _ in enumerate(st.session_state.sc_supervisions):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"اسم الطالب {i+1}", key=f"sc_sup_stud_{i}", placeholder="اسم الطالب")
            st.text_input(f"عنوان الأطروحة {i+1}", key=f"sc_sup_thesis_{i}", placeholder="عنوان الأطروحة")
        with c2:
            stype = st.selectbox("الصفة", list(SUPERV_PTS.keys()), key=f"sc_sup_type_{i}")
            st.date_input("تاريخ المناقشة", key=f"sc_sup_date_{i}")
        with c3:
            has = smart_upload(f"محضر {i+1}", f"sc_sup_cert_{i}", required=True)
            if stype == "عضو لجنة مناقشة":
                jury_n += 1
                pts = SUPERV_PTS["عضو لجنة مناقشة"] if (has and jury_n <= 2) else 0
                if jury_n > 2: st.markdown('<div style="font-size:.72rem;color:#e74c3c;">تجاوز الحد (2)</div>', unsafe_allow_html=True)
            else:
                pts = SUPERV_PTS.get(stype,0) if has else 0
            item_pts(pts)
            if st.button("🗑️", key=f"sc_del_sup_{i}"): del_sup.append(i)
            sup_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_sup): st.session_state.sc_supervisions.pop(i); st.rerun()
    score_line("مجموع نقاط الإشراف", sup_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑦ الإشراف على الدكتوراه"] = sup_pts

    # ⑧ إشراف القرار 1275
    _sec("⑧", "الإشراف في إطار القرار الوزاري 1275/2022",
         "مشروع مذكرة تخرج / براءة اختراع — 2 نقطة (حد أقصى مشروعان).")
    if _add_btn("sc_add_law"): st.session_state.sc_law_proj.append({}); st.rerun()
    law_pts = 0.0; del_law = []
    for i, _ in enumerate(st.session_state.sc_law_proj):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"عنوان المشروع {i+1}", key=f"sc_law_title_{i}", placeholder="عنوان المشروع")
        with c2:
            st.date_input("تاريخ المناقشة", key=f"sc_law_date_{i}")
        with c3:
            has = smart_upload(f"وثيقة {i+1}", f"sc_law_cert_{i}", required=True)
            pts = 2.0 if (has and law_pts < 4.0) else 0
            if law_pts >= 4.0: st.markdown('<div style="font-size:.72rem;color:#e74c3c;">تجاوز الحد</div>', unsafe_allow_html=True)
            item_pts(pts)
            if st.button("🗑️", key=f"sc_del_law_{i}"): del_law.append(i)
            law_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_law): st.session_state.sc_law_proj.pop(i); st.rerun()
    law_pts = min(law_pts, 4.0)
    score_line("نقاط القرار 1275", law_pts, 4)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑧ الإشراف القرار 1275"] = law_pts

    # ⑨ وسم لابل/مبتكر/ناشئة
    _sec("⑨", "الإشراف على مشروع وسم لابل أو مبتكر أو ناشئة", "5 نقاط لكل مشروع.")
    if _add_btn("sc_add_lbl"): st.session_state.sc_label_proj.append({}); st.rerun()
    lbl_pts = 0.0; del_lbl = []
    for i, _ in enumerate(st.session_state.sc_label_proj):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"اسم المشروع {i+1}", key=f"sc_lbl_title_{i}", placeholder="اسم المشروع")
        with c2:
            lbl_type = st.selectbox("النوع", ["وسم لابل","مبتكر","ناشئة"], key=f"sc_lbl_type_{i}")
        with c3:
            has = smart_upload(f"وثيقة {i+1}", f"sc_lbl_cert_{i}", required=True)
            pts = 5.0 if has else 0
            item_pts(pts)
            if st.button("🗑️", key=f"sc_del_lbl_{i}"): del_lbl.append(i)
            lbl_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_lbl): st.session_state.sc_label_proj.pop(i); st.rerun()
    score_line("نقاط لابل/مبتكر/ناشئة", lbl_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑨ لابل/مبتكر/ناشئة"] = lbl_pts

    # ⑩ تأطير الماستر والليسانس والجذع المشترك
    _sec("⑩", "التأطير والتدريس", "ماستر: 1ن/مذكرة (حد 3) — ليسانس: 0.5ن/موضوع (حد 3) — جذع مشترك: 4ن.")
    c1, c2 = st.columns(2)
    with c1:
        master_n = st.number_input("عدد مذكرات الماستر", 0, 50, 0, key="sc_master_1")
        master_pts = 0.0
        if master_n > 0:
            if smart_upload("محاضر مناقشة الماستر (ملف واحد)", "sc_master_doc_1", required=True):
                master_pts = min(master_n * 1.0, 3.0)
        score_line("نقاط الماستر", master_pts, 3)
    with c2:
        lic_n = st.number_input("عدد مواضيع الليسانس", 0, 100, 0, key="sc_lic_1")
        lic_pts = 0.0
        if lic_n > 0:
            if smart_upload("وثيقة من رئيس القسم (ليسانس)", "sc_lic_doc_1", required=True):
                lic_pts = min(lic_n * 0.5, 3.0)
        score_line("نقاط الليسانس", lic_pts, 3)
    shared_ok = st.checkbox("التدريس في جذع مشترك — 4 نقاط", key="sc_shared_1")
    shared_pts = 0.0
    if shared_ok:
        if smart_upload("وثيقة إثبات التدريس في جذع مشترك", "sc_shared_doc_1", required=True):
            shared_pts = 4.0
    score_line("الجذع المشترك", shared_pts, 4)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑩ تأطير الماستر"]   = master_pts
    scores["⑩ تأطير الليسانس"] = lic_pts
    scores["⑩ الجذع المشترك"]   = shared_pts

    # ⑪ الخبرة التحكيمية
    _sec("⑪", "الخبرة التحكيمية في المجلات المصنفة",
         "A+→5ن | A→4ن (حد 16) | B→2ن (حد 8) | C→1ن (حد 4).")
    if _add_btn("sc_add_rev"): st.session_state.sc_reviews.append({}); st.rerun()
    rev_pts = 0.0; rev_counts = {}; del_rev = []
    for i, _ in enumerate(st.session_state.sc_reviews):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"اسم المجلة {i+1}", key=f"sc_rev_journal_{i}", placeholder="اسم المجلة")
        with c2:
            cat = st.selectbox("صنف المجلة", ["A+","A","B","C"], key=f"sc_rev_cat_{i}")
        with c3:
            has = smart_upload(f"إثبات {i+1}", f"sc_rev_cert_{i}", required=True)
            rev_counts[cat] = rev_counts.get(cat, 0) + REVIEW_PTS.get(cat,0)
            max_v = REVIEW_MAX.get(cat)
            if max_v and rev_counts[cat] > max_v:
                pts = 0
                st.markdown(f'<div style="font-size:.72rem;color:#e74c3c;">تجاوز الحد ({max_v}ن)</div>', unsafe_allow_html=True)
            else:
                pts = REVIEW_PTS.get(cat,0) if has else 0
            item_pts(pts)
            if st.button("🗑️", key=f"sc_del_rev_{i}"): del_rev.append(i)
            rev_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_rev): st.session_state.sc_reviews.pop(i); st.rerun()
    score_line("مجموع نقاط التحكيم", rev_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑪ الخبرة التحكيمية"] = rev_pts

    # ⑫ المطبوعات والكتب والدروس
    _sec("⑫", "المطبوعات والكتب والدروس الإلكترونية")
    pub_pts = 0.0
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**مطبوعة بيداغوجية (3ن)**")
        if st.checkbox("لدي مطبوعة بيداغوجية مصادق عليها", key="sc_pub"):
            if smart_upload("وثيقة المطبوعة", "sc_pub_doc", required=True):
                pub_pts += 3.0
                if st.checkbox("المطبوعة باللغة الإنجليزية (+2ن)", key="sc_pub_en"):
                    pub_pts += 2.0
                if st.checkbox("أدرّس بها (+2ن)", key="sc_pub_teach"):
                    pub_pts += 2.0
    with c2:
        st.markdown("**كتاب بيداغوجي/علمي ISBN (5ن)**")
        if st.checkbox("لدي كتاب برقم ISBN مصادق عليه", key="sc_book"):
            if smart_upload("وثيقة الكتاب", "sc_book_doc", required=True):
                pub_pts += 5.0
                if st.checkbox("الكتاب باللغة الإنجليزية (+2ن)", key="sc_book_en"):
                    pub_pts += 2.0
    st.markdown("**Chapterbook محكم دولي (5ن)**")
    if st.checkbox("لدي Chapterbook محكم في قاعدة بيانات دولية", key="sc_chapter"):
        if smart_upload("وثيقة Chapterbook", "sc_chapter_doc", required=True):
            pub_pts += 5.0
    st.markdown("**دروس e-Learning**")
    elearn_pts = 0.0
    c1,c2,c3 = st.columns(3)
    with c1:
        if st.checkbox("دروس (2ن)", key="sc_el_cours"):
            elearn_pts += 2.0
    with c2:
        if st.checkbox("أعمال موجهة (1ن)", key="sc_el_td"):
            elearn_pts += 1.0
    with c3:
        if st.checkbox("أعمال تطبيقية (1ن)", key="sc_el_tp"):
            elearn_pts += 1.0
    if elearn_pts > 0:
        if st.checkbox("الدروس باللغة الإنجليزية (+2ن)", key="sc_el_en"):
            elearn_pts += 2.0
        smart_upload("وثيقة إثبات e-Learning", "sc_elearn_doc", required=True)
    pub_pts += elearn_pts
    score_line("مجموع نقاط المطبوعات والكتب والدروس", pub_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑫ المطبوعات والكتب والدروس"] = pub_pts

    # ⑬ عضوية اللجان والمجالس
    _sec("⑬", "عضوية اللجان والمجالس العلمية",
         "1ن/عضوية (حد 3ن) — رئيس هيئة: 2ن — مدير نشر/رئيس تحرير/عضو مختبر: 1ن.")
    if _add_btn("sc_add_council"): st.session_state.sc_councils.append({}); st.rerun()
    council_pts = 0.0; member_total = 0.0; del_council = []
    for i, _ in enumerate(st.session_state.sc_councils):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"اسم اللجنة/المجلس {i+1}", key=f"sc_council_name_{i}", placeholder="المجلس العلمي...")
        with c2:
            ctype = st.selectbox("الصفة", list(COUNCIL_PTS.keys()), key=f"sc_council_type_{i}")
        with c3:
            has = smart_upload(f"وثيقة {i+1}", f"sc_council_cert_{i}", required=True)
            pts = COUNCIL_PTS.get(ctype,0) if has else 0
            if ctype == "عضو":
                if member_total + pts > 3.0:
                    pts = max(0, 3.0 - member_total)
                    st.markdown('<div style="font-size:.72rem;color:#e74c3c;">اقتراب من الحد (3ن)</div>', unsafe_allow_html=True)
                member_total += pts
            item_pts(pts)
            if st.button("🗑️", key=f"sc_del_council_{i}"): del_council.append(i)
            council_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_council): st.session_state.sc_councils.pop(i); st.rerun()
    score_line("مجموع نقاط اللجان والمجالس", council_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑬ عضوية اللجان والمجالس"] = council_pts

    # ⑭ هيئات المرافقة
    _sec("⑭", "هيئات المرافقة الجامعية",
         "CDC / CATI / حاضنة أعمال... — 1ن/شهادة — حد أقصى 2ن.")
    if _add_btn("sc_add_body"): st.session_state.sc_bodies.append({}); st.rerun()
    body_pts = 0.0; del_body = []
    for i, _ in enumerate(st.session_state.sc_bodies):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,3,1])
        with c1:
            st.text_input(f"اسم الهيئة {i+1}", key=f"sc_body_name_{i}", placeholder="CDC / CATI...")
        with c2:
            has = smart_upload(f"شهادة {i+1}", f"sc_body_cert_{i}", required=True)
            if has: body_pts += 1.0
        with c3:
            st.write("")
            if st.button("🗑️", key=f"sc_del_body_{i}"): del_body.append(i)
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_body): st.session_state.sc_bodies.pop(i); st.rerun()
    body_pts = min(body_pts, 2.0)
    score_line("نقاط هيئات المرافقة", body_pts, 2)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑭ هيئات المرافقة"] = body_pts

    # ⑮ المنصب العالي
    _sec("⑮", "المنصب العالي (هيكلي/وظيفي)", "2 نقطتان — وثيقة إثبات إلزامية.")
    high_ok = st.checkbox("أشغل منصباً عالياً — 2 نقطة", key="sc_high")
    high_pts = 0.0
    if high_ok:
        if smart_upload("وثيقة إثبات المنصب العالي", "sc_high_doc", required=True):
            high_pts = 2.0
    score_line("المنصب العالي", high_pts, 2)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑮ المنصب العالي"] = high_pts

    # ══ ملخص ══
    partial = sum(float(v) for v in scores.values() if v is not None)
    st.markdown('<div class="card"><div class="card-title">🏆 ملخص النقاط</div>', unsafe_allow_html=True)
    for label, pts in scores.items():
        col = "#e74c3c" if float(pts) < 0 else "#1a3a5c"
        st.markdown(f'<div class="score-row"><span>{label}</span><span style="font-weight:700;color:{col};">{float(pts):+.1f} ن</span></div>', unsafe_allow_html=True)
    color = "#27ae60" if partial >= 30 else "#c8973a" if partial >= 0 else "#e74c3c"
    st.markdown(f"""
    <div class="total-box" style="margin-top:.8rem;">
      <div style="color:rgba(255,255,255,.65);font-size:.82rem;">مجموع النقاط</div>
      <div class="total-num" style="color:{color};">{partial:.1f}</div>
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    if not rank_ok:
        st.markdown('<div class="alert al-er">❌ لا يمكن التقديم بدون رفع وثيقة الرتبة.</div>', unsafe_allow_html=True)
    decl = st.checkbox("أُقرّ بأن جميع المعلومات المُدرجة صحيحة وكاملة وأتحمل المسؤولية الكاملة.")
    if st.button("📤 تقديم الملف النهائي",
                 disabled=not (decl and rank_ok and admin_docs_ok),
                 use_container_width=True):
        do_submit(partial, scores, SCALE_NAME, SUBMITTED_KEY)
    st.markdown('</div>', unsafe_allow_html=True)
