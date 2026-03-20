"""
نموذج التقديم — سلم الموظفين الإداريين والتقنيين
الحل: حفظ محتوى الملفات في session_state فور رفعها
"""
import streamlit as st, json
from datetime import datetime
from pathlib import Path


def _logout():
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()


def _header():
    st.markdown(f"""
    <div class="gov-header">
      <div style="font-size:.74rem;opacity:.6;margin-bottom:.2rem;">
        الجمهورية الجزائرية الديمقراطية الشعبية — وزارة التعليم العالي والبحث العلمي
      </div>
      <h1>📋 طلب الانتقاء — الموظفون الإداريون والتقنيون</h1>
      <p>كلية الحقوق والعلوم السياسية — جامعة محمد البشير الإبراهيمي برج بوعريريج</p>
      <div style="margin-top:.5rem;">
        <span class="badge b-blue">{st.session_state.user_name}</span>
        <span class="badge b-gold">{st.session_state.position}</span>
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
    col = "#e74c3c" if neg else "#1a3a5c"
    val = f"{pts:+.1f}" if neg else f"{pts:.1f}"
    st.markdown(
        f'<div class="score-row"><span>{label}</span>'
        f'<span style="font-weight:700;color:{col};">{val}{mx} ن</span></div>',
        unsafe_allow_html=True)


def _smart_upload(label, session_key, required=True):
    """
    رفع ملف ذكي — يحفظ المحتوى في session_state فور الرفع
    يعيد True إذا الملف موجود (مرفوع الآن أو سابقاً)
    """
    marker = " *" if required else " (اختياري)"
    f = st.file_uploader(f"📎 {label}{marker}",
                         type=["pdf","jpg","jpeg","png"],
                         key=f"uploader_{session_key}")
    
    # حفظ المحتوى فور الرفع
    if f is not None:
        st.session_state[f"file_{session_key}"] = {
            "name":    f.name,
            "content": f.read(),
            "type":    f.type,
        }
    
    # هل الملف موجود؟ (مرفوع الآن أو سابقاً في الجلسة)
    has_file = f"file_{session_key}" in st.session_state
    
    if has_file:
        fname = st.session_state[f"file_{session_key}"]["name"]
        st.markdown(f'<div style="font-size:.78rem;color:#1a7a4a;margin-top:-6px;">✅ {fname}</div>',
                    unsafe_allow_html=True)
    elif required:
        st.markdown('<div style="font-size:.78rem;color:#e74c3c;margin-top:-6px;">⚠️ الوثيقة مطلوبة</div>',
                    unsafe_allow_html=True)
    return has_file


def _get_all_files() -> dict:
    """جمع كل الملفات المحفوظة في session_state"""
    files = {}
    for key, val in st.session_state.items():
        if key.startswith("file_") and isinstance(val, dict) and "content" in val:
            doc_name = key.replace("file_", "")
            files[doc_name] = val
    return files


# ══════════════════════════════════════════════════
def show_form():
    _header()

    # تهيئة القوائم
    if "bodies"   not in st.session_state: st.session_state.bodies   = []
    if "iprojects" not in st.session_state: st.session_state.iprojects = []

    # ① الرتبة الوظيفية
    _sec("①", "الرتبة الوظيفية",
         "ارفع وثيقة آخر ترقية في الرتبة — اللجنة تحدد نقاطك (8–12 نقطة).")
    rank_ok = _smart_upload("وثيقة آخر ترقية في الرتبة", "rank_doc", required=True)
    st.markdown('<div class="alert al-wn" style="font-size:.85rem;">⏳ نقاط الرتبة تُحدَّد من اللجنة بعد مراجعة الوثيقة.</div>',
                unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ② الأقدمية
    _sec("②", "الأقدمية في القطاع", "0.5 نقطة لكل سنة — حد أقصى 10 نقاط.")
    c1, c2 = st.columns(2)
    with c1:
        seniority = st.number_input("عدد سنوات الخدمة في قطاع التعليم العالي",
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
            has_lang = _smart_upload("وثيقة إثبات التحكم في اللغة", "lang_doc", required=True)
            if has_lang:
                lang_pts += 1.0
            else:
                st.markdown('<div class="alert al-wn" style="font-size:.82rem;">⚠️ لن تُحتسب النقطة بدون وثيقة.</div>',
                            unsafe_allow_html=True)
    with c2:
        st.markdown("**ب. المركز المكثف للإنجليزية**")
        eng_ok = st.checkbox("مُسجَّل في المركز المكثف للإنجليزية — 2 نقطة", key="chk_eng")
        if eng_ok:
            has_eng = _smart_upload("شهادة التسجيل في المركز", "eng_doc", required=True)
            if has_eng:
                lang_pts += 2.0
            else:
                st.markdown('<div class="alert al-wn" style="font-size:.82rem;">⚠️ لن تُحتسب النقطتان بدون شهادة.</div>',
                            unsafe_allow_html=True)
    _score_line("نقاط اللغات", lang_pts, 3)
    st.markdown('</div>', unsafe_allow_html=True)

    # ④ المشروع الوزاري
    _sec("④", "المساهمة في المشروع الوزاري (القرار 1275)",
         "الإشراف على مشروع مذكرة تخرج لمؤسسة ناشئة / مصغرة / براءة اختراع.")
    min_ok = st.checkbox("شاركت في تجسيد هذا المشروع — 1 نقطة", key="chk_min")
    min_pts = 0.0
    if min_ok:
        has_min = _smart_upload("وثيقة إثبات المشاركة", "min_doc", required=True)
        min_pts = 1.0 if has_min else 0.0
        if not has_min:
            st.markdown('<div class="alert al-wn" style="font-size:.82rem;">⚠️ لن تُحتسب النقطة بدون وثيقة.</div>',
                        unsafe_allow_html=True)
    _score_line("نقاط المشروع الوزاري", min_pts, 1)
    st.markdown('</div>', unsafe_allow_html=True)

    # ⑤ هيئات المرافقة
    _sec("⑤", "هيئات المرافقة الجامعية",
         "CDC / CATI / حاضنة أعمال... — 1 نقطة / شهادة — حد أقصى 2 نقطة.")
    _, btn_col = st.columns([5,1])
    with btn_col:
        if st.button("➕ إضافة", key="add_body", use_container_width=True):
            st.session_state.bodies.append({}); st.rerun()

    body_pts = 0.0; del_body = []
    for i, _ in enumerate(st.session_state.bodies):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        ca, cb, cc = st.columns([3,3,1])
        with ca:
            st.text_input(f"اسم الهيئة {i+1}", key=f"body_name_{i}", placeholder="مثال: CDC")
        with cb:
            has = _smart_upload(f"شهادة العمل {i+1}", f"body_cert_{i}", required=True)
            if has: body_pts += 1.0
        with cc:
            st.write("")
            if st.button("🗑️", key=f"del_body_{i}"): del_body.append(i)
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_body):
        st.session_state.bodies.pop(i)
        # حذف الملف المرتبط
        st.session_state.pop(f"file_body_cert_{i}", None)
        st.rerun()
    body_pts = min(body_pts, 2.0)
    _score_line("نقاط هيئات المرافقة", body_pts, 2)
    st.markdown('</div>', unsafe_allow_html=True)

    # ⑥ مشاريع دولية
    _sec("⑥", "المشاركة في المشاريع الدولية",
         "Erasmus+ / PRIMA / Horizon... — 2 نقطة / مشروع — حد أقصى 2 نقطة.")
    _, btn_col2 = st.columns([5,1])
    with btn_col2:
        if st.button("➕ إضافة", key="add_iproj", use_container_width=True):
            st.session_state.iprojects.append({}); st.rerun()

    iproj_pts = 0.0; del_iproj = []
    for i, _ in enumerate(st.session_state.iprojects):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        ca, cb, cc = st.columns([3,3,1])
        with ca:
            st.text_input(f"اسم المشروع {i+1}", key=f"iproj_name_{i}", placeholder="Erasmus+ / PRIMA...")
        with cb:
            has = _smart_upload(f"شهادة المشاركة {i+1}", f"iproj_cert_{i}", required=True)
            if has: iproj_pts += 2.0
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
    high_ok = st.checkbox("أشغل منصباً عالياً — 2 نقطة", key="chk_high")
    high_pts = 0.0
    if high_ok:
        has_high = _smart_upload("وثيقة إثبات المنصب العالي", "high_doc", required=True)
        high_pts = 2.0 if has_high else 0.0
        if not has_high:
            st.markdown('<div class="alert al-wn" style="font-size:.82rem;">⚠️ لن تُحتسب النقطتان بدون وثيقة.</div>',
                        unsafe_allow_html=True)
    _score_line("نقاط المنصب العالي", high_pts, 2)
    st.markdown('</div>', unsafe_allow_html=True)

    # ⑧ الاستفادات السابقة — -5 نقاط لكل استفادة
    _sec("⑧", "الاستفادات السابقة من التربصات في الخارج",
         "يُخصم 5 نقاط عن كل تربص استُفيد منه في آخر 6 سنوات.")
    prev = st.number_input("عدد الاستفادات السابقة في آخر 6 سنوات",
                           min_value=0, max_value=10, value=0)
    deduction = prev * 5.0
    if deduction > 0:
        st.markdown(f'<div class="alert al-wn">سيُخصم: {deduction:.0f} نقطة ({prev} × 5)</div>',
                    unsafe_allow_html=True)
    _score_line("الخصم", -deduction, neg=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ══ ملخص النقاط ══
    partial = seniority_pts + lang_pts + min_pts + body_pts + iproj_pts + high_pts - deduction
    partial = max(partial, 0.0)

    st.markdown('<div class="card"><div class="card-title">🏆 ملخص النقاط</div>',
                unsafe_allow_html=True)
    rows = [
        ("① الرتبة الوظيفية",        None,         "⏳ تُحدَّد من اللجنة (8–12 ن)"),
        ("② الأقدمية",               seniority_pts, None),
        ("③ اللغات",                 lang_pts,       None),
        ("④ المشروع الوزاري",        min_pts,        None),
        ("⑤ هيئات المرافقة",         body_pts,       None),
        ("⑥ مشاريع دولية",           iproj_pts,      None),
        ("⑦ المنصب العالي",           high_pts,       None),
        ("⑧ خصم الاستفادات السابقة", -deduction,     None),
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

    color = "#27ae60" if partial >= 20 else "#c8973a" if partial >= 10 else "#e74c3c"
    st.markdown(f"""
    <div class="total-box" style="margin-top:.8rem;">
      <div style="color:rgba(255,255,255,.65);font-size:.82rem;">مجموع النقاط الجزئية</div>
      <div class="total-num" style="color:{color};">{partial:.1f}</div>
      <div style="color:rgba(255,255,255,.5);font-size:.78rem;">+ نقاط الرتبة تُضاف من اللجنة (8–12 ن)</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── الإقرار والتقديم
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if not rank_ok:
        st.markdown('<div class="alert al-er">❌ لا يمكن التقديم بدون رفع وثيقة آخر ترقية.</div>',
                    unsafe_allow_html=True)
    decl = st.checkbox("أُقرّ بأن جميع المعلومات المُدرجة صحيحة وكاملة وأتحمل المسؤولية الكاملة.")
    if st.button("📤 تقديم الملف النهائي",
                 disabled=not (decl and rank_ok),
                 use_container_width=True):
        _submit(partial, {
            "الأقدمية": seniority_pts, "اللغات": lang_pts,
            "المشروع الوزاري": min_pts, "هيئات المرافقة": body_pts,
            "المشاريع الدولية": iproj_pts, "المنصب العالي": high_pts,
            "خصم الاستفادات": -deduction,
        })
    st.markdown('</div>', unsafe_allow_html=True)


def _submit(partial, breakdown):
    with st.spinner("⏳ جارٍ رفع الوثائق وحفظ الملف..."):

        # ── رفع الوثائق على Drive ────────────────────
        drive_links = {}
        try:
            from utils.drive import upload_file
            username = st.session_state.username
            all_files = _get_all_files()
            for doc_name, file_data in all_files.items():
                import io
                link = upload_file(
                    io.BytesIO(file_data["content"]),
                    f"{username}_{doc_name}.{file_data['name'].rsplit('.',1)[-1]}",
                    username,
                    file_data["type"]
                )
                if link:
                    drive_links[doc_name] = link
        except Exception as e:
            pass

        # ── حفظ في Sheets ────────────────────────────
        data = {
            "username":    st.session_state.username,
            "name":        st.session_state.user_name,
            "grade":       "مرفوعة — بانتظار اللجنة",
            "position":    st.session_state.position,
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

    st.balloons()
    st.markdown(f"""
    <div class="alert al-ok">
      ✅ <strong>تم تقديم ملفك بنجاح!</strong><br>
      مجموع نقاطك الجزئية: <strong>{partial:.1f} نقطة</strong><br>
      وثائق مرفوعة على Drive: <strong>{len(drive_links)}</strong>
    </div>
    """, unsafe_allow_html=True)
    if drive_links:
        st.markdown("**روابط وثائقك:**")
        for name, link in drive_links.items():
            st.markdown(f"• [{name}]({link})")
