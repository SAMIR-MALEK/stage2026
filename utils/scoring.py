"""
محرك حساب النقاط - وفق سلالم التقييم الأربعة
القرار رقم 3/ك.ب/3 المؤرخ في 09 مارس 2026
"""


# ══════════════════════════════════════════════════════════════
# السلم الأول: الموظفون الإداريون والتقنيون
# ══════════════════════════════════════════════════════════════

RANK_SCORES_ADMIN = {
    "أعلى من 17": 12,
    "الرتبة 17": 11.5,
    "الرتبة 16": 11,
    "الرتبة 15": 10.5,
    "الرتبة 14": 10,
    "الرتبة 13": 9.5,
    "الرتبة 12": 9,
    "الرتبة 11": 8.5,
    "الرتبة 10": 8,
}

def calculate_admin_score(data: dict) -> dict:
    """
    حساب نقاط الموظفين الإداريين والتقنيين
    data keys:
      rank, seniority_years, lang_training, english_center,
      supervisor_attendance, supervisor_efficiency, supervisor_initiative, supervisor_availability,
      ministerial_contribution, accomp_bodies, intl_projects, high_position,
      prev_beneficiaries_count
    """
    breakdown = {}
    total = 0.0

    # 1. الرتبة
    rank_score = RANK_SCORES_ADMIN.get(data.get("rank", ""), 0)
    breakdown["الرتبة"] = rank_score
    total += rank_score

    # 2. الأقدمية في القطاع (0.5 لكل سنة، حد أقصى 10)
    seniority = min(data.get("seniority_years", 0) * 0.5, 10)
    breakdown["الأقدمية في القطاع"] = round(seniority, 1)
    total += seniority

    # 3. التحكم في اللغات
    lang_score = 0
    if data.get("lang_training"):     lang_score += 1   # لغة التكوين
    if data.get("english_center"):    lang_score += 2   # التسجيل في المركز المكثف
    breakdown["التحكم في اللغات"] = lang_score
    total += lang_score

    # 4. تقييم المسؤول المباشر (الحد الأقصى 9)
    sup_score = 0
    if data.get("supervisor_attendance"):   sup_score = min(sup_score + 3, 3)
    if data.get("supervisor_efficiency"):   sup_score = min(sup_score + 3, 6)
    if data.get("supervisor_initiative"):   sup_score = min(sup_score + 3, 9)
    if data.get("supervisor_availability"): sup_score = min(sup_score + 3, 9)
    sup_score = min(sup_score, 9)
    breakdown["تقييم المسؤول المباشر"] = sup_score
    total += sup_score

    # 5. المساهمة في المشروع الوزاري (القرار 1275)
    if data.get("ministerial_contribution"):
        breakdown["المساهمة في المشروع الوزاري"] = 1
        total += 1
    else:
        breakdown["المساهمة في المشروع الوزاري"] = 0

    # 6. شهادة تثبت عمل داخل هيئات المرافقة (حد أقصى 2)
    accomp = min(data.get("accomp_bodies", 0) * 1, 2)
    breakdown["هيئات المرافقة الجامعية"] = accomp
    total += accomp

    # 7. المشاركة في المشاريع الدولية (حد أقصى 2)
    intl = min(data.get("intl_projects", 0) * 2, 2)
    breakdown["المشاركة في المشاريع الدولية"] = intl
    total += intl

    # 8. المنصب العالي (هيكلي/وظيفي)
    if data.get("high_position"):
        breakdown["المنصب العالي"] = 2
        total += 2
    else:
        breakdown["المنصب العالي"] = 0

    # 9. خصم الاستفادات السابقة (-0.5 لكل تربص)
    prev = data.get("prev_beneficiaries_count", 0)
    deduction = prev * -0.5
    breakdown["خصم الاستفادات السابقة"] = round(deduction, 1)
    total += deduction

    return {
        "breakdown": breakdown,
        "total": round(max(total, 0), 2),
        "scale": "الموظفون الإداريون والتقنيون"
    }


# ══════════════════════════════════════════════════════════════
# السلم الثاني: الإقامة العلمية قصيرة المدى (أستاذ)
# ══════════════════════════════════════════════════════════════

SCIENTIFIC_RANK_SCORES = {
    "أستاذ مميز": 9,
    "أستاذ محاضر أ": 7,
    "أستاذ محاضر ب": 5,
    "أستاذ مساعد أ (مع ملف تأهيل)": 3 + 4,  # 3 + إضافة 4 لتحضير التأهيل
    "أستاذ مساعد أ": 3,
}

