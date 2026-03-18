"""
نموذج التقديم — سلم تربص تحسين المستوى (أساتذة)
المعايير المسقفة: حقول ثابتة
المعايير غير المسقفة: زر ➕ إضافة إلى ما لا نهاية
"""
import streamlit as st, json
from datetime import datetime, date
from pathlib import Path

# ── نقاط المعايير ──────────────────────────────────────────
ARTICLE_PTS  = {"A+": 20, "A": 15, "B": 10, "C (وطني)": 5}
INTERV_PTS   = {"دولية مفهرسة (Scopus/WOS)": 4, "دولية غير مفهرسة": 2, "وطنية": 1}
PROJECT_PTS  = {"دولي (Erasmus+, PRIMA, Horizon...)": 10, "وطني (PNR, PRFU...)": 5}
SUPERV_PTS   = {"مشرف رئيسي": 5, "مشرف مشارك": 3, "عضو لجنة مناقشة": 1}
JURY_MAX     = 2   # حد أقصى لعضوية لجان المناقشة


def _logout():
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

def _header():
    st.markdown(f"""
    <div class="gov-header">
      <div style="font-size:.74rem;opacity:.6;margin-bottom:.2rem;">
        الجمهورية الجزائرية الديمقراطية الشعبية — وزارة التعليم العالي والبحث العلمي
      </div>
      <h1>📋 طلب الانتقاء — تربص تحسين المستوى</h1>
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

def _upload(label, key, required=True):
    tag = ' <span style="color:#e74c3c;font-size:.8rem;">*إلزامي</span>' if required \
          else ' <span style="color:#6b7f96;font-size:.8rem;">(اختياري)</span>'
    f = st.file_uploader(f"📎 {label}{tag}",
                         type=["pdf","jpg","jpeg","png"], key=key)
    if f:
        st.markdown(f'<div style="font-size:.78rem;color:#1a7a4a;margin-top:-6px;">✅ {f.name}</div>',
                    unsafe_allow_html=True)
    elif required:
        st.markdown('<div style="font-size:.78rem;color:#e74c3c;margin-top:-6px;">⚠️ الوثيقة مطلوبة</div>',
                    unsafe_allow_html=True)
    return f

def _add_btn(key):
    """زر إضافة عنصر جديد"""
    _, c = st.columns([5,1])
    with c:
        return st.button("➕ إضافة", key=key, use_container_width=True)

def _del_btn(key):
    return st.button("🗑️", key=key, help="حذف")


# ══════════════════════════════════════════════════
# النموذج الرئيسي
# ══════════════════════════════════════════════════

def show_form():
    _header()

    # تهيئة القوائم الديناميكية
    for lst in ["tr_articles","tr_interventions","tr_patents",
                "tr_projects","tr_supervisions"]:
        if lst not in st.session_state:
            st.session_state[lst] = []

    scores = {}

    # ──────────────────────────────────────────────
    # ① الرتبة العلمية — اللجنة تحدد النقاط
    # ──────────────────────────────────────────────
    _sec("①", "الرتبة العلمية",
         "ارفع وثيقة <strong>آخر ترقية</strong> — اللجنة تحدد نقاطك (7 – 9 نقطة).")
    rank_doc = _upload("وثيقة آخر ترقية في الرتبة", "rank_doc", required=True)
    st.markdown('<div class="alert al-wn" style="font-size:.85rem;">⏳ نقاط الرتبة تُضاف من اللجنة بعد مراجعة الوثيقة.</div>',
                unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["الرتبة"] = None   # اللجنة

    # ──────────────────────────────────────────────
    # ② التسجيل المنتظم — مسقَّف (حسب عدد السنوات)
    # ──────────────────────────────────────────────
    _sec("②", "التسجيل المنتظم",
         "2 نقطة لكل سنة تسجيل منتظم في الدكتوراه أو التأهيل.")
    reg_count = st.number_input("عدد سنوات التسجيل المنتظم", 0, 10, 0, key="tr_reg")
    reg_doc   = _upload("وثيقة إثبات التسجيل", "reg_doc", required=reg_count > 0)
    reg_pts   = reg_count * 2.0
    _score_line("نقاط التسجيل المنتظم", reg_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["التسجيل المنتظم"] = reg_pts

    # ──────────────────────────────────────────────
    # ③ الاستفادات السابقة — مسقَّف
    # ──────────────────────────────────────────────
    _sec("③", "الاستفادات السابقة",
         "الصيغة: <strong>n − 3</strong> (n = عدد الاستفادات السابقة). قد تكون سالبة.")
    prev_n    = st.number_input("عدد الاستفادات السابقة (n)", 0, 15, 0, key="tr_prev")
    prev_pts  = float(prev_n - 3)
    _score_line("نقاط / خصم الاستفادات", prev_pts, neg=(prev_pts < 0))
    st.markdown('</div>', unsafe_allow_html=True)
    scores["الاستفادات السابقة"] = prev_pts

    # ──────────────────────────────────────────────
    # ④ الجوائز — مسقَّف (5 نقاط)
    # ──────────────────────────────────────────────
    _sec("④", "الجوائز الوطنية والدولية المرتبطة بإنجازات علمية",
         "5 نقاط — وثيقة الجائزة إلزامية.")
    award_ok  = st.checkbox("حصلت على جائزة وطنية أو دولية — 5 نقطة", key="tr_award")
    award_doc = None
    if award_ok:
        award_doc = _upload("وثيقة الجائزة أو شهادة التكريم", "award_doc", required=True)
    award_pts = 5.0 if (award_ok and award_doc) else 0.0
    _score_line("نقاط الجوائز", award_pts, 5)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["الجوائز"] = award_pts

    # ──────────────────────────────────────────────
    # ⑤ المقالات العلمية — غير مسقَّفة ➕ إلى ما لا نهاية
    # ──────────────────────────────────────────────
    _sec("⑤", "المقالات العلمية المنشورة",
         "أضف مقالاً لكل ورقة منشورة. الرابط (DOI) إلزامي لكل مقال.")

    if _add_btn("add_art"):
        st.session_state.tr_articles.append({}); st.rerun()

    art_pts = 0.0; del_art = []
    for i, _ in enumerate(st.session_state.tr_articles):
        st.markdown(f'<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3, 2, 1])
        with c1:
            st.text_input(f"عنوان المقال {i+1} *", key=f"art_title_{i}",
                          placeholder="عنوان المقال العلمي")
            st.text_input(f"اسم المجلة {i+1} *", key=f"art_journal_{i}",
                          placeholder="اسم المجلة")
        with c2:
            scope = st.selectbox("النطاق", ["دولي","وطني"], key=f"art_scope_{i}")
            cats  = list(ARTICLE_PTS.keys()) if scope == "دولي" else ["C (وطني)"]
            cat   = st.selectbox("التصنيف", cats, key=f"art_cat_{i}")
            st.text_input(f"رابط DOI *", key=f"art_doi_{i}",
                          placeholder="https://doi.org/...")
        with c3:
            f = st.file_uploader(f"📎 PDF {i+1}", type=["pdf"], key=f"art_pdf_{i}")
            if f: st.markdown(f'<div style="font-size:.75rem;color:#1a7a4a;">✅</div>', unsafe_allow_html=True)
            doi_val = st.session_state.get(f"art_doi_{i}", "")
            pts = ARTICLE_PTS.get(cat, 0) if doi_val else 0
            st.markdown(f'<div style="font-weight:700;color:#1a3a5c;text-align:center;font-size:1rem;">{pts}ن</div>',
                        unsafe_allow_html=True)
            if _del_btn(f"del_art_{i}"): del_art.append(i)
        art_pts += ARTICLE_PTS.get(cat, 0) if st.session_state.get(f"art_doi_{i}","") else 0
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_art): st.session_state.tr_articles.pop(i); st.rerun()
    _score_line("مجموع نقاط المقالات", art_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["المقالات"] = art_pts

    # ──────────────────────────────────────────────
    # ⑥ المداخلات — غير مسقَّفة ➕
    # ──────────────────────────────────────────────
    _sec("⑥", "المداخلات في المؤتمرات",
         "شهادة المشاركة <strong>إلزامية</strong> لكل مداخلة — بدونها لا تُحتسب النقاط.")

    if _add_btn("add_int"):
        st.session_state.tr_interventions.append({}); st.rerun()

    int_pts = 0.0; del_int = []
    for i, _ in enumerate(st.session_state.tr_interventions):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3, 2, 1])
        with c1:
            st.text_input(f"عنوان المداخلة {i+1} *", key=f"int_title_{i}",
                          placeholder="عنوان الورقة البحثية")
            st.text_input(f"اسم المؤتمر {i+1} *", key=f"int_conf_{i}",
                          placeholder="اسم المؤتمر أو الملتقى")
        with c2:
            int_type = st.selectbox("نوع المداخلة", list(INTERV_PTS.keys()), key=f"int_type_{i}")
            st.date_input(f"تاريخ المداخلة", key=f"int_date_{i}")
        with c3:
            cert = st.file_uploader(f"📎 شهادة {i+1} *",
                                    type=["pdf","jpg","jpeg","png"], key=f"int_cert_{i}")
            has  = cert is not None
            if has:   st.markdown('<div style="font-size:.75rem;color:#1a7a4a;">✅</div>', unsafe_allow_html=True)
            else:     st.markdown('<div style="font-size:.75rem;color:#e74c3c;">⚠️</div>', unsafe_allow_html=True)
            pts  = INTERV_PTS.get(int_type, 0) if has else 0
            st.markdown(f'<div style="font-weight:700;color:#1a3a5c;text-align:center;font-size:1rem;">{pts}ن</div>',
                        unsafe_allow_html=True)
            if _del_btn(f"del_int_{i}"): del_int.append(i)
            int_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_int): st.session_state.tr_interventions.pop(i); st.rerun()
    _score_line("مجموع نقاط المداخلات", int_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["المداخلات"] = int_pts

    # ──────────────────────────────────────────────
    # ⑦ براءات الاختراع — غير مسقَّفة ➕ (حد 45 ن)
    # ──────────────────────────────────────────────
    _sec("⑦", "براءات الاختراع",
         "15 نقطة لكل براءة — <strong>حد أقصى 45 نقطة</strong>. شهادة البراءة إلزامية.")

    if _add_btn("add_pat"):
        st.session_state.tr_patents.append({}); st.rerun()

    pat_pts = 0.0; del_pat = []
    for i, _ in enumerate(st.session_state.tr_patents):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3, 2, 1])
        with c1:
            st.text_input(f"عنوان البراءة {i+1} *", key=f"pat_title_{i}",
                          placeholder="عنوان الاختراع")
            st.text_input(f"رقم البراءة {i+1}", key=f"pat_num_{i}",
                          placeholder="رقم شهادة البراءة")
        with c2:
            st.date_input(f"تاريخ الحصول", key=f"pat_date_{i}")
            st.text_input(f"رابط (اختياري)", key=f"pat_url_{i}",
                          placeholder="https://...")
        with c3:
            cert = st.file_uploader(f"📎 شهادة {i+1} *",
                                    type=["pdf","jpg","jpeg","png"], key=f"pat_cert_{i}")
            has  = cert is not None
            if has:   st.markdown('<div style="font-size:.75rem;color:#1a7a4a;">✅</div>', unsafe_allow_html=True)
            else:     st.markdown('<div style="font-size:.75rem;color:#e74c3c;">⚠️</div>', unsafe_allow_html=True)
            pts  = 15 if has else 0
            st.markdown(f'<div style="font-weight:700;color:#1a3a5c;text-align:center;font-size:1rem;">{pts}ن</div>',
                        unsafe_allow_html=True)
            if _del_btn(f"del_pat_{i}"): del_pat.append(i)
            pat_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_pat): st.session_state.tr_patents.pop(i); st.rerun()
    pat_pts = min(pat_pts, 45.0)
    _score_line("مجموع نقاط براءات الاختراع", pat_pts, 45)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["براءات الاختراع"] = pat_pts

    # ──────────────────────────────────────────────
    # ⑧ المشاريع البحثية — غير مسقَّفة ➕
    # ──────────────────────────────────────────────
    _sec("⑧", "المشاريع البحثية",
         "أضف كل مشروع بحثي شاركت فيه. وثيقة الإثبات إلزامية.")

    if _add_btn("add_proj"):
        st.session_state.tr_projects.append({}); st.rerun()

    proj_pts = 0.0; del_proj = []
    for i, _ in enumerate(st.session_state.tr_projects):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3, 2, 1])
        with c1:
            st.text_input(f"عنوان المشروع {i+1} *", key=f"proj_title_{i}",
                          placeholder="عنوان المشروع البحثي")
            st.text_input(f"رابط المشروع (اختياري)", key=f"proj_url_{i}",
                          placeholder="https://...")
        with c2:
            ptype = st.selectbox("نوع المشروع", list(PROJECT_PTS.keys()), key=f"proj_type_{i}")
            st.date_input("تاريخ البداية", key=f"proj_date_{i}")
        with c3:
            cert = st.file_uploader(f"📎 وثيقة {i+1} *",
                                    type=["pdf","jpg","jpeg","png"], key=f"proj_cert_{i}")
            has  = cert is not None
            if has:   st.markdown('<div style="font-size:.75rem;color:#1a7a4a;">✅</div>', unsafe_allow_html=True)
            else:     st.markdown('<div style="font-size:.75rem;color:#e74c3c;">⚠️</div>', unsafe_allow_html=True)
            pts  = PROJECT_PTS.get(ptype, 0) if has else 0
            st.markdown(f'<div style="font-weight:700;color:#1a3a5c;text-align:center;font-size:1rem;">{pts}ن</div>',
                        unsafe_allow_html=True)
            if _del_btn(f"del_proj_{i}"): del_proj.append(i)
            proj_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_proj): st.session_state.tr_projects.pop(i); st.rerun()
    _score_line("مجموع نقاط المشاريع", proj_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["المشاريع"] = proj_pts

    # ──────────────────────────────────────────────
    # ⑨ الإشراف على الدكتوراه — غير مسقَّف ➕
    # ──────────────────────────────────────────────
    _sec("⑨", "الإشراف على أطروحات الدكتوراه",
         "أضف كل أطروحة شاركت في الإشراف عليها أو مناقشتها. محضر المناقشة إلزامي.")

    if _add_btn("add_sup"):
        st.session_state.tr_supervisions.append({}); st.rerun()

    sup_pts = 0.0; jury_count = 0; del_sup = []
    for i, _ in enumerate(st.session_state.tr_supervisions):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3, 2, 1])
        with c1:
            st.text_input(f"اسم الطالب {i+1}", key=f"sup_stud_{i}",
                          placeholder="اسم الطالب")
            st.text_input(f"عنوان الأطروحة {i+1}", key=f"sup_thesis_{i}",
                          placeholder="عنوان أطروحة الدكتوراه")
        with c2:
            stype = st.selectbox("الصفة", list(SUPERV_PTS.keys()), key=f"sup_type_{i}")
            st.date_input("تاريخ المناقشة", key=f"sup_date_{i}")
        with c3:
            cert = st.file_uploader(f"📎 محضر {i+1} *",
                                    type=["pdf","jpg","jpeg","png"], key=f"sup_cert_{i}")
            has  = cert is not None
            if has:   st.markdown('<div style="font-size:.75rem;color:#1a7a4a;">✅</div>', unsafe_allow_html=True)
            else:     st.markdown('<div style="font-size:.75rem;color:#e74c3c;">⚠️</div>', unsafe_allow_html=True)
            if stype == "عضو لجنة مناقشة":
                jury_count += 1
                pts = SUPERV_PTS["عضو لجنة مناقشة"] if (has and jury_count <= JURY_MAX) else 0
                if jury_count > JURY_MAX:
                    st.markdown('<div style="font-size:.72rem;color:#e74c3c;">تجاوز الحد (2)</div>',
                                unsafe_allow_html=True)
            else:
                pts = SUPERV_PTS.get(stype, 0) if has else 0
            st.markdown(f'<div style="font-weight:700;color:#1a3a5c;text-align:center;font-size:1rem;">{pts}ن</div>',
                        unsafe_allow_html=True)
            if _del_btn(f"del_sup_{i}"): del_sup.append(i)
            sup_pts += pts
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_sup): st.session_state.tr_supervisions.pop(i); st.rerun()
    _score_line("مجموع نقاط الإشراف على الدكتوراه", sup_pts)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["الإشراف على الدكتوراه"] = sup_pts

    # ──────────────────────────────────────────────
    # ⑩ تأطير الماستر والليسانس — مسقَّف (حد 3 لكل)
    # ──────────────────────────────────────────────
    _sec("⑩", "تأطير مذكرات الماستر والليسانس",
         "ماستر: 1 نقطة / مذكرة (حد 3 ن) — ليسانس: 0.5 نقطة / موضوع (حد 3 ن).")
    c1, c2 = st.columns(2)
    with c1:
        master_n  = st.number_input("عدد مذكرات الماستر المُؤطَّرة", 0, 50, 0, key="tr_master")
        master_pts= min(master_n * 1.0, 3.0)
        _score_line("نقاط الماستر", master_pts, 3)
    with c2:
        lic_n     = st.number_input("عدد مواضيع الليسانس المُؤطَّرة", 0, 100, 0, key="tr_lic")
        lic_pts   = min(lic_n * 0.5, 3.0)
        _score_line("نقاط الليسانس", lic_pts, 3)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["تأطير الماستر"]   = master_pts
    scores["تأطير الليسانس"] = lic_pts

    # ──────────────────────────────────────────────
    # ⑪⑫ المنصب العالي + التدريس في جذع مشترك — مسقَّف
    # ──────────────────────────────────────────────
    _sec("⑪⑫", "أنشطة إضافية")
    c1, c2 = st.columns(2)
    with c1:
        high_ok  = st.checkbox("المنصب العالي (هيكلي/وظيفي) — 2 نقطة", key="tr_high")
        high_pts = 2.0 if high_ok else 0.0
        _score_line("المنصب العالي", high_pts, 2)
    with c2:
        shared_ok  = st.checkbox("التدريس في جذع مشترك — 4 نقاط", key="tr_shared")
        shared_pts = 4.0 if shared_ok else 0.0
        _score_line("التدريس في جذع مشترك", shared_pts, 4)
    st.markdown('</div>', unsafe_allow_html=True)
    scores["المنصب العالي"]            = high_pts
    scores["التدريس في جذع مشترك"]    = shared_pts

    # ══════════════════════════════════════════════
    # ملخص النقاط الكلية
    # ══════════════════════════════════════════════
    partial = sum(v for v in scores.values() if v is not None)

    st.markdown('<div class="card"><div class="card-title">🏆 ملخص النقاط</div>', unsafe_allow_html=True)
    for label, pts in scores.items():
        if pts is None:
            st.markdown(
                f'<div class="score-row"><span>① الرتبة العلمية</span>'
                f'<span style="color:#c8973a;font-size:.82rem;">⏳ تُحدَّد من اللجنة (7–9 ن)</span></div>',
                unsafe_allow_html=True)
        else:
            neg = pts < 0
            col = "#e74c3c" if neg else "#1a3a5c"
            st.markdown(
                f'<div class="score-row"><span>{label}</span>'
                f'<span style="font-weight:700;color:{col};">{pts:+.1f} ن</span></div>',
                unsafe_allow_html=True)

    color = "#27ae60" if partial >= 30 else "#c8973a" if partial >= 15 else "#e74c3c"
    st.markdown(f"""
    <div class="total-box" style="margin-top:.8rem;">
      <div style="color:rgba(255,255,255,.65);font-size:.82rem;">مجموع النقاط الجزئية</div>
      <div class="total-num" style="color:{color};">{partial:.1f}</div>
      <div style="color:rgba(255,255,255,.5);font-size:.78rem;">+ نقاط الرتبة تُضاف من اللجنة (7–9 ن)</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── الإقرار والتقديم ──────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if not rank_doc:
        st.markdown('<div class="alert al-er">❌ لا يمكن التقديم بدون رفع وثيقة آخر ترقية.</div>',
                    unsafe_allow_html=True)
    decl = st.checkbox("أُقرّ بأن جميع المعلومات المُدرجة صحيحة وكاملة وأتحمل المسؤولية الكاملة.")
    if st.button("📤 تقديم الملف النهائي",
                 disabled=not (decl and rank_doc), use_container_width=True):
        _submit(partial, scores)
    st.markdown('</div>', unsafe_allow_html=True)


def _submit(partial, scores):
    data = {
        "username":     st.session_state.username,
        "name":         st.session_state.user_name,
        "grade":        "مرفوعة — بانتظار اللجنة",
        "position":     st.session_state.get("department","") or st.session_state.get("position",""),
        "scale":        "تربص تحسين المستوى",
        "total_score":  partial,
        "breakdown":    json.dumps(scores, ensure_ascii=False),
        "status":       "قيد المراجعة",
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
