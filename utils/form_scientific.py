"""
نموذج التقديم — سلم الإقامة العلمية قصيرة المدى
مشابه لسلم تربص تحسين المستوى مع فروق في النقاط وإضافات
"""
import streamlit as st, json
from datetime import datetime
from pathlib import Path

ARTICLE_PTS = {"A+": 20, "A": 15, "B": 10, "C (وطني)": 5}
INTERV_PTS  = {"دولية مفهرسة (Scopus/WOS)": 4, "دولية غير مفهرسة": 2, "وطنية": 1}
PROJECT_PTS = {"دولي (Erasmus+, PRIMA, Horizon...)": 10, "وطني (PNR, PRFU...)": 5}
SUPERV_PTS  = {"مشرف رئيسي": 5, "مشرف مشارك": 3, "عضو لجنة مناقشة": 1}
JURY_MAX    = 2


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
        <span class="badge b-blue">{st.session_state.user_name}</span>
        <span class="badge b-gold">{st.session_state.get('grade','')}</span>
        <span class="badge b-green">{st.session_state.get('department','') or st.session_state.get('position','')}</span>
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

def _score_line(label, pts, max_pts=None, neg=False):
    mx  = f"<small style='color:#6b7f96'> / {max_pts}</small>" if max_pts else ""
    col = "#e74c3c" if neg else "#1a3a5c"
    val = f"{pts:+.1f}" if neg else f"{pts:.1f}"
    st.markdown(f'<div class="score-row"><span>{label}</span>'
                f'<span style="font-weight:700;color:{col};">{val}{mx} ن</span></div>',
                unsafe_allow_html=True)


def _smart_upload(label, session_key, required=True):
    """رفع ملف ذكي — يحفظ المحتوى في session_state فور الرفع"""
    marker = " *" if required else " (اختياري)"
    f = st.file_uploader(f"📎 {label}{marker}",
                         type=["pdf","jpg","jpeg","png"],
                         key=f"uploader_{session_key}")
    if f is not None:
        st.session_state[f"file_{session_key}"] = {
            "name": f.name, "content": f.read(), "type": f.type,
        }
    has_file = f"file_{session_key}" in st.session_state
    if has_file:
        fname = st.session_state[f"file_{session_key}"]["name"]
        st.markdown(f'<div style="font-size:.78rem;color:#1a7a4a;margin-top:-6px;">✅ {fname}</div>',
                    unsafe_allow_html=True)
    elif required:
        st.markdown('<div style="font-size:.78rem;color:#e74c3c;margin-top:-6px;">⚠️ الوثيقة مطلوبة</div>',
                    unsafe_allow_html=True)
    return has_file


def _add_btn(key):
    _, c = st.columns([5,1])
    with c:
        return st.button("➕ إضافة", key=key, use_container_width=True)

def _del_btn(key):
    return st.button("🗑️", key=key, help="حذف")