ARTICLE_SCORES = {
    "A+": 20, "A": 15, "B": 10, "C (وطني)": 5
}

def calculate_scientific_score(data: dict) -> dict:
    """
    حساب نقاط الإقامة العلمية قصيرة المدى
    """
    breakdown = {}
    total = 0.0

    # 1. الرتبة العلمية
    rank_score = SCIENTIFIC_RANK_SCORES.get(data.get("scientific_rank", ""), 0)
    breakdown["الرتبة العلمية"] = rank_score
    total += rank_score

    # 2. الاستفادات السابقة (n-3)
    prev = data.get("prev_beneficiaries", 0)
    prev_score = prev - 3
    breakdown["الاستفادات السابقة (n-3)"] = prev_score
    total += prev_score

    # 3. جوائز دولية/وطنية (10 نقاط بعد الاستفادة السابقة)
    if data.get("intl_awards"):
        breakdown["جوائز دولية/وطنية"] = 10
        total += 10
    else:
        breakdown["جوائز دولية/وطنية"] = 0

    # 4. نشر مقالات بعد آخر استفادة
    articles_score = 0
    for art in data.get("articles", []):
        cat = art.get("category", "")
        scope = art.get("scope", "دولي")
        if scope == "دولي":
            articles_score += ARTICLE_SCORES.get(cat, 0)
        else:
            articles_score += 5  # وطني صنف C (حد أقصى مقالان)
    breakdown["نشر المقالات"] = articles_score
    total += articles_score

    # 5. مداخلات بعد آخر استفادة
    intl_interv = data.get("intl_interventions", 0)
    intl_listed = data.get("intl_listed_interventions", 0)
    intl_unlisted = data.get("intl_unlisted_interventions", 0)
    natl_interv = data.get("natl_interventions", 0)

    interv_score = 0
    interv_score += min(intl_listed * 4, 4 * 4)       # مفهرسة: 4 نقاط (حد 4 مداخلات)
    interv_score += min(intl_unlisted * 2, 2 * 4)      # غير مفهرسة: 2 نقطة
    interv_score += min(natl_interv * 1, 1 * 4)        # وطنية: 1 نقطة
    breakdown["المداخلات الدولية والوطنية"] = interv_score
    total += interv_score

    # 6. مشروع دولي (10 نقاط/مشروع)
    intl_projects = data.get("intl_projects", 0)
    natl_projects = data.get("natl_projects", 0)
    proj_score = intl_projects * 10 + natl_projects * 5
    breakdown["المشاريع البحثية"] = proj_score
    total += proj_score

    # 7. الإشراف على الدكتوراه
    phd_supervised = data.get("phd_supervised", 0)
    phd_co_supervised = data.get("phd_co_supervised", 0)
    phd_juries = min(data.get("phd_juries", 0), 2)
    phd_score = phd_supervised * 5 + phd_co_supervised * 3 + phd_juries * 1
    breakdown["الإشراف على الدكتوراه"] = phd_score
    total += phd_score

    # 8. الإشراف على مذكرات الماستر والليسانس
    master_score = min(data.get("master_thesis", 0) * 1, 3)
    licence_score = min(data.get("licence_topics", 0) * 0.5, 3)
    breakdown["الإشراف على مذكرات الماستر"] = master_score
    breakdown["الإشراف على مذكرات الليسانس"] = licence_score
    total += master_score + licence_score

    # 9. المنصب العالي
    if data.get("high_position"):
        breakdown["المنصب العالي"] = 2
        total += 2
    else:
        breakdown["المنصب العالي"] = 0

    return {
        "breakdown": breakdown,
        "total": round(total, 2),
        "scale": "الإقامة العلمية قصيرة المدى"
    }


# ══════════════════════════════════════════════════════════════
# السلم الثالث: تربص تحسين المستوى
# ══════════════════════════════════════════════════════════════

