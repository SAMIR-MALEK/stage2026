"""لوحة لجنة الانتقاء — مبسّطة ومنظمة بالصيغ"""
import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

STATUS_OPTIONS = ["قيد المراجعة", "مقبول", "مرفوض", "قائمة انتظار"]

LABEL_MAP = {
    "tr_rank":"وثيقة الرتبة","rank_doc":"وثيقة الرتبة","sc_rank":"وثيقة الرتبة",
    "tr_reg_doc":"وثيقة التسجيل","tr_award_doc":"وثيقة الجائزة",
    "tr_sup_cert_0":"محضر دكتوراه 1","tr_sup_cert_1":"محضر دكتوراه 2",
    "tr_int_cert_0":"شهادة مداخلة 1","tr_int_cert_1":"شهادة مداخلة 2",
    "tr_pat_cert_0":"براءة اختراع 1","tr_proj_cert_0":"وثيقة مشروع 1",
    "tr_master_doc_1":"محاضر ماستر","tr_lic_doc_1":"وثيقة إشراف ليسانس",
    "tr_shared_doc_1":"وثيقة جذع مشترك","high_doc":"وثيقة المنصب العالي",
    "adm_f1_istimara":"استمارة الترشح ص1","adm_f1_mashrou3":"مشروع العمل","adm_f1_ta3ahod":"التعهد",
    "adm_f2_istimara":"استمارة الترشح ص2","adm_f2_mashrou3":"مشروع العمل","adm_f2_ta3ahod":"التعهد",
    "adm_f3_istimara":"استمارة الترشح ص3","adm_f3_mashrou3":"مشروع العمل",
    "adm_f3_ta3ahod":"التعهد","adm_f3_tasrih":"التصريح الشرفي",
    "adm_f4_istimara":"استمارة الترشح ص4","adm_f4_mashrou3":"مشروع العمل","adm_f4_ta3ahod":"التعهد",
    "taheel_doc":"تعهد التأهيل",
}

SILKS = [
    ("صيغة 1 — أساتذة محاضرون",  "أساتذة محاضرون"),
    ("صيغة 2 — أساتذة مساعدون",  "أساتذة مساعدون"),
    ("صيغة 3 — طلبة دكتوراه",    "طلبة دكتوراه"),
    ("صيغة 4 — إداريون وتقنيون", "إداريون وتقنيون"),
]


def _logout():
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()


def _f(v):
    try:
        s = str(v).replace(",","").replace(" ","")
        return float(s) if s not in ("","None","nan") else 0.0
    except:
        return 0.0


