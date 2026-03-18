"""نموذج التقديم — جميع السلالم الأربعة"""
import streamlit as st
import sys
sys.path.insert(0, ".")

from utils.scoring import (
    calculate_score,
    RANK_SCORES_ADMIN,
    SCIENTIFIC_RANK_SCORES,
)
from utils.google_integration import save_candidate_to_sheet, upload_multiple_files

SCALES = [
    "الموظفون الإداريون والتقنيون",
    "الإقامة العلمية قصيرة المدى",
    "تربص تحسين المستوى",
    "التربصات قصيرة المدى للباحثين الدائمين",
]

INSTITUTIONS = [
    "جامعة الجزائر 1", "جامعة الجزائر 2", "جامعة الجزائر 3",
    "جامعة سطيف 1", "جامعة سطيف 2",
    "جامعة قسنطينة 1", "جامعة قسنطينة 2", "جامعة قسنطينة 3",
    "جامعة وهران 1", "جامعة وهران 2",
    "جامعة عنابة", "جامعة بجاية", "جامعة تيزي وزو",
    "جامعة تلمسان", "جامعة بسكرة", "جامعة باتنة 1", "جامعة باتنة 2",
    "جامعة سيدي بلعباس", "جامعة مسيلة", "جامعة المسيلة",
    "المدرسة الوطنية العليا للهندسة", "مؤسسة أخرى",
]