def calculate_training_score(data: dict) -> dict:
    """
    حساب نقاط تربص تحسين المستوى
    """
    breakdown = {}
    total = 0.0

    # 1. الرتبة العلمية (نفس السلم الثاني)
    rank_score = SCIENTIFIC_RANK_SCORES.get(data.get("scientific_rank", ""), 0)
    breakdown["الرتبة العلمية"] = rank_score
    total += rank_score

    # 2. تسجيل منتظم (2 نقاط لكل تسجيل)
    reg_score = data.get("regular_registrations", 0) * 2
    breakdown["التسجيل المنتظم"] = reg_score
    total += reg_score

    # 3. الاستفادات السابقة (n-3)
    prev = data.get("prev_beneficiaries", 0)
    prev_score = prev - 3
    breakdown["الاستفادات السابقة (n-3)"] = prev_score
    total += prev_score

    # 4. جوائز
    if data.get("awards"):
        breakdown["الجوائز الوطنية والدولية"] = 5
        total += 5
    else:
        breakdown["الجوائز الوطنية والدولية"] = 0

    # 5. نشر مقالات
    articles_score = 0
    for art in data.get("articles", []):
        cat = art.get("category", "")
        scope = art.get("scope", "دولي")
        if scope == "دولي":
            articles_score += ARTICLE_SCORES.get(cat, 0)
        elif scope == "وطني":
            articles_score += 5
    breakdown["نشر المقالات"] = articles_score
    total += articles_score

    # 6. مداخلات
    intl_listed = data.get("intl_listed_interventions", 0)
    intl_unlisted = data.get("intl_unlisted_interventions", 0)
    natl_interv = data.get("natl_interventions", 0)
    interv_score = (
        min(intl_listed * 4, 16) +
        min(intl_unlisted * 2, 8) +
        min(natl_interv, 4)
    )
    breakdown["المداخلات"] = interv_score
    total += interv_score

    # 7. براءات الاختراع
    patents = data.get("patents", 0)
    patent_score = min(patents * 15, 45)
    breakdown["براءات الاختراع"] = patent_score
    total += patent_score

    # 8. مشاريع
    intl_projects = data.get("intl_projects", 0)
    natl_projects = data.get("natl_projects", 0)
    proj_score = intl_projects * 10 + natl_projects * 5
    breakdown["المشاريع البحثية"] = proj_score
    total += proj_score

    # 9. الإشراف على الدكتوراه
    phd_supervised = data.get("phd_supervised", 0)
    phd_co = data.get("phd_co_supervised", 0)
    phd_juries = min(data.get("phd_juries", 0), 2)
    proj_ref = data.get("ministerial_projects", 0)
    phd_score = phd_supervised * 5 + phd_co * 3 + phd_juries * 1 + min(proj_ref * 2, 4)
    breakdown["الإشراف على الدكتوراه"] = phd_score
    total += phd_score

    # 10. تأطير الماستر والليسانس
    master = min(data.get("master_thesis", 0) * 1, 3)
    licence = min(data.get("licence_topics", 0) * 0.5, 3)
    breakdown["تأطير مذكرات الماستر"] = master
    breakdown["تأطير مذكرات الليسانس"] = licence
    total += master + licence

    # 11. التدريس في جذع مشترك
    if data.get("shared_teaching"):
        breakdown["التدريس في جذع مشترك"] = 4
        total += 4
    else:
        breakdown["التدريس في جذع مشترك"] = 0

    # 12. المنصب العالي
    if data.get("high_position"):
        breakdown["المنصب العالي"] = 2
        total += 2
    else:
        breakdown["المنصب العالي"] = 0

    # 13. دراسة وخبرة ذات بُعد وطني/دولي
    natl_exp = min(data.get("natl_experience_reports", 0) * 2, 6)
    intl_exp = min(data.get("intl_experience_reports", 0) * 3, 9)
    exp_reports = min(data.get("experience_reports", 0) * 3, 6)
    breakdown["الدراسة والخبرة الوطنية"] = natl_exp
    breakdown["الدراسة والخبرة الدولية"] = intl_exp
    breakdown["تقارير ذات بُعد وطني"] = exp_reports
    total += natl_exp + intl_exp + exp_reports

    return {
        "breakdown": breakdown,
        "total": round(total, 2),
        "scale": "تربص تحسين المستوى"
    }


# ══════════════════════════════════════════════════════════════
# السلم الرابع: التربصات قصيرة المدى للباحثين الدائمين
# ══════════════════════════════════════════════════════════════