def _load_df() -> pd.DataFrame:
    records = []
    try:
        from utils.sheets import _get_client, SHEET_NAME
        cl = _get_client()
        if cl:
            recs = cl.open(SHEET_NAME).sheet1.get_all_records()
            records = recs if recs else []
    except Exception:
        pass
    if not records:
        sub = Path("data/submissions")
        if sub.exists():
            for f in sorted(sub.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
                try:
                    with open(f, encoding="utf-8") as fp:
                        d = json.load(fp); records.append(d)
                except Exception:
                    pass
    if not records:
        return pd.DataFrame()
    rows = []
    for r in records:
        rows.append({
            "اسم_المستخدم": str(r.get("اسم_المستخدم", r.get("username",""))).strip(),
            "الاسم_الكامل": str(r.get("الاسم_الكامل", r.get("name",""))).strip(),
            "السلك":        str(r.get("السلك",  r.get("silk",""))).strip(),
            "الرتبة":       str(r.get("الرتبة", r.get("rank",""))).strip(),
            "الصيغة":       str(r.get("الصيغة", r.get("scale",""))).strip(),
            "النقاط_الجزئية":_f(r.get("النقاط_الجزئية", r.get("total_score",0))),
            "النقاط_الكلية": _f(r.get("النقاط_الكلية",  r.get("total_score",0))),
            "الحالة":       str(r.get("الحالة", r.get("status","قيد المراجعة"))).strip(),
            "التاريخ":      str(r.get("التاريخ","")).strip(),
            "تفصيل_النقاط": str(r.get("تفصيل_النقاط", r.get("breakdown","{}")) or "{}"),
            "روابط_الوثائق":str(r.get("روابط_الوثائق", r.get("drive_links","{}")) or "{}"),
        })
    return pd.DataFrame(rows)


def _parse_json(s):
    try:
        v = str(s).strip()
        if not v or v in ("nan","None","{}"): return {}
        return json.loads(v)
    except:
        return {}


def _save(username, new_scores, new_total, new_status):
    try:
        from utils.sheets import _get_client, SHEET_NAME
        cl = _get_client()
        if cl:
            ws   = cl.open(SHEET_NAME).sheet1
            recs = ws.get_all_records()
            hdrs = list(recs[0].keys()) if recs else []
            for i, rec in enumerate(recs, 2):
                if str(rec.get("اسم_المستخدم","")).strip() == username:
                    if "تفصيل_النقاط" in hdrs:
                        ws.update_cell(i, hdrs.index("تفصيل_النقاط")+1,
                                       json.dumps(new_scores, ensure_ascii=False))
                    if "النقاط_الكلية" in hdrs:
                        ws.update_cell(i, hdrs.index("النقاط_الكلية")+1, round(new_total,2))
                    if "الحالة" in hdrs:
                        ws.update_cell(i, hdrs.index("الحالة")+1, new_status)
                    return True
    except Exception:
        pass
    for f in Path("data/submissions").glob(f"{username}_*.json"):
        try:
            with open(f, encoding="utf-8") as fp: d = json.load(fp)
            d["breakdown"]   = new_scores
            d["total_score"] = new_total
            d["status"]      = new_status
            with open(f, "w", encoding="utf-8") as fp:
                json.dump(d, fp, ensure_ascii=False, indent=2)
            return True
        except: pass
    return False


def _review_card(row):
    """بطاقة مراجعة مترشح واحد"""
    username  = row["اسم_المستخدم"]
    links     = _parse_json(row["روابط_الوثائق"])
    breakdown = _parse_json(row["تفصيل_النقاط"])

    # ── الوثائق ──────────────────────────────────
    if links:
        st.markdown("**📎 وثائق المترشح:**")
        cols = st.columns(4)
        ci = 0
        for dk, link in links.items():
            if link and str(link).startswith("http"):
                label = LABEL_MAP.get(dk, dk.replace("_"," "))
                with cols[ci % 4]:
                    st.markdown(
                        f'<a href="{link}" target="_blank" style="display:block;'
                        f'padding:5px 8px;background:#f0f4fa;border:1px solid #dce3ee;'
                        f'border-radius:6px;font-size:.78rem;color:#1a3a5c;'
                        f'text-decoration:none;margin-bottom:5px;">🔗 {label}</a>',
                        unsafe_allow_html=True)
                ci += 1
        st.markdown("---")

    # ── تعديل النقاط ─────────────────────────────
    st.markdown("**✏️ مراجعة النقاط — النقطة الأولية | النقطة النهائية:**")

    new_scores = {}
    if breakdown:
        for label, pts in breakdown.items():
            c1, c2, c3 = st.columns([3, 1, 1.5])
            with c1:
                st.markdown(f'<div style="padding:4px 0;font-size:.9rem;">{label}</div>',
                            unsafe_allow_html=True)
            with c2:
                if pts is None:
                    orig = 0.0
                    st.markdown('<div style="text-align:center;color:#c8973a;">⏳</div>',
                                unsafe_allow_html=True)
                else:
                    try:
                        orig = float(pts)
                        col  = "#e74c3c" if orig < 0 else "#27ae60"
                        st.markdown(
                            f'<div style="text-align:center;font-weight:700;color:{col};">{orig:+.1f}</div>',
                            unsafe_allow_html=True)
                    except:
                        orig = 0.0
                        st.markdown('<div style="text-align:center;">—</div>', unsafe_allow_html=True)
            with c3:
                new_val = st.number_input(
                    "ن", min_value=-50.0, max_value=100.0,
                    value=float(orig), step=0.5,
                    key=f"nv_{username}_{label}",
                    label_visibility="collapsed"
                )
            new_scores[label] = new_val
            st.markdown('<div style="border-bottom:.5px solid #f0f0f0;margin:.1rem 0;"></div>',
                        unsafe_allow_html=True)
    else:
        # لا تفصيل — نقطة كلية فقط
        st.markdown('<div class="alert al-wn" style="font-size:.82rem;">لا يوجد تفصيل — أدخل النقطة الكلية مباشرة.</div>',
                    unsafe_allow_html=True)
        new_val = st.number_input(
            "النقطة الكلية النهائية",
            min_value=0.0, max_value=100.0,
            value=float(row["النقاط_الكلية"]), step=0.5,
            key=f"total_{username}"
        )
        new_scores = {"النقطة الكلية": new_val}

    # المجموع
    new_total = round(sum(float(v) for v in new_scores.values()), 2)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f'<div style="text-align:center;padding:.7rem;background:#f8f9fa;border-radius:8px;">'
            f'<div style="font-size:.75rem;color:#6b7f96;">النقاط الأولية</div>'
            f'<div style="font-size:1.3rem;font-weight:800;color:#c8973a;">{row["النقاط_الكلية"]:.1f}</div></div>',
            unsafe_allow_html=True)
    with c2:
        st.markdown(
            f'<div style="text-align:center;padding:.7rem;background:linear-gradient(135deg,#0d1f35,#1a3a5c);border-radius:8px;">'
            f'<div style="font-size:.75rem;color:rgba(255,255,255,.7);">المجموع النهائي</div>'
            f'<div style="font-size:1.3rem;font-weight:800;color:#27ae60;">{new_total:.1f}</div></div>',
            unsafe_allow_html=True)

    st.markdown("---")
    cur_idx    = STATUS_OPTIONS.index(row["الحالة"]) if row["الحالة"] in STATUS_OPTIONS else 0
    new_status = st.selectbox("النتيجة:", STATUS_OPTIONS, index=cur_idx,
                               key=f"status_{username}")

    if st.button("💾 حفظ المراجعة", use_container_width=True, key=f"save_{username}"):
        if _save(username, new_scores, new_total, new_status):
            st.success(f"✅ تم — المجموع: {new_total:.1f} | الحالة: {new_status}")
            st.rerun()
        else:
            st.error("❌ فشل الحفظ")


