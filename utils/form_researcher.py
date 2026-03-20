"""
نموذج التقديم — سلم التربصات قصيرة المدى للباحثين الدائمين
خاص بالباحثين المسجلين في الدكتوراه
"""
import streamlit as st, json
from datetime import datetime
from pathlib import Path

ARTICLE_PTS = {"A+": 20, "A": 15, "B": 10, "C (وطني)": 5}
INTERV_PTS  = {"دولية مفهرسة (Scopus/WOS)": 4, "دولية غير مفهرسة": 2, "وطنية": 1}
PROJECT_PTS = {"دولي (Erasmus+, PRIMA, Horizon...)": 10, "وطني (PNR, PRFU...)": 5}


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

    for lst in ["rs_articles","rs_interventions","rs_patents",
                "rs_projects","rs_natl_studies","rs_intl_studies"]:
        if lst not in st.session_state:
            st.session_state[lst] = []

    scores = {}

    # ① التسجيل في الدكتوراه — مسقَّف
    _sec("①", "التسجيل في الدكتوراه",
         "2 نقطة لكل سنة تسجيل — وثيقة التسجيل إلزامية.")
    c1, c2 = st.columns(2)
    with c1:
        phd_years = st.number_input("عدد سنوات التسجيل في الدكتوراه", 0, 10, 1, key="rs_phd_years")
        phd_pts   = phd_years * 2.0
        _score_line("نقاط التسجيل في الدكتوراه", phd_pts)
    with c2:
        phd_doc = _smart_upload("وثيقة التسجيل في الدكتوراه", "rs_phd_doc", required=True)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["① التسجيل في الدكتوراه"] = phd_pts if phd_doc else 0.0

    # ② الاستفادات السابقة
    _sec("②", "الاستفادات السابقة (n − 3)")
    prev_n   = st.number_input("عدد الاستفادات السابقة (n)", 0, 15, 0, key="rs_prev")
    prev_pts = float(prev_n * -5)
    _score_line("نقاط / خصم الاستفادات", prev_pts, neg=(prev_pts < 0))
    st.markdown('</div>', unsafe_allow_html=True)
    scores["② الاستفادات السابقة"] = prev_pts

    # ③ مشروع مؤسسة ناشئة في الحاضنة — مسقَّف
    _sec("③", "مشروع مؤسسة ناشئة في الحاضنة الجامعية",
         "1 نقطة — شهادة تسجيل المشروع في الحاضنة إلزامية.")
    incub_ok  = st.checkbox("لديّ مشروع مسجّل في الحاضنة الجامعية — 1 نقطة", key="rs_incub")
    incub_doc = _smart_upload("شهادة تسجيل المشروع في الحاضنة", "rs_incub_doc", required=incub_ok) if incub_ok else None
    incub_pts = 1.0 if (incub_ok and incub_doc) else 0.0
    _score_line("نقاط مشروع الحاضنة", incub_pts, 1)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["③ مشروع الحاضنة"] = incub_pts

    # ④ جوائز — 5 نقاط
    _sec("④", "جوائز وطنية/دولية مرتبطة بإنجازات علمية",
         "5 نقاط — وثيقة الجائزة إلزامية.")
    award_ok  = st.checkbox("حصلت على جائزة وطنية أو دولية — 5 نقطة", key="rs_award")
    award_doc = _smart_upload("وثيقة الجائزة أو شهادة التكريم", "rs_award_doc", required=award_ok) if award_ok else None
    award_pts = 5.0 if (award_ok and award_doc) else 0.0
    _score_line("نقاط الجوائز", award_pts, 5)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["④ الجوائز"] = award_pts

    # ⑤ مقالات علمية — غير مسقَّفة ➕
    _sec("⑤", "المقالات العلمية المنشورة",
         "أضف مقالاً لكل ورقة منشورة. رابط DOI إلزامي.")
    if _add_btn("rs_add_art"):
        st.session_state.rs_articles.append({}); st.rerun()

    art_pts = 0.0; del_art = []
    for i, _ in enumerate(st.session_state.rs_articles):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"عنوان المقال {i+1} *", key=f"rs_art_title_{i}", placeholder="عنوان المقال")
            st.text_input(f"اسم المجلة {i+1}", key=f"rs_art_journal_{i}", placeholder="اسم المجلة")
        with c2:
            scope = st.selectbox("النطاق", ["دولي","وطني"], key=f"rs_art_scope_{i}")
            cats  = list(ARTICLE_PTS.keys()) if scope == "دولي" else ["C (وطني)"]
            cat   = st.selectbox("التصنيف", cats, key=f"rs_art_cat_{i}")
            st.text_input(f"رابط DOI *", key=f"rs_art_doi_{i}", placeholder="https://doi.org/...")
        with c3:
            f = st.file_uploader(f"📎 PDF", type=["pdf"], key=f"rs_art_pdf_{i}")
            if f: st.markdown('<div style="font-size:.75rem;color:#1a7a4a;">✅</div>', unsafe_allow_html=True)
            doi_val = st.session_state.get(f"rs_art_doi_{i}","")
            pts = ARTICLE_PTS.get(cat,0) if doi_val else 0
            _item_pts(pts)
            if _del_btn(f"rs_del_art_{i}"): del_art.append(i)
        art_pts += ARTICLE_PTS.get(cat,0) if st.session_state.get(f"rs_art_doi_{i}","") else 0
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_art): st.session_state.rs_articles.pop(i); st.rerun()
    _score_line("مجموع نقاط المقالات", art_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑤ المقالات"] = art_pts

    # ⑥ مداخلات — غير مسقَّفة ➕
    _sec("⑥", "المداخلات في المؤتمرات",
         "شهادة المشاركة <strong>إلزامية</strong> — بدونها لا تُحتسب النقاط.")
    if _add_btn("rs_add_int"):
        st.session_state.rs_interventions.append({}); st.rerun()

    int_pts = 0.0; del_int = []
    for i, _ in enumerate(st.session_state.rs_interventions):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"عنوان المداخلة {i+1} *", key=f"rs_int_title_{i}", placeholder="عنوان الورقة")
            st.text_input(f"اسم المؤتمر {i+1} *", key=f"rs_int_conf_{i}", placeholder="اسم المؤتمر")
        with c2:
            int_type = st.selectbox("نوع المداخلة", list(INTERV_PTS.keys()), key=f"rs_int_type_{i}")
            st.date_input("تاريخ المداخلة", key=f"rs_int_date_{i}")
        with c3:
            # cert = st.file_uploader(f"📎 شهادة *", type=["pdf","jpg","jpeg","png"], key=f"rs_int_cert_{i}")
            # auto
            st.markdown(f'<div style="font-size:.75rem;color:{"#1a7a4a" if has else "#e74c3c"};">{"✅" if has else "⚠️"}</div>',
                        unsafe_allow_html=True)
            pts  = INTERV_PTS.get(int_type,0) if has else 0
            _item_pts(pts)
            if _del_btn(f"rs_del_int_{i}"): del_int.append(i)
            int_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_int): st.session_state.rs_interventions.pop(i); st.rerun()
    _score_line("مجموع نقاط المداخلات", int_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑥ المداخلات"] = int_pts

    # ⑦ براءات اختراع — غير مسقَّفة ➕ (حد 45 ن)
    _sec("⑦", "براءات الاختراع",
         "15 نقطة لكل براءة — <strong>حد أقصى 45 نقطة</strong>.")
    if _add_btn("rs_add_pat"):
        st.session_state.rs_patents.append({}); st.rerun()

    pat_pts = 0.0; del_pat = []
    for i, _ in enumerate(st.session_state.rs_patents):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"عنوان البراءة {i+1} *", key=f"rs_pat_title_{i}", placeholder="عنوان الاختراع")
            st.text_input(f"رقم البراءة", key=f"rs_pat_num_{i}", placeholder="رقم الشهادة")
        with c2:
            st.date_input("تاريخ الحصول", key=f"rs_pat_date_{i}")
            st.text_input(f"رابط (اختياري)", key=f"rs_pat_url_{i}", placeholder="https://...")
        with c3:
            # cert = st.file_uploader(f"📎 شهادة *", type=["pdf","jpg","jpeg","png"], key=f"rs_pat_cert_{i}")
            # auto
            st.markdown(f'<div style="font-size:.75rem;color:{"#1a7a4a" if has else "#e74c3c"};">{"✅" if has else "⚠️"}</div>',
                        unsafe_allow_html=True)
            pts  = 15 if has else 0
            _item_pts(pts)
            if _del_btn(f"rs_del_pat_{i}"): del_pat.append(i)
            pat_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_pat): st.session_state.rs_patents.pop(i); st.rerun()
    pat_pts = min(pat_pts, 45.0)
    _score_line("مجموع نقاط براءات الاختراع", pat_pts, 45)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑦ براءات الاختراع"] = pat_pts

    # ⑧ مشاريع بحثية — غير مسقَّفة ➕
    _sec("⑧", "المشاريع البحثية",
         "وثيقة إثبات المشاركة إلزامية.")
    if _add_btn("rs_add_proj"):
        st.session_state.rs_projects.append({}); st.rerun()

    proj_pts = 0.0; del_proj = []
    for i, _ in enumerate(st.session_state.rs_projects):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"عنوان المشروع {i+1} *", key=f"rs_proj_title_{i}", placeholder="عنوان المشروع")
            st.text_input(f"رابط (اختياري)", key=f"rs_proj_url_{i}", placeholder="https://...")
        with c2:
            ptype = st.selectbox("نوع المشروع", list(PROJECT_PTS.keys()), key=f"rs_proj_type_{i}")
            st.date_input("تاريخ البداية", key=f"rs_proj_date_{i}")
        with c3:
            # cert = st.file_uploader(f"📎 وثيقة *", type=["pdf","jpg","jpeg","png"], key=f"rs_proj_cert_{i}")
            # auto
            st.markdown(f'<div style="font-size:.75rem;color:{"#1a7a4a" if has else "#e74c3c"};">{"✅" if has else "⚠️"}</div>',
                        unsafe_allow_html=True)
            pts  = PROJECT_PTS.get(ptype,0) if has else 0
            _item_pts(pts)
            if _del_btn(f"rs_del_proj_{i}"): del_proj.append(i)
            proj_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_proj): st.session_state.rs_projects.pop(i); st.rerun()
    _score_line("مجموع نقاط المشاريع", proj_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑧ المشاريع"] = proj_pts

    # ⑨ دراسات وطنية — غير مسقَّفة ➕ (حد 6 ن)
    _sec("⑨", "دراسات وخبرة ذات بُعد وطني",
         "2 نقطة / دراسة — <strong>حد أقصى 6 نقاط</strong>.")
    if _add_btn("rs_add_natl"):
        st.session_state.rs_natl_studies.append({}); st.rerun()

    natl_pts = 0.0; del_natl = []
    for i, _ in enumerate(st.session_state.rs_natl_studies):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"عنوان الدراسة {i+1} *", key=f"rs_natl_title_{i}", placeholder="عنوان الدراسة أو التقرير")
        with c2:
            st.date_input("تاريخ الدراسة", key=f"rs_natl_date_{i}")
        with c3:
            # cert = st.file_uploader(f"📎 تقرير *", type=["pdf","jpg","jpeg","png"], key=f"rs_natl_cert_{i}")
            # auto
            st.markdown(f'<div style="font-size:.75rem;color:{"#1a7a4a" if has else "#e74c3c"};">{"✅" if has else "⚠️"}</div>',
                        unsafe_allow_html=True)
            pts  = 2 if has else 0
            _item_pts(pts)
            if _del_btn(f"rs_del_natl_{i}"): del_natl.append(i)
            natl_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_natl): st.session_state.rs_natl_studies.pop(i); st.rerun()
    natl_pts = min(natl_pts, 6.0)
    _score_line("نقاط الدراسات الوطنية", natl_pts, 6)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑨ الدراسات الوطنية"] = natl_pts

    # ⑩ دراسات دولية — غير مسقَّفة ➕ (حد 9 ن)
    _sec("⑩", "دراسات وخبرة ذات بُعد دولي",
         "3 نقاط / دراسة — <strong>حد أقصى 9 نقاط</strong>.")
    if _add_btn("rs_add_intl"):
        st.session_state.rs_intl_studies.append({}); st.rerun()

    intl_pts = 0.0; del_intl = []
    for i, _ in enumerate(st.session_state.rs_intl_studies):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3,2,1])
        with c1:
            st.text_input(f"عنوان الدراسة {i+1} *", key=f"rs_intl_title_{i}", placeholder="عنوان الدراسة الدولية")
            st.text_input(f"الجهة المنظمة", key=f"rs_intl_org_{i}", placeholder="اسم الجهة أو المنظمة")
        with c2:
            st.date_input("تاريخ الدراسة", key=f"rs_intl_date_{i}")
        with c3:
            # cert = st.file_uploader(f"📎 تقرير *", type=["pdf","jpg","jpeg","png"], key=f"rs_intl_cert_{i}")
            # auto
            st.markdown(f'<div style="font-size:.75rem;color:{"#1a7a4a" if has else "#e74c3c"};">{"✅" if has else "⚠️"}</div>',
                        unsafe_allow_html=True)
            pts  = 3 if has else 0
            _item_pts(pts)
            if _del_btn(f"rs_del_intl_{i}"): del_intl.append(i)
            intl_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_intl): st.session_state.rs_intl_studies.pop(i); st.rerun()
    intl_pts = min(intl_pts, 9.0)
    _score_line("نقاط الدراسات الدولية", intl_pts, 9)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["⑩ الدراسات الدولية"] = intl_pts

    # ══ ملخص النقاط ══════════════════════════════
    partial = sum(v for v in scores.values() if v is not None)

    st.markdown('<div class="card"><div class="card-title">🏆 ملخص النقاط</div>', unsafe_allow_html=True)
    for label, pts in scores.items():
        neg = pts < 0
        col = "#e74c3c" if neg else "#1a3a5c"
        st.markdown(
            f'<div class="score-row"><span>{label}</span>'
            f'<span style="font-weight:700;color:{col};">{pts:+.1f} ن</span></div>',
            unsafe_allow_html=True)

    color = "#27ae60" if partial >= 25 else "#c8973a" if partial >= 12 else "#e74c3c"
    st.markdown(f"""
    <div class="total-box" style="margin-top:.8rem;">
      <div style="color:rgba(255,255,255,.65);font-size:.82rem;">المجموع الكلي للنقاط</div>
      <div class="total-num" style="color:{color};">{partial:.1f}</div>
      <div style="color:rgba(255,255,255,.5);font-size:.78rem;">نقطة</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── الإقرار والتقديم
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if not st.session_state.get("rs_phd_doc"):
        st.markdown('<div class="alert al-er">❌ لا يمكن التقديم بدون رفع وثيقة التسجيل في الدكتوراه.</div>',
                    unsafe_allow_html=True)
    phd_doc_present = any(
        st.session_state.get(k) is not None
        for k in st.session_state
        if k == "rs_phd_doc"
    )
    decl = st.checkbox("أُقرّ بأن جميع المعلومات المُدرجة صحيحة وكاملة وأتحمل المسؤولية الكاملة.")
    if st.button("📤 تقديم الملف النهائي",
                 disabled=not decl, use_container_width=True):
        _upload_and_save(partial, scores, "التربصات قصيرة المدى للباحثين الدائمين")
    st.markdown('</div>', unsafe_allow_html=True)


def _upload_and_save(partial, scores, "التربصات قصيرة المدى للباحثين الدائمين"):
    data = {
        "username":    st.session_state.username,
        "name":        st.session_state.user_name,
        "grade":       st.session_state.get("grade",""),
        "position":    st.session_state.get("department","") or st.session_state.get("position",""),
        "scale":       "التربصات قصيرة المدى للباحثين الدائمين",
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
      مجموع نقاطك: <strong>{partial:.1f} نقطة</strong><br>
      سيتم إعلامك بالنتيجة من إدارة الكلية.
    </div>
    """, unsafe_allow_html=True)
