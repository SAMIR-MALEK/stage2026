"""
نموذج التقديم — سلم الموظفين الإداريين والتقنيين
الرتبة: يرفع المترشح وثيقة آخر ترقية — اللجنة تحدد النقاط لاحقاً
تقييم المسؤول: محذوف كلياً
"""
import streamlit as st, json
from datetime import datetime
from pathlib import Path


def _logout():
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()


def _header():
    n = st.session_state.user_name
    p = st.session_state.position
    st.markdown(f"""
    <div class="gov-header">
      <div style="font-size:.74rem;opacity:.6;margin-bottom:.2rem;">
        الجمهورية الجزائرية الديمقراطية الشعبية — وزارة التعليم العالي والبحث العلمي
      </div>
      <h1>📋 طلب الانتقاء — الموظفون الإداريون والتقنيون</h1>
      <p>كلية الحقوق والعلوم السياسية — جامعة محمد البشير الإبراهيمي برج بوعريريج</p>
      <div style="margin-top:.5rem;">
        <span class="badge b-blue">{n}</span>
        <span class="badge b-gold">{p}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    _, c2 = st.columns([5,1])
    with c2:
        if st.button("🚪 خروج", use_container_width=True): _logout()


def _section(num, title, info=None):
    st.markdown(f'<div class="card"><div class="card-title">{num} {title}</div>', unsafe_allow_html=True)
    if info:
        st.markdown(f'<div class="alert al-in">{info}</div>', unsafe_allow_html=True)


def _score_line(label, pts, max_pts=None, negative=False):
    mx = f"<small style='color:#6b7f96'> / {max_pts}</small>" if max_pts else ""
    c  = "#e74c3c" if negative else "#1a3a5c"
    sign = f"{pts:+.1f}" if negative else f"{pts:.1f}"
    st.markdown(
        f'<div class="score-row"><span>{label}</span>'
        f'<span style="font-weight:700;color:{c};">{sign}{mx} ن</span></div>',
        unsafe_allow_html=True,
    )


def _upload(label, key, required=True, types=None):
    types = types or ["pdf", "jpg", "jpeg", "png"]
    tag = ' <span style="color:#e74c3c;font-size:.8rem;">*إلزامي</span>' if required else \
          ' <span style="color:#6b7f96;font-size:.8rem;">(اختياري)</span>'
    f = st.file_uploader(f"📎 {label}{tag}", type=types, key=key)
    if f:
        st.markdown(f'<div style="font-size:.78rem;color:#1a7a4a;margin-top:-6px;">✅ {f.name}</div>',
                    unsafe_allow_html=True)
    elif required:
        st.markdown('<div style="font-size:.78rem;color:#e74c3c;margin-top:-6px;">⚠️ الوثيقة مطلوبة</div>',
                    unsafe_allow_html=True)
    return f


# ══════════════════════════════════════════════════
def show_form():
    _header()

    # ① الرتبة الوظيفية — يرفع وثيقة، اللجنة تحدد النقاط
    _section("①", "الرتبة الوظيفية",
             "ارفع وثيقة <strong>آخر ترقية في الرتبة</strong> — ستقوم اللجنة بتحديد نقاطك بعد مراجعتها.")
    rank_doc = _upload("وثيقة آخر ترقية في الرتبة", "rank_doc", required=True)
    st.markdown("""
    <div class="alert al-wn" style="font-size:.85rem;">
      ⏳ نقاط الرتبة تُحدَّد من اللجنة بعد التحقق من الوثيقة (8 – 12 نقطة حسب الصنف).
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ② الأقدمية
    _section("②", "الأقدمية في القطاع",
             "0.5 نقطة لكل سنة خدمة — <strong>حد أقصى 10 نقاط</strong>.")
    c1, c2 = st.columns(2)
    with c1:
        seniority = st.number_input("عدد سنوات الخدمة في قطاع التعليم العالي",
                                    min_value=0, max_value=40,
                                    value=int(st.session_state.get("years", 0)))
    with c2:
        sen_doc = _upload("وثيقة إثبات الخدمة (قرار التوظيف)", "sen_doc", required=False)
    seniority_pts = min(seniority * 0.5, 10.0)
    _score_line("نقاط الأقدمية", seniority_pts, 10)
    st.markdown('</div>', unsafe_allow_html=True)

    # ③ لغة التكوين
    _section("③", "التحكم في اللغات")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**لغة التكوين**")
        lang_ok = st.checkbox("أتحكم في لغة التكوين — 1 نقطة")
    with c2:
        st.markdown("**المركز المكثف للإنجليزية**")
        eng_ok  = st.checkbox("مُسجَّل في المركز المكثف للإنجليزية — 2 نقطة")
        eng_doc = None
        if eng_ok:
            eng_doc = _upload("شهادة التسجيل في المركز", "eng_doc", required=True)
    lang_pts = (1.0 if lang_ok else 0.0) + (2.0 if (eng_ok and eng_doc) else 0.0)
    _score_line("نقاط اللغات", lang_pts, 3)
    st.markdown('</div>', unsafe_allow_html=True)

    # ④ المشروع الوزاري
    _section("④", "المساهمة في المشروع الوزاري (القرار 1275)",
             "الإشراف على مشروع مذكرة تخرج لمؤسسة ناشئة / مؤسسة مصغرة / براءة اختراع.")
    min_ok  = st.checkbox("شاركت في تجسيد هذا المشروع — 1 نقطة")
    min_doc = None
    if min_ok:
        min_doc = _upload("وثيقة إثبات المشاركة", "min_doc", required=True)
    min_pts = 1.0 if (min_ok and min_doc) else 0.0
    _score_line("نقاط المشروع الوزاري", min_pts, 1)
    st.markdown('</div>', unsafe_allow_html=True)

    # ⑤ هيئات المرافقة
    _section("⑤", "هيئات المرافقة الجامعية",
             "CDC / CATI / حاضنة أعمال / نادي البحث عن الشغل... — 1 نقطة / شهادة — <strong>حد أقصى 2 نقطة</strong>.")
    if "bodies" not in st.session_state: st.session_state.bodies = []
    _, btn_col = st.columns([5,1])
    with btn_col:
        if st.button("➕ إضافة", key="add_body", use_container_width=True):
            st.session_state.bodies.append({}); st.rerun()

    body_pts = 0.0; del_body = []
    for i, _ in enumerate(st.session_state.bodies):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        ca, cb, cc = st.columns([3,3,1])
        with ca:
            st.text_input(f"اسم الهيئة {i+1}", key=f"body_name_{i}",
                          placeholder="مثال: CDC — مركز المسارات المهنية")
        with cb:
            f = st.file_uploader(f"📎 شهادة العمل {i+1} *",
                                 type=["pdf","jpg","jpeg","png"], key=f"body_cert_{i}")
            if f:
                st.markdown(f'<div style="font-size:.78rem;color:#1a7a4a;">✅ {f.name}</div>',
                            unsafe_allow_html=True)
                body_pts += 1.0
            else:
                st.markdown('<div style="font-size:.78rem;color:#e74c3c;">⚠️ الشهادة مطلوبة</div>',
                            unsafe_allow_html=True)
        with cc:
            st.write("")
            if st.button("🗑️", key=f"del_body_{i}"): del_body.append(i)
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_body): st.session_state.bodies.pop(i); st.rerun()
    body_pts = min(body_pts, 2.0)
    _score_line("نقاط هيئات المرافقة", body_pts, 2)
    st.markdown('</div>', unsafe_allow_html=True)

    # ⑥ مشاريع دولية
    _section("⑥", "المشاركة في المشاريع الدولية",
             "Erasmus+ / PRIMA / Horizon... — 2 نقطة / مشروع — <strong>حد أقصى 2 نقطة</strong>.")
    if "iprojects" not in st.session_state: st.session_state.iprojects = []
    _, btn_col2 = st.columns([5,1])
    with btn_col2:
        if st.button("➕ إضافة", key="add_iproj", use_container_width=True):
            st.session_state.iprojects.append({}); st.rerun()

    iproj_pts = 0.0; del_iproj = []
    for i, _ in enumerate(st.session_state.iprojects):
        st.markdown('<div class="item-block">', unsafe_allow_html=True)
        ca, cb, cc = st.columns([3,3,1])
        with ca:
            st.text_input(f"اسم المشروع {i+1}", key=f"iproj_name_{i}",
                          placeholder="Erasmus+ / PRIMA...")
        with cb:
            f = st.file_uploader(f"📎 شهادة المشاركة {i+1} *",
                                 type=["pdf","jpg","jpeg","png"], key=f"iproj_cert_{i}")
            if f:
                st.markdown(f'<div style="font-size:.78rem;color:#1a7a4a;">✅ {f.name}</div>',
                            unsafe_allow_html=True)
                iproj_pts += 2.0
            else:
                st.markdown('<div style="font-size:.78rem;color:#e74c3c;">⚠️ الشهادة مطلوبة</div>',
                            unsafe_allow_html=True)
        with cc:
            st.write("")
            if st.button("🗑️", key=f"del_iproj_{i}"): del_iproj.append(i)
        st.markdown('</div>', unsafe_allow_html=True)
    for i in reversed(del_iproj): st.session_state.iprojects.pop(i); st.rerun()
    iproj_pts = min(iproj_pts, 2.0)
    _score_line("نقاط المشاريع الدولية", iproj_pts, 2)
    st.markdown('</div>', unsafe_allow_html=True)

    # ⑦ المنصب العالي
    _section("⑦", "المنصب العالي (هيكلي/وظيفي)")
    high_ok = st.checkbox("أشغل منصباً عالياً (رئيس مصلحة / مدير فرعي...) — 2 نقطة")
    high_pts = 2.0 if high_ok else 0.0
    _score_line("نقاط المنصب العالي", high_pts, 2)
    st.markdown('</div>', unsafe_allow_html=True)

    # ⑧ استفادات سابقة
    _section("⑧", "الاستفادات السابقة من التربصات في الخارج",
             "يُخصم <strong>0.5 نقطة</strong> عن كل تربص استُفيد منه في آخر 6 سنوات.")
    prev = st.number_input("عدد الاستفادات السابقة", min_value=0, max_value=10, value=0)
    deduction = prev * 0.5
    _score_line("الخصم", -deduction, negative=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════
    # ملخص النقاط
    # ══════════════════════════════════════════════
    partial = seniority_pts + lang_pts + min_pts + body_pts + iproj_pts + high_pts - deduction
    partial = max(partial, 0.0)

    st.markdown('<div class="card"><div class="card-title">🏆 ملخص النقاط</div>', unsafe_allow_html=True)
    rows = [
        ("① الرتبة الوظيفية",           None,         "⏳ تُحدَّد من اللجنة بعد مراجعة الوثيقة"),
        ("② الأقدمية",                  seniority_pts, None),
        ("③ اللغات",                    lang_pts,      None),
        ("④ المشروع الوزاري",           min_pts,       None),
        ("⑤ هيئات المرافقة",            body_pts,      None),
        ("⑥ مشاريع دولية",              iproj_pts,     None),
        ("⑦ المنصب العالي",              high_pts,      None),
        ("⑧ خصم الاستفادات السابقة",   -deduction,    None),
    ]
    for label, pts, note in rows:
        if pts is None:
            st.markdown(
                f'<div class="score-row"><span>{label}</span>'
                f'<span style="color:#c8973a;font-size:.82rem;">{note}</span></div>',
                unsafe_allow_html=True,
            )
        else:
            c = "#e74c3c" if pts < 0 else "#1a3a5c"
            st.markdown(
                f'<div class="score-row"><span>{label}</span>'
                f'<span style="font-weight:700;color:{c};">{pts:+.1f} ن</span></div>',
                unsafe_allow_html=True,
            )

    color = "#27ae60" if partial >= 20 else "#c8973a" if partial >= 10 else "#e74c3c"
    st.markdown(f"""
    <div class="total-box" style="margin-top:.8rem;">
      <div style="color:rgba(255,255,255,.65);font-size:.82rem;">
        مجموع النقاط الجزئية (بدون نقاط الرتبة)
      </div>
      <div class="total-num" style="color:{color};">{partial:.1f}</div>
      <div style="color:rgba(255,255,255,.5);font-size:.78rem;">
        + نقاط الرتبة تُضاف من اللجنة (8 – 12 نقطة)
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── الإقرار والتقديم ──────────────────────────────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if not rank_doc:
        st.markdown('<div class="alert al-er">❌ لا يمكن التقديم بدون رفع وثيقة آخر ترقية.</div>',
                    unsafe_allow_html=True)
    decl = st.checkbox("أُقرّ بأن جميع المعلومات المُدرجة صحيحة وكاملة وأتحمل المسؤولية الكاملة عن أي معلومة مغلوطة.")
    can_submit = decl and rank_doc is not None
    if st.button("📤 تقديم الملف النهائي", disabled=not can_submit, use_container_width=True):
        breakdown = {
            "seniority_pts": seniority_pts, "lang_pts": lang_pts,
            "min_pts": min_pts, "body_pts": body_pts,
            "iproj_pts": iproj_pts, "high_pts": high_pts,
            "deduction": deduction, "rank_note": "تُحدَّد من اللجنة",
        }
        _submit(partial, breakdown)
    st.markdown('</div>', unsafe_allow_html=True)


def _submit(partial, breakdown):
    data = {
        "username":    st.session_state.username,
        "name":        st.session_state.user_name,
        "grade":       "مرفوعة — بانتظار اللجنة",
        "position":    st.session_state.position,
        "scale":       "الموظفون الإداريون والتقنيون",
        "partial_score": partial,
        "total_score": partial,   # اللجنة ستضيف نقاط الرتبة لاحقاً
        "breakdown":   json.dumps(breakdown, ensure_ascii=False),
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
            with open(fname, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    st.balloons()
    st.markdown(f"""
    <div class="alert al-ok">
      ✅ <strong>تم تقديم ملفك بنجاح!</strong><br>
      مجموع نقاطك الجزئية: <strong>{partial:.1f} نقطة</strong><br>
      ستُضاف نقاط الرتبة من اللجنة بعد مراجعة وثيقة الترقية.<br>
      سيتم إعلامك بالنتيجة النهائية من إدارة الكلية.
    </div>
    """, unsafe_allow_html=True)