def show_committee():
    st.markdown(f"""
    <div class="gov-header">
      <div style="font-size:.74rem;opacity:.6;margin-bottom:.2rem;">
        الجمهورية الجزائرية الديمقراطية الشعبية — وزارة التعليم العالي والبحث العلمي
      </div>
      <h1>👥 لوحة لجنة الانتقاء</h1>
      <p>كلية الحقوق والعلوم السياسية — جامعة محمد البشير الإبراهيمي برج بوعريريج</p>
      <span class="badge b-blue">{st.session_state.user_name}</span>
    </div>
    """, unsafe_allow_html=True)

    _, cx = st.columns([5,1])
    with cx:
        if st.button("🚪 خروج", use_container_width=True): _logout()

    with st.spinner("جارٍ تحميل..."):
        df = _load_df()

    if df.empty:
        st.markdown('<div class="alert al-in">📭 لا توجد ملفات مقدَّمة بعد.</div>',
                    unsafe_allow_html=True)
        return

    # إحصائيات
    c1,c2,c3,c4 = st.columns(4)
    for col,(val,color,label) in zip([c1,c2,c3,c4],[
        (len(df),"#1a3a5c","إجمالي الملفات"),
        (len(df[df["الحالة"]=="مقبول"]),"#27ae60","مقبول"),
        (len(df[df["الحالة"]=="قيد المراجعة"]),"#c8973a","قيد المراجعة"),
        (len(df[df["الحالة"]=="مرفوض"]),"#e74c3c","مرفوض"),
    ]):
        with col:
            st.markdown(
                f'<div class="card"><div style="font-size:1.8rem;font-weight:800;color:{color};">{val}</div>'
                f'<div style="font-size:.82rem;color:#6b7f96;">{label}</div></div>',
                unsafe_allow_html=True)

    # تبويب لكل صيغة + تصدير
    tab_names = [s[0] for s in SILKS] + ["📥 تصدير"]
    tabs = st.tabs(tab_names)

    for tab, (tab_name, silk_val) in zip(tabs[:-1], SILKS):
        with tab:
            silk_df = df[df["السلك"]==silk_val].copy()

            if silk_df.empty:
                st.markdown('<div class="alert al-in">📭 لا توجد ملفات لهذه الصيغة.</div>',
                            unsafe_allow_html=True)
                continue

            st.markdown(f"**{len(silk_df)} ملف مقدَّم**")

            for _, row in silk_df.iterrows():
                sc = {"مقبول":"🟢","مرفوض":"🔴","قائمة انتظار":"🔵","قيد المراجعة":"🟡"}.get(row["الحالة"],"⚪")
                with st.expander(
                    f"{sc} {row['الاسم_الكامل']} | {row['الرتبة']} | "
                    f"نقاط: {row['النقاط_الكلية']:.1f} | {row['الحالة']} | {row['التاريخ']}"
                ):
                    _review_card(row)

    # تصدير
    with tabs[-1]:
        show = ["الاسم_الكامل","السلك","الرتبة","النقاط_الجزئية","النقاط_الكلية","الحالة"]
        ex = df.copy()
        # تصدير مفصّل لكل صيغة
        for tab_name, silk_val in SILKS:
            silk_ex = ex[ex["السلك"]==silk_val][show]
            if not silk_ex.empty:
                st.markdown(f"**{tab_name}**")
                st.dataframe(silk_ex, use_container_width=True)

        st.markdown("---")
        ex_all = ex[show]
        c1,c2 = st.columns(2)
        with c1:
            st.download_button(
                "📥 تحميل CSV الكل",
                data=ex_all.to_csv(encoding="utf-8-sig",index=False).encode("utf-8-sig"),
                file_name=f"المترشحون_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True
            )
        with c2:
            try:
                import io, openpyxl
                from openpyxl.styles import Font, PatternFill, Alignment
                from openpyxl.utils import get_column_letter
                wb = openpyxl.Workbook()
                wb.remove(wb.active)
                STATUS_FILL = {"مقبول":"E8F8F0","مرفوض":"FDECEA",
                               "قائمة انتظار":"E6F1FB","قيد المراجعة":"FEF9EC"}
                for tab_name, silk_val in SILKS:
                    silk_ex = ex[ex["السلك"]==silk_val][show]
                    if silk_ex.empty: continue
                    ws = wb.create_sheet(title=silk_val[:31])
                    for ci, h in enumerate(show, 1):
                        c = ws.cell(1, ci, h)
                        c.font = Font(bold=True,color="FFFFFF",name="Arial")
                        c.fill = PatternFill("solid",fgColor="1A3A5C")
                        c.alignment = Alignment(horizontal="center",vertical="center")
                        ws.column_dimensions[get_column_letter(ci)].width = 22
                    for ri, (_, row) in enumerate(silk_ex.iterrows(), 2):
                        fc = PatternFill("solid",fgColor=STATUS_FILL.get(str(row.get("الحالة","")),"FFFFFF"))
                        for ci, col in enumerate(show, 1):
                            cell = ws.cell(ri, ci, row.get(col,""))
                            cell.fill = fc
                            cell.alignment = Alignment(horizontal="center",vertical="center")
                buf = io.BytesIO(); wb.save(buf)
                st.download_button(
                    "📥 تحميل Excel (صيغة لكل ورقة)",
                    data=buf.getvalue(),
                    file_name=f"المترشحون_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"خطأ Excel: {e}")