def calculate_researcher_score(data: dict) -> dict:
    """
    حساب نقاط التربصات قصيرة المدى للباحثين الدائمين
    """
    breakdown = {}
    total = 0.0

    # 1. التسجيل في الدكتوراه (2 نقاط/سنة)
    phd_years = data.get("phd_registration_years", 0)
    phd_reg_score = phd_years * 2
    breakdown["التسجيل في الدكتوراه"] = phd_reg_score
    total += phd_reg_score

    # 2. الاستفادات السابقة (n-3)
    prev = data.get("prev_beneficiaries", 0)
    prev_score = prev - 3
    breakdown["الاستفادات السابقة (n-3)"] = prev_score
    total += prev_score

    # 3. نشر في مجلة Scopus/Web of Science
    scopus_articles = data.get("scopus_articles", 0)
    wos_articles = data.get("wos_articles", 0)
    intl_conf = data.get("intl_conference_papers", 0)

    scopus_score = min(scopus_articles * 8, 70)  # 8 نقاط للمقال في Scopus (WOS)
    wos_score = min(wos_articles * 12, 70)        # 12 نقاط في WOS (IF)
    conf_score = min(intl_conf * 4, 12)           # Conference paper Scopus: 4
    pub_score = min(scopus_score + wos_score + conf_score, 70)

    breakdown["المنشورات في Scopus/WOS"] = pub_score
    total += pub_score

    # 4. مداخلات بعد آخر استفادة
    intl_listed = data.get("intl_listed_interventions", 0)
    intl_unlisted = data.get("intl_unlisted_interventions", 0)
    natl_interv = data.get("natl_interventions", 0)
    interv_score = (
        min(intl_listed * 4, 16) +
        min(intl_unlisted * 2, 8) +
        min(natl_interv, 4)
    )
    breakdown["المداخلات"] = interv_score
    total += interv_score

    # 5. براءات الاختراع
    patents = data.get("patents", 0)
    onda = data.get("onda_certificates", 0)
    patent_score = min(patents * 15, 45) + min(onda * 4, 8)
    breakdown["براءات الاختراع"] = patent_score
    total += patent_score

    # 6. مشاريع بحثية
    intl_projects = data.get("intl_projects", 0)
    natl_projects = data.get("natl_projects", 0)
    proj_score = min(intl_projects * 2, 6) + min(natl_projects * 2, 6)
    breakdown["المشاريع البحثية"] = proj_score
    total += proj_score

    # 7. الأنشطة الإدارية
    research_head = data.get("research_head", 0) * 2
    lab_resp = data.get("lab_responsible", 0) * 1
    incub_member = min(data.get("incubator_member", 0), 4)
    admin_score = research_head + lab_resp + incub_member
    breakdown["الأنشطة الإدارية"] = admin_score
    total += admin_score

    # 8. الأنشطة العلمية
    sci_committee = min(data.get("sci_committee_activities", 0), 6)
    sci_head = min(data.get("sci_committee_head", 0) * 2, 4)
    journal_review = min(data.get("journal_review", 0), 3)
    journal_editor = data.get("journal_editor", 0) * 2
    sci_score = sci_committee + sci_head + journal_review + journal_editor
    breakdown["الأنشطة العلمية"] = sci_score
    total += sci_score

    # 9. إشراف مذكرات الماستر (بعد آخر استفادة)
    master_thesis = min(data.get("master_thesis", 0) * 2, 6)
    breakdown["إشراف مذكرات الماستر"] = master_thesis
    total += master_thesis

    # 10. دراسة وخبرة
    natl_exp = min(data.get("natl_experience", 0) * 2, 6)
    intl_exp = min(data.get("intl_experience", 0) * 3, 9)
    exp_reports = min(data.get("experience_reports", 0) * 3, 6)
    breakdown["الدراسة والخبرة الوطنية"] = natl_exp
    breakdown["الدراسة والخبرة الدولية"] = intl_exp
    breakdown["التقارير ذات البُعد الوطني"] = exp_reports
    total += natl_exp + intl_exp + exp_reports

    return {
        "breakdown": breakdown,
        "total": round(total, 2),
        "scale": "التربصات قصيرة المدى للباحثين الدائمين"
    }


# ══════════════════════════════════════════════════════════════
# دالة الحساب الموحدة
# ══════════════════════════════════════════════════════════════

SCALE_FUNCTIONS = {
    "الموظفون الإداريون والتقنيون": calculate_admin_score,
    "الإقامة العلمية قصيرة المدى": calculate_scientific_score,
    "تربص تحسين المستوى": calculate_training_score,
    "التربصات قصيرة المدى للباحثين الدائمين": calculate_researcher_score,
}

def calculate_score(scale: str, data: dict) -> dict:
    """الدالة الرئيسية لحساب النقاط"""
    func = SCALE_FUNCTIONS.get(scale)
    if func:
        return func(data)
    return {"breakdown": {}, "total": 0, "scale": scale}