def _item_pts(pts):
    st.markdown(f'<div style="font-weight:700;color:#1a3a5c;text-align:center;font-size:1rem;">{pts}ن</div>',
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════
def show_form():
    _header()

    for lst in ["sc_articles","sc_interventions","sc_projects",
                "sc_supervisions","sc_law1275","sc_labels",
                "sc_natl_studies","sc_intl_studies"]:
        if lst not in st.session_state:
            st.session_state[lst] = []

    scores = {}

    # ① الرتبة — اللجنة تحدد
    _sec("①", "الرتبة العلمية",
         "ارفع وثيقة <strong>آخر ترقية</strong> — اللجنة تحدد نقاطك (3–9 نقاط).")
    rank_doc = _smart_upload("وثيقة آخر ترقية في الرتبة", "sc_rank_doc", required=True)
    st.markdown('<div class="alert al-wn" style="font-size:.85rem;">⏳ نقاط الرتبة تُضاف من اللجنة بعد مراجعة الوثيقة.</div>',
                unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["① الرتبة العلمية"] = None

    # ② الاستفادات السابقة
    _sec("②", "الاستفادات السابقة (n − 3)")
    prev_n   = st.number_input("عدد الاستفادات السابقة (n)", 0, 15, 0, key="sc_prev")
    prev_pts = float(prev_n * -5)
    _score_line("نقاط / خصم الاستفادات", prev_pts, neg=(prev_pts < 0))
    st.markdown('</div>', unsafe_allow_html=True)
    scores["② الاستفادات السابقة"] = prev_pts

    # ③ جوائز — 10 نقاط (يختلف عن السلم ②)
    _sec("③", "جوائز دولية/وطنية مرتبطة بإنجازات علمية",
         "10 نقاط — وثيقة الجائزة إلزامية.")
    award_ok  = st.checkbox("حصلت على جائزة وطنية أو دولية — 10 نقطة", key="sc_award")
    award_doc = _smart_upload("وثيقة الجائزة أو شهادة التكريم", "sc_award_doc", required=award_ok) if award_ok else None
    award_pts = 10.0 if (award_ok and award_doc) else 0.0
    _score_line("نقاط الجوائز", award_pts, 10)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["③ الجوائز"] = award_pts

    # ④ مقالات — غير مسقَّفة ➕
    _sec("④", "المقالات العلمية المنشورة",
         "أضف مقالاً لكل ورقة منشورة. رابط DOI إلزامي.")
    if _add_btn("sc_add_art"):
        st.session_state.sc_articles.append({}); st.rerun()

    art_pts = 0.0; del_art = []
    for i, _ in enumerate(st.session_state.sc_articles):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"عنوان المقال {i+1} *", key=f"sc_art_title_{i}", placeholder="عنوان المقال")
            st.text_input(f"اسم المجلة {i+1}", key=f"sc_art_journal_{i}", placeholder="اسم المجلة")
        with c2:
            scope = st.selectbox("النطاق", ["دولي","وطني"], key=f"sc_art_scope_{i}")
            cats  = list(ARTICLE_PTS.keys()) if scope == "دولي" else ["C (وطني)"]
            cat   = st.selectbox("التصنيف", cats, key=f"sc_art_cat_{i}")
            st.text_input(f"رابط DOI *", key=f"sc_art_doi_{i}", placeholder="https://doi.org/...")
        with c3:
            f = st.file_uploader(f"📎 PDF", type=["pdf"], key=f"sc_art_pdf_{i}")
            if f: st.markdown('<div style="font-size:.75rem;color:#1a7a4a;">✅</div>', unsafe_allow_html=True)
            doi_val = st.session_state.get(f"sc_art_doi_{i}", "")
            pts = ARTICLE_PTS.get(cat, 0) if doi_val else 0
            _item_pts(pts)
            if _del_btn(f"sc_del_art_{i}"): del_art.append(i)
        art_pts += ARTICLE_PTS.get(cat,0) if st.session_state.get(f"sc_art_doi_{i}","") else 0
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_art): st.session_state.sc_articles.pop(i); st.rerun()
    _score_line("مجموع نقاط المقالات", art_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["④ المقالات"] = art_pts

    # ⑤ مداخلات — غير مسقَّفة ➕
    _sec("⑤", "المداخلات في المؤتمرات",
         "شهادة المشاركة <strong>إلزامية</strong> — بدونها لا تُحتسب النقاط.")
    if _add_btn("sc_add_int"):
        st.session_state.sc_interventions.append({}); st.rerun()

    int_pts = 0.0; del_int = []
    for i, _ in enumerate(st.session_state.sc_interventions):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"عنوان المداخلة {i+1} *", key=f"sc_int_title_{i}", placeholder="عنوان الورقة")
            st.text_input(f"اسم المؤتمر {i+1} *", key=f"sc_int_conf_{i}", placeholder="اسم المؤتمر")
        with c2:
            int_type = st.selectbox("نوع المداخلة", list(INTERV_PTS.keys()), key=f"sc_int_type_{i}")
            st.date_input("تاريخ المداخلة", key=f"sc_int_date_{i}")
        with c3:
            # cert = st.file_uploader(f"📎 شهادة *", type=["pdf","jpg","jpeg","png"], key=f"sc_int_cert_{i}")
            # auto
            st.markdown(f'<div style="font-size:.75rem;color:{"#1a7a4a" if has else "#e74c3c"};">{"✅" if has else "⚠️"}</div>',
                        unsafe_allow_html=True)
            pts  = INTERV_PTS.get(int_type, 0) if has else 0
            _item_pts(pts)
            if _del_btn(f"sc_del_int_{i}"): del_int.append(i)
            int_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_int): st.session_state.sc_interventions.pop(i); st.rerun()
    _score_line("مجموع نقاط المداخلات", int_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑤ المداخلات"] = int_pts

    # ⑥ مشاريع — غير مسقَّفة ➕
    _sec("⑥", "المشاريع البحثية",
         "وثيقة إثبات المشاركة إلزامية.")
    if _add_btn("sc_add_proj"):
        st.session_state.sc_projects.append({}); st.rerun()

    proj_pts = 0.0; del_proj = []
    for i, _ in enumerate(st.session_state.sc_projects):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"عنوان المشروع {i+1} *", key=f"sc_proj_title_{i}", placeholder="عنوان المشروع")
            st.text_input(f"رابط (اختياري)", key=f"sc_proj_url_{i}", placeholder="https://...")
        with c2:
            ptype = st.selectbox("نوع المشروع", list(PROJECT_PTS.keys()), key=f"sc_proj_type_{i}")
            st.date_input("تاريخ البداية", key=f"sc_proj_date_{i}")
        with c3:
            # cert = st.file_uploader(f"📎 وثيقة *", type=["pdf","jpg","jpeg","png"], key=f"sc_proj_cert_{i}")
            # auto
            st.markdown(f'<div style="font-size:.75rem;color:{"#1a7a4a" if has else "#e74c3c"};">{"✅" if has else "⚠️"}</div>',
                        unsafe_allow_html=True)
            pts  = PROJECT_PTS.get(ptype, 0) if has else 0
            _item_pts(pts)
            if _del_btn(f"sc_del_proj_{i}"): del_proj.append(i)
            proj_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_proj): st.session_state.sc_projects.pop(i); st.rerun()
    _score_line("مجموع نقاط المشاريع", proj_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑥ المشاريع"] = proj_pts

    # ⑦ إشراف دكتوراه — غير مسقَّف ➕
    _sec("⑦", "الإشراف على أطروحات الدكتوراه",
         "محضر المناقشة إلزامي. عضوية لجان المناقشة: حد أقصى <strong>2 نقطة</strong>.")
    if _add_btn("sc_add_sup"):
        st.session_state.sc_supervisions.append({}); st.rerun()

    sup_pts = 0.0; jury_count = 0; del_sup = []
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
            # cert = st.file_uploader(f"📎 محضر *", type=["pdf","jpg","jpeg","png"], key=f"sc_sup_cert_{i}")
            # auto
            st.markdown(f'<div style="font-size:.75rem;color:{"#1a7a4a" if has else "#e74c3c"};">{"✅" if has else "⚠️"}</div>',
                        unsafe_allow_html=True)
            if stype == "عضو لجنة مناقشة":
                jury_count += 1
                pts = SUPERV_PTS["عضو لجنة مناقشة"] if (has and jury_count <= JURY_MAX) else 0
                if jury_count > JURY_MAX:
                    st.markdown('<div style="font-size:.72rem;color:#e74c3c;">تجاوز الحد (2)</div>', unsafe_allow_html=True)
            else:
                pts = SUPERV_PTS.get(stype, 0) if has else 0
            _item_pts(pts)
            if _del_btn(f"sc_del_sup_{i}"): del_sup.append(i)
            sup_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_sup): st.session_state.sc_supervisions.pop(i); st.rerun()
    _score_line("مجموع نقاط الإشراف", sup_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑦ الإشراف على الدكتوراه"] = sup_pts

    # ⑧ الإشراف على طالب القرار 1275 — غير مسقَّف ➕ (حد 2 مشروع)
    _sec("⑧", "الإشراف على طلاب القرار الوزاري 1275",
         "2 نقطة / مشروع — <strong>حد أقصى 2 مشروع = 4 نقاط</strong>. وثيقة إثبات إلزامية.")
    if _add_btn("sc_add_law"):
        st.session_state.sc_law1275.append({}); st.rerun()

    law_pts = 0.0; del_law = []
    for i, _ in enumerate(st.session_state.sc_law1275):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"اسم الطالب {i+1}", key=f"sc_law_stud_{i}", placeholder="اسم الطالب")
            st.text_input(f"عنوان المشروع {i+1}", key=f"sc_law_title_{i}", placeholder="عنوان مشروع المذكرة")
        with c2:
            st.selectbox("نوع المؤسسة", ["مؤسسة ناشئة","مؤسسة مصغرة","براءة اختراع"], key=f"sc_law_type_{i}")
            st.date_input("تاريخ المناقشة", key=f"sc_law_date_{i}")
        with c3:
            # cert = st.file_uploader(f"📎 وثيقة *", type=["pdf","jpg","jpeg","png"], key=f"sc_law_cert_{i}")
            # auto
            st.markdown(f'<div style="font-size:.75rem;color:{"#1a7a4a" if has else "#e74c3c"};">{"✅" if has else "⚠️"}</div>',
                        unsafe_allow_html=True)
            pts = 2 if has else 0
            _item_pts(pts)
            if _del_btn(f"sc_del_law_{i}"): del_law.append(i)
            law_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_law): st.session_state.sc_law1275.pop(i); st.rerun()
    law_pts = min(law_pts, 4.0)
    _score_line("نقاط الإشراف على طلاب القرار 1275", law_pts, 4)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑧ الإشراف على طلاب القرار 1275"] = law_pts

    # ⑨ مشاريع حصلت على وسم لابل / مبتكر — غير مسقَّفة ➕ (حد 3 = 15 ن)
    _sec("⑨", "مشاريع حصلت على وسم لابل / مشروع مبتكر / مؤسسة ناشئة",
         "5 نقاط / مشروع — <strong>حد أقصى 3 مشاريع = 15 نقطة</strong>.")
    if _add_btn("sc_add_lbl"):
        st.session_state.sc_labels.append({}); st.rerun()

    lbl_pts = 0.0; del_lbl = []
    for i, _ in enumerate(st.session_state.sc_labels):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"عنوان المشروع {i+1} *", key=f"sc_lbl_title_{i}", placeholder="عنوان المشروع")
        with c2:
            st.selectbox("نوع الوسم", ["وسم لابل Label","مشروع مبتكر","مؤسسة ناشئة"], key=f"sc_lbl_type_{i}")
            st.date_input("تاريخ الحصول على الوسم", key=f"sc_lbl_date_{i}")
        with c3:
            # cert = st.file_uploader(f"📎 وثيقة الوسم *", type=["pdf","jpg","jpeg","png"], key=f"sc_lbl_cert_{i}")
            # auto
            st.markdown(f'<div style="font-size:.75rem;color:{"#1a7a4a" if has else "#e74c3c"};">{"✅" if has else "⚠️"}</div>',
                        unsafe_allow_html=True)
            pts = 5 if has else 0
            _item_pts(pts)
            if _del_btn(f"sc_del_lbl_{i}"): del_lbl.append(i)
            lbl_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_lbl): st.session_state.sc_labels.pop(i); st.rerun()
    lbl_pts = min(lbl_pts, 15.0)
    _score_line("نقاط مشاريع الوسم", lbl_pts, 15)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑨ مشاريع الوسم / المبتكر"] = lbl_pts

    # ⑩ تأطير ماستر / ليسانس — مسقَّف
    _sec("⑩", "تأطير مذكرات الماستر والليسانس",
         "ماستر: 1 نقطة / مذكرة (حد 3 ن) — ليسانس: 0.5 نقطة / موضوع (حد 3 ن).")
    c1, c2 = st.columns(2)
    with c1:
        master_n   = st.number_input("عدد مذكرات الماستر المُؤطَّرة", 0, 50, 0, key="sc_master")
        master_pts = min(master_n * 1.0, 3.0)
        _score_line("نقاط الماستر", master_pts, 3)
    with c2:
        lic_n   = st.number_input("عدد مواضيع الليسانس المُؤطَّرة", 0, 100, 0, key="sc_lic")
        lic_pts = min(lic_n * 0.5, 3.0)
        _score_line("نقاط الليسانس", lic_pts, 3)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑩ تأطير الماستر"]   = master_pts
    scores["⑩ تأطير الليسانس"] = lic_pts

    # ⑪ دراسات ذات بُعد وطني — غير مسقَّفة ➕ (حد 6 ن)
    _sec("⑪", "دراسات وخبرة ذات بُعد وطني",
         "2 نقطة / دراسة — <strong>حد أقصى 6 نقاط</strong>. تقرير الدراسة إلزامي.")
    if _add_btn("sc_add_natl"):
        st.session_state.sc_natl_studies.append({}); st.rerun()

    natl_pts = 0.0; del_natl = []
    for i, _ in enumerate(st.session_state.sc_natl_studies):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"عنوان الدراسة {i+1} *", key=f"sc_natl_title_{i}", placeholder="عنوان الدراسة أو التقرير")
        with c2:
            st.date_input("تاريخ الدراسة", key=f"sc_natl_date_{i}")
        with c3:
            # cert = st.file_uploader(f"📎 تقرير *", type=["pdf","jpg","jpeg","png"], key=f"sc_natl_cert_{i}")
            # auto
            st.markdown(f'<div style="font-size:.75rem;color:{"#1a7a4a" if has else "#e74c3c"};">{"✅" if has else "⚠️"}</div>',
                        unsafe_allow_html=True)
            pts = 2 if has else 0
            _item_pts(pts)
            if _del_btn(f"sc_del_natl_{i}"): del_natl.append(i)
            natl_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_natl): st.session_state.sc_natl_studies.pop(i); st.rerun()
    natl_pts = min(natl_pts, 6.0)
    _score_line("نقاط الدراسات الوطنية", natl_pts, 6)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑪ الدراسات الوطنية"] = natl_pts

    # ⑫ دراسات ذات بُعد دولي — غير مسقَّفة ➕ (حد 9 ن)
    _sec("⑫", "دراسات وخبرة ذات بُعد دولي",
         "3 نقاط / دراسة — <strong>حد أقصى 9 نقاط</strong>. تقرير الدراسة إلزامي.")
    if _add_btn("sc_add_intl"):
        st.session_state.sc_intl_studies.append({}); st.rerun()

    intl_pts = 0.0; del_intl = []
    for i, _ in enumerate(st.session_state.sc_intl_studies):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"عنوان الدراسة {i+1} *", key=f"sc_intl_title_{i}", placeholder="عنوان الدراسة الدولية")
            st.text_input(f"الجهة أو المنظمة", key=f"sc_intl_org_{i}", placeholder="اسم الجهة المنظمة")
        with c2:
            st.date_input("تاريخ الدراسة", key=f"sc_intl_date_{i}")
        with c3:
            # cert = st.file_uploader(f"📎 تقرير *", type=["pdf","jpg","jpeg","png"], key=f"sc_intl_cert_{i}")
            # auto
            st.markdown(f'<div style="font-size:.75rem;color:{"#1a7a4a" if has else "#e74c3c"};">{"✅" if has else "⚠️"}</div>',
                        unsafe_allow_html=True)
            pts = 3 if has else 0
            _item_pts(pts)
            if _del_btn(f"sc_del_intl_{i}"): del_intl.append(i)
            intl_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_intl): st.session_state.sc_intl_studies.pop(i); st.rerun()
    intl_pts = min(intl_pts, 9.0)
    _score_line("نقاط الدراسات الدولية", intl_pts, 9)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑫ الدراسات الدولية"] = intl_pts

    # ⑬ المنصب العالي — مسقَّف
    _sec("⑬", "المنصب العالي (هيكلي/وظيفي)")
    high_ok  = st.checkbox("أشغل منصباً عالياً — 2 نقطة", key="sc_high")
    high_pts = 2.0 if high_ok else 0.0
    _score_line("نقاط المنصب العالي", high_pts, 2)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑬ المنصب العالي"] = high_pts

    # ══ ملخص النقاط ══
    partial = sum(v for v in scores.values() if v is not None)

    st.markdown('<div class="card"><div class="card-title">🏆 ملخص النقاط</div>', unsafe_allow_html=True)
    for label, pts in scores.items():
        if pts is None:
            st.markdown(
                f'<div class="score-row"><span>{label}</span>'
                f'<span style="color:#c8973a;font-size:.82rem;">⏳ تُحدَّد من اللجنة (3–9 ن)</span></div>',
                unsafe_allow_html=True)
        else:
            neg = pts < 0
            col = "#e74c3c" if neg else "#1a3a5c"
            st.markdown(
                f'<div class="score-row"><span>{label}</span>'
                f'<span style="font-weight:700;color:{col};">{pts:+.1f} ن</span></div>',
                unsafe_allow_html=True)

    color = "#27ae60" if partial >= 35 else "#c8973a" if partial >= 18 else "#e74c3c"
    st.markdown(f"""
    <div class="total-box" style="margin-top:.8rem;">
      <div style="color:rgba(255,255,255,.65);font-size:.82rem;">مجموع النقاط الجزئية</div>
      <div class="total-num" style="color:{color};">{partial:.1f}</div>
      <div style="color:rgba(255,255,255,.5);font-size:.78rem;">+ نقاط الرتبة تُضاف من اللجنة (3–9 ن)</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── الإقرار والتقديم
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if not rank_doc:
        st.markdown('<div class="alert al-er">❌ لا يمكن التقديم بدون رفع وثيقة آخر ترقية.</div>',
                    unsafe_allow_html=True)
    decl = st.checkbox("أُقرّ بأن جميع المعلومات المُدرجة صحيحة وكاملة وأتحمل المسؤولية الكاملة.")
    if st.button("📤 تقديم الملف النهائي",
                 disabled=not (decl and rank_doc), use_container_width=True):
        _upload_and_save(partial, scores, "الإقامة العلمية قصيرة المدى")
    st.markdown('</div>', unsafe_allow_html=True)


def _upload_and_save(partial, scores, "الإقامة العلمية قصيرة المدى"):
    data = {
        "username":    st.session_state.username,
        "name":        st.session_state.user_name,
        "grade":       "مرفوعة — بانتظار اللجنة",
        "position":    st.session_state.get("department","") or st.session_state.get("position",""),
        "scale":       "الإقامة العلمية قصيرة المدى",
        "total_score": partial,
        "breakdown":   json.dumps(scores, ensure_ascii=False),
        "status":      "قيد المراجعة",
    }
    with st.spinner("⏳ جارٍ حفظ ملفك..."):
        saved = False
        try:
            from utils.sheets import save_application
            saved = save_application(data)
        except Exception:
            pass
        if not saved:
            Path("data/submissions").mkdir(parents=True, exist_ok=True)
            fname = f"data/submissions/{st.session_state.username}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            with open(fname,"w",encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    st.balloons()
    st.markdown(f"""
    <div class="alert al-ok">
      ✅ <strong>تم تقديم ملفك بنجاح!</strong><br>
      مجموع نقاطك الجزئية: <strong>{partial:.1f} نقطة</strong><br>
      ستُضاف نقاط الرتبة من اللجنة بعد مراجعة الوثيقة.
    </div>
    """, unsafe_allow_html=True)
