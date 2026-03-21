"""
نموذج التقديم — سلم الموظفين الإداريين والتقنيين
الإصلاحات:
1. النقاط تُحسب حتى لو سالبة (لا max(0))
2. _smart_upload يحفظ الملف في session_state فوراً
3. Drive يرفع bytes من session_state
4. بعد التقديم: عرض فقط بدون تعديل
"""
import streamlit as st, json, io
from datetime import datetime
from pathlib import Path


def _logout():
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()


def _header():
    name = st.session_state.get("user_name", "")
    rank = st.session_state.get("rank", "")
    silk = st.session_state.get("silk", "")
    st.markdown(f"""
    <div class="gov-header">
      <div style="font-size:.74rem;opacity:.6;margin-bottom:.2rem;">
        الجمهورية الجزائرية الديمقراطية الشعبية — وزارة التعليم العالي والبحث العلمي
      </div>
      <h1>📋 طلب الانتقاء — الموظفون الإداريون والتقنيون</h1>
      <p>كلية الحقوق والعلوم السياسية — جامعة محمد البشير الإبراهيمي برج بوعريريج</p>
      <div style="margin-top:.5rem;">
        <span class="badge b-blue">{name}</span>
        <span class="badge b-gold">{rank}</span>
        <span class="badge b-green">{silk}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    _, c2 = st.columns([5,1])
    with c2:
        if st.button("🚪 خروج", use_container_width=True): _logout()


def _sec(num, title, info=None):
    st.markdown(f'<div class="card"><div class="card-title">{num} {title}</div>',
                unsafe_allow_html=True)
    if info:
        st.markdown(f'<div class="alert al-in">{info}</div>', unsafe_allow_html=True)


def _score_line(label, pts, max_pts=None, neg=False):
    mx  = f" / {max_pts}" if max_pts else ""
    col = "#e74c3c" if (neg or pts < 0) else "#1a3a5c"
    val = f"{pts:+.1f}" if pts < 0 else f"{pts:.1f}"
    st.markdown(
        f'<div class="score-row"><span>{label}</span>'
        f'<span style="font-weight:700;color:{col};">{val}{mx} ن</span></div>',
        unsafe_allow_html=True)


def _smart_upload(label, skey, required=True):
    """
    يحفظ bytes الملف في session_state فور الرفع
    يعيد True إذا الملف موجود
    """
    marker = " *" if required else " (اختياري)"
    uploaded = st.file_uploader(
        f"📎 {label}{marker}",
        type=["pdf","jpg","jpeg","png"],
        key=f"uploader_{skey}"
    )
    if uploaded is not None:
        # احفظ فوراً قبل أي rerun
        st.session_state[f"file_{skey}"] = {
            "name":    uploaded.name,
            "content": uploaded.read(),
            "mime":    uploaded.type,
        }
    has = f"file_{skey}" in st.session_state
    if has:
        st.markdown(
            f'<div style="font-size:.78rem;color:#1a7a4a;margin-top:-6px;">'
            f'✅ {st.session_state[f"file_{skey}"]["name"]}</div>',
            unsafe_allow_html=True)
    elif required:
        st.markdown(
            '<div style="font-size:.78rem;color:#e74c3c;margin-top:-6px;">⚠️ الوثيقة مطلوبة</div>',
            unsafe_allow_html=True)
    return has


def _show_submitted():
    """عرض الملف المقدَّم بدون تعديل"""
    data = st.session_state.get("submitted_data", {})
    st.markdown(f"""
    <div class="alert al-ok">
      ✅ <strong>تم تقديم ملفك بنجاح — لا يمكن التعديل بعد التقديم.</strong><br>
      مجموع نقاطك الجزئية: <strong>{data.get('total_score', 0):.1f} نقطة</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-title">📋 ملخص ما قدّمته</div>',
                unsafe_allow_html=True)
    breakdown = json.loads(data.get("breakdown","{}"))
    for label, pts in breakdown.items():
        col = "#e74c3c" if float(pts) < 0 else "#1a3a5c"
        st.markdown(
            f'<div class="score-row"><span>{label}</span>'
            f'<span style="font-weight:700;color:{col};">{float(pts):+.1f} ن</span></div>',
            unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    links = json.loads(data.get("drive_links","{}"))
    if links:
        st.markdown('<div class="card"><div class="card-title">📎 وثائقك على Google Drive</div>',
                    unsafe_allow_html=True)
        for name, link in links.items():
            st.markdown(f"• [{name}]({link})")
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════
def show_form():
    _header()

    # ── إذا سبق التقديم: عرض فقط ─────────────────
    if st.session_state.get("submitted_admin"):
        _show_submitted()
        return

    if "bodies"    not in st.session_state: st.session_state.bodies    = []
    if "iprojects" not in st.session_state: st.session_state.iprojects = []

    # ① الرتبة الوظيفية
    _sec("①", "الرتبة الوظيفية",
         "ارفع وثيقة آخر ترقية — اللجنة تحدد نقاطك (8–12 نقطة).")
    rank_ok = _smart_upload("وثيقة آخر ترقية في الرتبة", "rank_doc", required=True)
    st.markdown('<div class="alert al-wn" style="font-size:.85rem;">⏳ نقاط الرتبة تُحدَّد من اللجنة بعد مراجعة الوثيقة.</div>',
                unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ② الأقدمية
    _sec("②", "الأقدمية في القطاع", "0.5 نقطة لكل سنة — حد أقصى 10 نقاط.")
    c1, c2 = st.columns(2)
    with c1:
        seniority = st.number_input("عدد سنوات الخدمة",
                                    min_value=0, max_value=40,
                                    value=int(st.session_state.get("years", 0)))
    with c2:
        _smart_upload("وثيقة إثبات الخدمة - قرار التوظيف", "sen_doc", required=False)
    seniority_pts = min(seniority * 0.5, 10.0)
    _score_line("نقاط الأقدمية", seniority_pts, 10)
    st.markdown('</div>', unsafe_allow_html=True)

    # ③ اللغات
    _sec("③", "التحكم في اللغات")
    lang_pts = 0.0
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**أ. لغة التكوين**")
        lang_ok = st.checkbox("أتحكم في لغة التكوين — 1 نقطة", key="chk_lang")
        if lang_ok:
            if _smart_upload("وثيقة إثبات التحكم في اللغة", "lang_doc", required=True):
                lang_pts += 1.0
            else:
                st.markdown('<div class="alert al-wn" style="font-size:.82rem;">⚠️ لن تُحتسب بدون وثيقة.</div>',
                            unsafe_allow_html=True)
    with c2:
        st.markdown("**ب. المركز المكثف للإنجليزية**")
        eng_ok = st.checkbox("مُسجَّل في المركز المكثف للإنجليزية — 2 نقطة", key="chk_eng")
        if eng_ok:
            if _smart_upload("شهادة التسجيل في المركز", "eng_doc", required=True):
                lang_pts += 2.0
            else:
                st.markdown('<div class="alert al-wn" style="font-size:.82rem;">⚠️ لن تُحتسب بدون شهادة.</div>',
                            unsafe_allow_html=True)
    _score_line("نقاط اللغات", lang_pts, 3)
    st.markdown('</div>', unsafe_allow_html=True)

    # ④ المشروع الوزاري
    _sec("④", "المساهمة في المشروع الوزاري (القرار 1275)",
         "الإشراف على مشروع مذكرة تخرج لمؤسسة ناشئة / مصغرة / براءة اختراع.")
    min_ok  = st.checkbox("شاركت في تجسيد هذا المشروع — 1 نقطة", key="chk_min")
    min_pts = 0.0
    if min_ok:
        if _smart_upload("وثيقة إثبات المشاركة", "min_doc", required=True):
            min_pts = 1.0
        else:
            st.markdown('<div class="alert al-wn" style="font-size:.82rem;">⚠️ لن تُحتسب بدون وثيقة.</div>',
                        unsafe_allow_html=True)
    _score_line("نقاط المشروع الوزاري", min_pts, 1)
    st.markdown('</div>', unsafe_allow_html=True)

    # ⑤ هيئات المرافقة
    _sec("⑤", "هيئات المرافقة الجامعية",
         "CDC / CATI / حاضنة أعمال... — 1 نقطة / شهادة — حد أقصى 2 نقطة.")
    _, bc = st.columns([5,1])
    with bc:
        if st.button("➕ إضافة", key="add_body", use_container_width=True):
            st.session_state.bodies.append({}); st.rerun()
    body_pts = 0.0; del_body = []
    for i, _ in enumerate(st.session_state.bodies):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        ca, cb, cc = st.columns([3,3,1])
        with ca:
            st.text_input(f"اسم الهيئة {i+1}", key=f"body_name_{i}", placeholder="مثال: CDC")
        with cb:
            if _smart_upload(f"شهادة العمل {i+1}", f"body_cert_{i}", required=True):
                body_pts += 1.0
        with cc:
            st.write("")
            if st.button("🗑️", key=f"del_body_{i}"): del_body.append(i)
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_body):
        st.session_state.bodies.pop(i)
        st.session_state.pop(f"file_body_cert_{i}", None)
        st.rerun()
    body_pts = min(body_pts, 2.0)
    _score_line("نقاط هيئات المرافقة", body_pts, 2)
    st.markdown('</div>', unsafe_allow_html=True)

    # ⑥ مشاريع دولية
    _sec("⑥", "المشاركة في المشاريع الدولية",
         "Erasmus+ / PRIMA / Horizon... — 2 نقطة / مشروع — حد أقصى 2 نقطة.")
    _, bc2 = st.columns([5,1])
    with bc2:
        if st.button("➕ إضافة", key="add_iproj", use_container_width=True):
            st.session_state.iprojects.append({}); st.rerun()
    iproj_pts = 0.0; del_iproj = []
    for i, _ in enumerate(st.session_state.iprojects):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        ca, cb, cc = st.columns([3,3,1])
        with ca:
            st.text_input(f"اسم المشروع {i+1}", key=f"iproj_name_{i}", placeholder="Erasmus+ / PRIMA...")
        with cb:
            if _smart_upload(f"شهادة المشاركة {i+1}", f"iproj_cert_{i}", required=True):
                iproj_pts += 2.0
        with cc:
            st.write("")
            if st.button("🗑️", key=f"del_iproj_{i}"): del_iproj.append(i)
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_iproj):
        st.session_state.iprojects.pop(i)
        st.session_state.pop(f"file_iproj_cert_{i}", None)
        st.rerun()
    iproj_pts = min(iproj_pts, 2.0)
    _score_line("نقاط المشاريع الدولية", iproj_pts, 2)
    st.markdown('</div>', unsafe_allow_html=True)

    # ⑦ المنصب العالي
    _sec("⑦", "المنصب العالي (هيكلي/وظيفي)",
         "رئيس مصلحة / مدير فرعي... — 2 نقطة. وثيقة إثبات إلزامية.")
    high_ok  = st.checkbox("أشغل منصباً عالياً — 2 نقطة", key="chk_high")
    high_pts = 0.0
    if high_ok:
        if _smart_upload("وثيقة إثبات المنصب العالي", "high_doc", required=True):
            high_pts = 2.0
        else:
            st.markdown('<div class="alert al-wn" style="font-size:.82rem;">⚠️ لن تُحتسب بدون وثيقة.</div>',
                        unsafe_allow_html=True)
    _score_line("نقاط المنصب العالي", high_pts, 2)
    st.markdown('</div>', unsafe_allow_html=True)

    # ⑧ الاستفادات السابقة — -5 نقاط لكل استفادة
    _sec("⑧", "الاستفادات السابقة من التربصات في الخارج",
         "يُخصم 5 نقاط عن كل تربص استُفيد منه في آخر 6 سنوات.")
    prev      = st.number_input("عدد الاستفادات السابقة", min_value=0, max_value=10, value=0)
    deduction = prev * 5.0
    if deduction > 0:
        st.markdown(f'<div class="alert al-wn">سيُخصم: {deduction:.0f} نقطة ({prev} × 5)</div>',
                    unsafe_allow_html=True)
    _score_line("الخصم", -deduction)
    st.markdown('</div>', unsafe_allow_html=True)

    # ══ ملخص النقاط — بدون max(0) ══
    partial = seniority_pts + lang_pts + min_pts + body_pts + iproj_pts + high_pts - deduction
    # لا نوقف عند الصفر — قد يكون سالباً

    st.markdown('<div class="card"><div class="card-title">🏆 ملخص النقاط</div>',
                unsafe_allow_html=True)
    rows = [
        ("① الرتبة الوظيفية",        None,          "⏳ تُحدَّد من اللجنة (8–12 ن)"),
        ("② الأقدمية",               seniority_pts,  None),
        ("③ اللغات",                 lang_pts,        None),
        ("④ المشروع الوزاري",        min_pts,         None),
        ("⑤ هيئات المرافقة",         body_pts,        None),
        ("⑥ مشاريع دولية",           iproj_pts,       None),
        ("⑦ المنصب العالي",           high_pts,        None),
        ("⑧ خصم الاستفادات السابقة", -deduction,      None),
    ]
    for label, pts, note in rows:
        if pts is None:
            st.markdown(
                f'<div class="score-row"><span>{label}</span>'
                f'<span style="color:#c8973a;font-size:.82rem;">{note}</span></div>',
                unsafe_allow_html=True)
        else:
            col = "#e74c3c" if pts < 0 else "#1a3a5c"
            st.markdown(
                f'<div class="score-row"><span>{label}</span>'
                f'<span style="font-weight:700;color:{col};">{pts:+.1f} ن</span></div>',
                unsafe_allow_html=True)

    color = "#27ae60" if partial >= 20 else "#c8973a" if partial >= 0 else "#e74c3c"
    st.markdown(f"""
    <div class="total-box" style="margin-top:.8rem;">
      <div style="color:rgba(255,255,255,.65);font-size:.82rem;">مجموع النقاط الجزئية</div>
      <div class="total-num" style="color:{color};">{partial:.1f}</div>
      <div style="color:rgba(255,255,255,.5);font-size:.78rem;">+ نقاط الرتبة تُضاف من اللجنة (8–12 ن)</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── الإقرار والتقديم ──────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if not rank_ok:
        st.markdown('<div class="alert al-er">❌ لا يمكن التقديم بدون رفع وثيقة آخر ترقية.</div>',
                    unsafe_allow_html=True)
    decl = st.checkbox("أُقرّ بأن جميع المعلومات المُدرجة صحيحة وكاملة وأتحمل المسؤولية الكاملة.")
    if st.button("📤 تقديم الملف النهائي",
                 disabled=not (decl and rank_ok and admin_docs_ok),
                 use_container_width=True):
        breakdown = {
            "الأقدمية": seniority_pts, "اللغات": lang_pts,
            "المشروع الوزاري": min_pts, "هيئات المرافقة": body_pts,
            "المشاريع الدولية": iproj_pts, "المنصب العالي": high_pts,
            "خصم الاستفادات": -deduction,
        }
        _submit(partial, breakdown)
    st.markdown('</div>', unsafe_allow_html=True)


def _submit(partial, breakdown):
    with st.spinner("⏳ جارٍ رفع الوثائق وحفظ الملف..."):

        # ── رفع كل الوثائق المحفوظة في session_state ──
        drive_links = {}
        try:
            from utils.drive import upload_file
            username = st.session_state.username
            for key, val in st.session_state.items():
                if key.startswith("file_") and isinstance(val, dict) and "content" in val:
                    doc_name = key.replace("file_", "")
                    ext      = val["name"].rsplit(".", 1)[-1]
                    link = upload_file(
                        content   = val["content"],
                        filename  = f"{username}_{doc_name}.{ext}",
                        username  = username,
                        mime_type = val["mime"],
                    )
                    if link:
                        drive_links[doc_name] = link
        except Exception:
            pass

        # ── حفظ في Sheets ────────────────────────────
        data = {
            "username":    st.session_state.username,
            "name":        st.session_state.user_name,
            "grade":       "مرفوعة — بانتظار اللجنة",
            "position":    st.session_state.get("rank",""),
            "scale":       "الموظفون الإداريون والتقنيون",
            "total_score": partial,
            "breakdown":   json.dumps(breakdown, ensure_ascii=False),
            "drive_links": json.dumps(drive_links, ensure_ascii=False),
            "status":      "قيد المراجعة",
        }
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

        # ── تسجيل أن المترشح قدّم ملفه ──────────────
        st.session_state.submitted_admin = True
        st.session_state.submitted_data  = data

    st.rerun()  # يُعيد التشغيل لعرض صفحة "تم التقديم"