def show():
    st.markdown("""
    <div class="gov-header">
        <h1>📋 نموذج التقديم لبرنامج تحسين المستوى في الخارج</h1>
        <p>يُرجى ملء جميع المعلومات بدقة وفق وضعيتك المهنية</p>
    </div>
    """, unsafe_allow_html=True)

    # ── اختيار السلم ──────────────────────────────────────
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<div class="form-section-title">① اختيار السلم</div>', unsafe_allow_html=True)
    selected_scale = st.selectbox(
        "اختر السلم المناسب لوضعيتك:",
        SCALES,
        help="اختر السلم المطابق لرتبتك وطبيعة التربص المطلوب"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── المعلومات الشخصية ──────────────────────────────────
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<div class="form-section-title">② المعلومات الشخصية</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        last_name  = st.text_input("اللقب *", placeholder="BENAISSA")
        email      = st.text_input("البريد الإلكتروني المؤسساتي *", placeholder="nom@univ.dz")
        institution = st.selectbox("المؤسسة *", INSTITUTIONS)
    with c2:
        first_name = st.text_input("الاسم *", placeholder="محمد")
        phone      = st.text_input("رقم الهاتف", placeholder="0555 XX XX XX")
        department = st.text_input("القسم / المخبر / الوحدة")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── معايير التقييم حسب السلم ──────────────────────────
    data = {}
    data["last_name"]   = last_name
    data["first_name"]  = first_name
    data["email"]       = email
    data["phone"]       = phone
    data["institution"] = institution
    data["department"]  = department

    if selected_scale == "الموظفون الإداريون والتقنيون":
        data.update(_form_admin())
    elif selected_scale == "الإقامة العلمية قصيرة المدى":
        data.update(_form_scientific())
    elif selected_scale == "تربص تحسين المستوى":
        data.update(_form_training())
    elif selected_scale == "التربصات قصيرة المدى للباحثين الدائمين":
        data.update(_form_researcher())

    # ── رفع الوثائق ────────────────────────────────────────
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<div class="form-section-title">④ الوثائق المطلوبة</div>', unsafe_allow_html=True)
    st.info("📎 يُرجى رفع الوثائق بصيغة PDF أو صورة (JPG, PNG). الحجم الأقصى: 10 ميجا لكل ملف")

    c1, c2 = st.columns(2)
    with c1:
        cv_file       = st.file_uploader("السيرة الذاتية (CV) *", type=["pdf", "jpg", "png"], key="cv")
        degree_file   = st.file_uploader("الشهادة العلمية *", type=["pdf", "jpg", "png"], key="deg")
        rank_cert     = st.file_uploader("شهادة الرتبة / الوضعية الإدارية *", type=["pdf", "jpg", "png"], key="rank")
    with c2:
        work_cert     = st.file_uploader("شهادة العمل *", type=["pdf", "jpg", "png"], key="work")
        supervisor_ev = st.file_uploader("تقييم المسؤول المباشر", type=["pdf", "jpg", "png"], key="sup")
        other_docs    = st.file_uploader("وثائق أخرى (مقالات، براءات، ...)", type=["pdf", "jpg", "png"],
                                          accept_multiple_files=True, key="other")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── حساب النقاط في الوقت الفعلي ─────────────────────
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<div class="form-section-title">⑤ حساب النقاط التقديري</div>', unsafe_allow_html=True)

    result = calculate_score(selected_scale, data)
    total  = result["total"]
    breakdown = result["breakdown"]

    col_score, col_detail = st.columns([1, 2])
    with col_score:
        color = "#2ecc71" if total >= 30 else "#c8973a" if total >= 15 else "#e74c3c"
        st.markdown(f"""
        <div class="score-display">
            <div class="score-label">مجموع النقاط</div>
            <div class="score-number" style='color:{color};'>{total:.1f}</div>
            <div class="score-label">نقطة</div>
        </div>
        """, unsafe_allow_html=True)

    with col_detail:
        st.markdown("**تفصيل النقاط:**")
        for criterion, pts in breakdown.items():
            color_pt = "green" if pts > 0 else ("red" if pts < 0 else "gray")
            icon = "✅" if pts > 0 else ("⚠️" if pts < 0 else "➖")
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;padding:0.3rem 0;"
                f"border-bottom:1px solid #eee;'>"
                f"<span>{icon} {criterion}</span>"
                f"<strong style='color:{color_pt};'>{pts:+.1f}</strong></div>",
                unsafe_allow_html=True
            )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── إقرار وتأكيد ───────────────────────────────────────
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    declaration = st.checkbox(
        "أقر بأن جميع المعلومات المدرجة في هذا الطلب صحيحة وكاملة، وأتحمل المسؤولية الكاملة عن أي معلومات مغلوطة."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── زر التقديم ─────────────────────────────────────────
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submit_btn = st.button("📤 تقديم الملف", use_container_width=True, disabled=not declaration)

    if submit_btn and declaration:
        if not last_name or not first_name or not email:
            st.error("❌ يرجى ملء جميع الحقول الإلزامية (*).")
        else:
            with st.spinner("⏳ جارٍ حفظ بياناتك ورفع الوثائق..."):
                # رفع الوثائق على Drive
                candidate_name = f"{last_name}_{first_name}"
                files_to_upload = [
                    ("cv", cv_file), ("degree", degree_file),
                    ("rank_cert", rank_cert), ("work_cert", work_cert),
                    ("supervisor_eval", supervisor_ev),
                ]
                drive_links = upload_multiple_files(files_to_upload, candidate_name)
                data["drive_links"] = str(drive_links)

                # حفظ في Google Sheets
                saved = save_candidate_to_sheet(data, result)

            if saved:
                st.balloons()
                st.markdown(f"""
                <div class="status-box status-accepted">
                    ✅ <strong>تم تقديم ملفك بنجاح!</strong><br>
                    مجموع نقاطك: <strong>{total:.1f} نقطة</strong><br>
                    سيتم إعلامك بنتيجة الانتقاء عبر البريد الإلكتروني: <strong>{email}</strong>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("حدث خطأ أثناء الحفظ. يرجى المحاولة مجدداً أو التواصل مع الإدارة.")


# ══════════════════════════════════════════════════════════
# نماذج المعايير حسب كل سلم
# ══════════════════════════════════════════════════════════

def _form_admin() -> dict:
    """نموذج الموظفين الإداريين"""
    data = {}
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<div class="form-section-title">③ معايير التصنيف — الموظفون الإداريون والتقنيون</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        data["rank"] = st.selectbox("الرتبة الوظيفية", list(RANK_SCORES_ADMIN.keys()))
        data["seniority_years"] = st.number_input("الأقدمية في القطاع (بالسنوات)", min_value=0, max_value=40, value=5)
    with c2:
        data["lang_training"] = st.checkbox("التحكم في لغة التكوين")
        data["english_center"] = st.checkbox("التسجيل في المركز المكثف للغة الإنجليزية")

    st.markdown("**تقييم المسؤول المباشر (كل بند = 3 نقاط):**")
    c1, c2 = st.columns(2)
    with c1:
        data["supervisor_attendance"]   = st.checkbox("الحضور")
        data["supervisor_efficiency"]   = st.checkbox("الكفاءة في العمل")
    with c2:
        data["supervisor_initiative"]   = st.checkbox("المبادرة")
        data["supervisor_availability"] = st.checkbox("التفرغ")

    st.markdown("**معايير إضافية:**")
    c1, c2 = st.columns(2)
    with c1:
        data["ministerial_contribution"] = st.checkbox("المساهمة في المشروع الوزاري (القرار 1275)")
        data["intl_projects"] = st.number_input("المشاركة في مشاريع دولية", min_value=0, max_value=5, value=0)
    with c2:
        data["accomp_bodies"] = st.number_input("شهادات هيئات المرافقة", min_value=0, max_value=2, value=0)
        data["high_position"] = st.checkbox("المنصب العالي (هيكلي/وظيفي)")

    data["prev_beneficiaries_count"] = st.number_input(
        "عدد الاستفادات السابقة خلال آخر 6 سنوات (يُطرح 0.5/تربص)",
        min_value=0, max_value=10, value=0
    )
    st.markdown('</div>', unsafe_allow_html=True)
    return data


def _form_scientific() -> dict:
    """نموذج الإقامة العلمية قصيرة المدى"""
    data = {}
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<div class="form-section-title">③ معايير التصنيف — الإقامة العلمية قصيرة المدى</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        data["scientific_rank"] = st.selectbox("الرتبة العلمية", list(SCIENTIFIC_RANK_SCORES.keys()))
        data["prev_beneficiaries"] = st.number_input("عدد الاستفادات السابقة (n)", min_value=0, max_value=10, value=0)
    with c2:
        data["intl_awards"] = st.checkbox("جوائز دولية/وطنية مرتبطة بإنجازات علمية")
        data["high_position"] = st.checkbox("المنصب العالي (هيكلي/وظيفي)")

    st.markdown("**المقالات المنشورة بعد آخر استفادة:**")
    n_articles = st.number_input("عدد المقالات المنشورة", min_value=0, max_value=20, value=0)
    articles = []
    for i in range(int(n_articles)):
        c1, c2 = st.columns(2)
        with c1:
            scope = st.selectbox(f"نطاق المقال {i+1}", ["دولي", "وطني"], key=f"art_scope_{i}")
        with c2:
            cats = ["A+", "A", "B", "C (وطني)"] if scope == "دولي" else ["C (وطني)"]
            cat = st.selectbox(f"تصنيف المقال {i+1}", cats, key=f"art_cat_{i}")
        articles.append({"scope": scope, "category": cat})
    data["articles"] = articles

    st.markdown("**المداخلات (بعد آخر استفادة):**")
    c1, c2, c3 = st.columns(3)
    with c1:
        data["intl_listed_interventions"]   = st.number_input("دولية مفهرسة", min_value=0, max_value=10, value=0)
    with c2:
        data["intl_unlisted_interventions"] = st.number_input("دولية غير مفهرسة", min_value=0, max_value=10, value=0)
    with c3:
        data["natl_interventions"]          = st.number_input("وطنية", min_value=0, max_value=10, value=0)

    st.markdown("**المشاريع البحثية:**")
    c1, c2 = st.columns(2)
    with c1:
        data["intl_projects"] = st.number_input("مشاريع دولية (Erasmus+, PRIMA...)", min_value=0, max_value=10, value=0)
    with c2:
        data["natl_projects"] = st.number_input("مشاريع وطنية (PNR, PRFU...)", min_value=0, max_value=10, value=0)

    st.markdown("**الإشراف على الدكتوراه:**")
    c1, c2, c3 = st.columns(3)
    with c1:
        data["phd_supervised"]    = st.number_input("أطروحات نوقشت (مشرف)", min_value=0, max_value=20, value=0)
    with c2:
        data["phd_co_supervised"] = st.number_input("أطروحات نوقشت (مشارك)", min_value=0, max_value=20, value=0)
    with c3:
        data["phd_juries"]        = st.number_input("مشاركة في لجان مناقشة", min_value=0, max_value=10, value=0)

    c1, c2 = st.columns(2)
    with c1:
        data["master_thesis"]  = st.number_input("مذكرات الماستر المأطرة", min_value=0, max_value=30, value=0)
    with c2:
        data["licence_topics"] = st.number_input("مواضيع الليسانس المأطرة", min_value=0, max_value=30, value=0)

    st.markdown('</div>', unsafe_allow_html=True)
    return data


def _form_training() -> dict:
    """نموذج تربص تحسين المستوى"""
    data = {}
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<div class="form-section-title">③ معايير التصنيف — تربص تحسين المستوى</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        data["scientific_rank"]       = st.selectbox("الرتبة العلمية", list(SCIENTIFIC_RANK_SCORES.keys()))
        data["regular_registrations"] = st.number_input("عدد التسجيلات المنتظمة", min_value=0, max_value=10, value=0)
        data["prev_beneficiaries"]    = st.number_input("عدد الاستفادات السابقة (n)", min_value=0, max_value=10, value=0)
    with c2:
        data["awards"]        = st.checkbox("جوائز دولية/وطنية")
        data["high_position"] = st.checkbox("المنصب العالي")
        data["shared_teaching"] = st.checkbox("التدريس في جذع مشترك")

    st.markdown("**المقالات:**")
    n_articles = st.number_input("عدد المقالات", min_value=0, max_value=20, value=0, key="train_arts")
    articles = []
    for i in range(int(n_articles)):
        c1, c2 = st.columns(2)
        with c1:
            scope = st.selectbox(f"نطاق {i+1}", ["دولي", "وطني"], key=f"tr_scope_{i}")
        with c2:
            cat = st.selectbox(f"تصنيف {i+1}", ["A+", "A", "B", "C (وطني)"], key=f"tr_cat_{i}")
        articles.append({"scope": scope, "category": cat})
    data["articles"] = articles

    st.markdown("**المداخلات:**")
    c1, c2, c3 = st.columns(3)
    with c1:
        data["intl_listed_interventions"]   = st.number_input("دولية مفهرسة", 0, 10, 0, key="tr_il")
    with c2:
        data["intl_unlisted_interventions"] = st.number_input("دولية غير مفهرسة", 0, 10, 0, key="tr_iu")
    with c3:
        data["natl_interventions"]          = st.number_input("وطنية", 0, 10, 0, key="tr_n")

    st.markdown("**براءات الاختراع والمشاريع:**")
    c1, c2, c3 = st.columns(3)
    with c1:
        data["patents"]       = st.number_input("براءات الاختراع", 0, 20, 0)
    with c2:
        data["intl_projects"] = st.number_input("مشاريع دولية", 0, 10, 0, key="tr_ip")
    with c3:
        data["natl_projects"] = st.number_input("مشاريع وطنية", 0, 10, 0, key="tr_np")

    st.markdown("**الإشراف والتأطير:**")
    c1, c2, c3 = st.columns(3)
    with c1:
        data["phd_supervised"]    = st.number_input("أطروحات دكتوراه (مشرف)", 0, 20, 0, key="tr_phd")
        data["ministerial_projects"] = st.number_input("مشاريع وزارية (القرار 1275)", 0, 5, 0)
    with c2:
        data["phd_co_supervised"] = st.number_input("أطروحات دكتوراه (مشارك)", 0, 20, 0, key="tr_cophd")
        data["master_thesis"]     = st.number_input("مذكرات الماستر", 0, 30, 0, key="tr_mast")
    with c3:
        data["phd_juries"]        = st.number_input("لجان مناقشة دكتوراه", 0, 10, 0, key="tr_jury")
        data["licence_topics"]    = st.number_input("مواضيع الليسانس", 0, 30, 0, key="tr_lic")

    st.markdown("**الدراسة والخبرة:**")
    c1, c2, c3 = st.columns(3)
    with c1:
        data["natl_experience_reports"] = st.number_input("دراسات ذات بُعد وطني", 0, 5, 0)
    with c2:
        data["intl_experience_reports"] = st.number_input("دراسات ذات بُعد دولي", 0, 5, 0)
    with c3:
        data["experience_reports"] = st.number_input("تقارير ذات بُعد وطني", 0, 5, 0, key="tr_rep")

    st.markdown('</div>', unsafe_allow_html=True)
    return data


def _form_researcher() -> dict:
    """نموذج الباحثين الدائمين"""
    data = {}
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<div class="form-section-title">③ معايير التصنيف — الباحثون الدائمون</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        data["phd_registration_years"] = st.number_input("سنوات التسجيل في الدكتوراه", 0, 10, 1)
        data["prev_beneficiaries"]     = st.number_input("عدد الاستفادات السابقة (n)", 0, 10, 0)
    with c2:
        data["onda_certificates"] = st.number_input("شهادات ONDA", 0, 5, 0)

    st.markdown("**المنشورات الدولية (Scopus / WOS):**")
    c1, c2, c3 = st.columns(3)
    with c1:
        data["scopus_articles"]      = st.number_input("مقالات Scopus", 0, 30, 0)
    with c2:
        data["wos_articles"]         = st.number_input("مقالات WOS (IF)", 0, 30, 0)
    with c3:
        data["intl_conference_papers"] = st.number_input("Conference Papers Scopus", 0, 20, 0)

    st.markdown("**المداخلات:**")
    c1, c2, c3 = st.columns(3)
    with c1:
        data["intl_listed_interventions"]   = st.number_input("دولية مفهرسة", 0, 10, 0, key="res_il")
    with c2:
        data["intl_unlisted_interventions"] = st.number_input("دولية غير مفهرسة", 0, 10, 0, key="res_iu")
    with c3:
        data["natl_interventions"]          = st.number_input("وطنية", 0, 10, 0, key="res_n")

    st.markdown("**براءات الاختراع:**")
    c1, c2 = st.columns(2)
    with c1:
        data["patents"] = st.number_input("براءات الاختراع", 0, 20, 0, key="res_pat")
    with c2:
        data["intl_projects"] = st.number_input("مشاريع دولية", 0, 10, 0, key="res_ip")
        data["natl_projects"] = st.number_input("مشاريع وطنية", 0, 10, 0, key="res_np")

    st.markdown("**الأنشطة الإدارية والعلمية:**")
    c1, c2 = st.columns(2)
    with c1:
        data["research_head"]             = st.number_input("مدير وحدة/مخبر بحث", 0, 3, 0)
        data["sci_committee_activities"]  = st.number_input("نشاطات اللجنة العلمية", 0, 10, 0)
        data["journal_review"]            = st.number_input("عضو لجنة قراءة في مجلة", 0, 5, 0)
    with c2:
        data["incubator_member"]          = st.number_input("عضوية اللجنة العلمية للحاضنة", 0, 4, 0)
        data["sci_committee_head"]        = st.number_input("رئيس لجنة علمية", 0, 5, 0)
        data["journal_editor"]            = st.number_input("رئيس مجلة علمية", 0, 3, 0)

    st.markdown("**تأطير المذكرات والخبرة:**")
    c1, c2 = st.columns(2)
    with c1:
        data["master_thesis"]     = st.number_input("مذكرات الماستر المأطرة", 0, 20, 0, key="res_mast")
        data["natl_experience"]   = st.number_input("دراسات وطنية", 0, 5, 0)
    with c2:
        data["intl_experience"]   = st.number_input("دراسات دولية", 0, 5, 0)
        data["experience_reports"] = st.number_input("تقارير ذات بُعد وطني", 0, 5, 0, key="res_rep")

    st.markdown('</div>', unsafe_allow_html=True)
    return data
