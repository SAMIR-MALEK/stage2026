"""لوحة لجنة الانتقاء — مبسّطة بتبويب لكل صيغة"""
import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

STATUS_OPTIONS = ["قيد المراجعة", "مقبول", "مرفوض", "قائمة انتظار"]

LABEL_MAP = {
    "tr_rank":"وثيقة الرتبة","rank_doc":"وثيقة الرتبة",
    "tr_reg_doc":"وثيقة التسجيل","tr_award_doc":"وثيقة الجائزة",
    "tr_sup_cert_0":"محضر دكتوراه 1","tr_sup_cert_1":"محضر دكتوراه 2",
    "tr_int_cert_0":"شهادة مداخلة 1","tr_int_cert_1":"شهادة مداخلة 2",
    "tr_pat_cert_0":"براءة اختراع 1","tr_proj_cert_0":"وثيقة مشروع 1",
    "tr_master_doc_1":"محاضر مناقشة ماستر","tr_lic_doc_1":"وثيقة إشراف ليسانس",
    "tr_shared_doc_1":"وثيقة جذع مشترك","high_doc":"وثيقة المنصب العالي",
    "adm_f1_istimara":"استمارة الترشح","adm_f1_mashrou3":"مشروع العمل","adm_f1_ta3ahod":"التعهد",
    "adm_f2_istimara":"استمارة الترشح","adm_f2_mashrou3":"مشروع العمل","adm_f2_ta3ahod":"التعهد",
    "adm_f3_istimara":"استمارة الترشح","adm_f3_mashrou3":"مشروع العمل",
    "adm_f3_ta3ahod":"التعهد","adm_f3_tasrih":"التصريح الشرفي",
    "adm_f4_istimara":"استمارة الترشح","adm_f4_mashrou3":"مشروع العمل","adm_f4_ta3ahod":"التعهد",
    "taheel_doc":"تعهد التأهيل",
}

SILKS = {
    "صيغة 1 — أساتذة محاضرون":   "أساتذة محاضرون",
    "صيغة 2 — أساتذة مساعدون":   "أساتذة مساعدون",
    "صيغة 3 — طلبة دكتوراه":     "طلبة دكتوراه",
    "صيغة 4 — إداريون وتقنيون":  "إداريون وتقنيون",
}


def _logout():
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()


def _safe_float(v):
    try:
        return float(str(v).replace(",","").replace(" ","")) if v not in ("","None",None) else 0.0
    except:
        return 0.0


def _load_all() -> list[dict]:
    records = []
    try:
        from utils.sheets import _get_client, SHEET_NAME
        cl = _get_client()
        if cl:
            recs = cl.open(SHEET_NAME).sheet1.get_all_records()
            if recs: return recs
    except Exception:
        pass
    sub = Path("data/submissions")
    if sub.exists():
        for f in sorted(sub.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                with open(f, encoding="utf-8") as fp:
                    d = json.load(fp); d["_file"] = str(f); records.append(d)
            except Exception:
                pass
    return records


def _normalize(raw):
    rows = []
    for r in raw:
        rows.append({
            "اسم_المستخدم":   str(r.get("اسم_المستخدم", r.get("username",""))).strip(),
            "الاسم_الكامل":   str(r.get("الاسم_الكامل", r.get("name",""))).strip(),
            "السلك":          str(r.get("السلك",  r.get("silk",""))).strip(),
            "الرتبة":         str(r.get("الرتبة", r.get("rank",""))).strip(),
            "الصيغة":         str(r.get("الصيغة", r.get("scale",""))).strip(),
            "النقاط_الجزئية": _safe_float(r.get("النقاط_الجزئية", r.get("total_score",0))),
            "نقاط_الرتبة":   _safe_float(r.get("نقاط_الرتبة",  r.get("rank_pts",0))),
            "النقاط_الكلية": _safe_float(r.get("النقاط_الكلية", r.get("total_score",0))),
            "الحالة":         str(r.get("الحالة",  r.get("status","قيد المراجعة"))).strip(),
            "التاريخ":        str(r.get("التاريخ","")).strip(),
            "التفصيل":        str(r.get("تفصيل_النقاط", r.get("breakdown","{}")) or "{}"),
            "روابط_Drive":    str(r.get("روابط_الوثائق", r.get("drive_links","{}")) or "{}"),
        })
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def _save_review(username, new_scores, new_total, new_status):
    try:
        from utils.sheets import _get_client, SHEET_NAME
        cl = _get_client()
        if cl:
            ws   = cl.open(SHEET_NAME).sheet1
            recs = ws.get_all_records()
            hdrs = list(recs[0].keys()) if recs else []
            for idx, rec in enumerate(recs, 2):
                if str(rec.get("اسم_المستخدم","")).strip() == username:
                    if "تفصيل_النقاط" in hdrs:
                        ws.update_cell(idx, hdrs.index("تفصيل_النقاط")+1,
                                       json.dumps(new_scores, ensure_ascii=False))
                    if "النقاط_الكلية" in hdrs:
                        ws.update_cell(idx, hdrs.index("النقاط_الكلية")+1, round(new_total,2))
                    if "الحالة" in hdrs:
                        ws.update_cell(idx, hdrs.index("الحالة")+1, new_status)
                    return True
    except Exception:
        pass
    # محلي
    sub = Path("data/submissions")
    if sub.exists():
        for f in sub.glob(f"{username}_*.json"):
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


def _candidate_review(row):
    """واجهة مراجعة مترشح واحد"""
    username = row["اسم_المستخدم"]

    # قراءة الوثائق والتفصيل
    try:
        links = json.loads(row.get("روابط_Drive","{}") or "{}")
    except:
        links = {}
    try:
        breakdown = json.loads(row.get("التفصيل","{}") or "{}")
    except:
        breakdown = {}

    st.markdown(f"""
    <div class="card">
      <div class="card-title">📋 {row['الاسم_الكامل']} — {row['الرتبة']}</div>
      <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:.5rem;">
        <span class="badge b-gold">{row['السلك']}</span>
        <span class="badge b-blue">{row['التاريخ']}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── الوثائق ──────────────────────────────────
    if links and any(v for v in links.values()):
        st.markdown('<div class="card"><div class="card-title">📎 وثائق المترشح</div>',
                    unsafe_allow_html=True)
        cols = st.columns(3)
        for i, (doc_key, link) in enumerate(links.items()):
            display = LABEL_MAP.get(doc_key, doc_key.replace("_"," "))
            if link and str(link).startswith("http"):
                with cols[i % 3]:
                    st.markdown(
                        f'<a href="{link}" target="_blank" style="display:block;padding:6px 10px;'
                        f'background:#f0f4fa;border:1px solid #dce3ee;border-radius:6px;'
                        f'font-size:.82rem;color:#1a3a5c;text-decoration:none;margin-bottom:6px;">'
                        f'🔗 {display}</a>',
                        unsafe_allow_html=True
                    )
        st.markdown('</div>', unsafe_allow_html=True)

    # ── تعديل النقاط ─────────────────────────────
    st.markdown('<div class="card"><div class="card-title">✏️ مراجعة النقاط</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div style="display:grid;grid-template-columns:3fr 1fr 1fr;gap:0;
                font-size:.82rem;font-weight:500;color:#6b7f96;
                padding:6px 8px;border-bottom:2px solid #1a3a5c;margin-bottom:4px;">
      <span>المعيار</span><span style="text-align:center">النقطة الأولية</span>
      <span style="text-align:center">النقطة النهائية</span>
    </div>
    """, unsafe_allow_html=True)

    new_scores = {}
    if breakdown:
        for label, pts in breakdown.items():
            c1, c2, c3 = st.columns([3, 1, 1.2])
            with c1:
                st.markdown(f'<div style="padding:.3rem .5rem;font-size:.9rem;">{label}</div>',
                            unsafe_allow_html=True)
            with c2:
                if pts is None:
                    st.markdown('<div style="text-align:center;color:#c8973a;padding:.3rem;">⏳</div>',
                                unsafe_allow_html=True)
                    orig = 0.0
                else:
                    try:
                        orig = float(pts)
                        col  = "#e74c3c" if orig < 0 else "#1a3a5c"
                        st.markdown(f'<div style="text-align:center;font-weight:600;color:{col};padding:.3rem;">{orig:+.1f}</div>',
                                    unsafe_allow_html=True)
                    except:
                        orig = 0.0
            with c3:
                new_val = st.number_input(
                    "ن", min_value=-20.0, max_value=100.0,
                    value=float(orig), step=0.5,
                    key=f"nv_{username}_{label}",
                    label_visibility="collapsed"
                )
            new_scores[label] = new_val
            st.markdown('<div style="border-bottom:.5px solid #f0f2f5;"></div>',
                        unsafe_allow_html=True)
    else:
        st.info("لا يوجد تفصيل للنقاط.")

    # المجموع
    new_total = round(sum(float(v) for v in new_scores.values() if isinstance(v,(int,float))), 2)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div style="text-align:center;padding:.8rem;background:#f8f9fa;border-radius:8px;"><div style="font-size:.78rem;color:#6b7f96;">النقاط الأولية</div><div style="font-size:1.4rem;font-weight:800;color:#c8973a;">{row["النقاط_الكلية"]:.1f}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div style="text-align:center;padding:.8rem;background:linear-gradient(135deg,#0d1f35,#1a3a5c);border-radius:8px;"><div style="font-size:.78rem;color:rgba(255,255,255,.7);">المجموع النهائي</div><div style="font-size:1.4rem;font-weight:800;color:#27ae60;">{new_total:.1f}</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # الحالة + الحفظ
    st.markdown('<div class="card">', unsafe_allow_html=True)
    cur_idx = STATUS_OPTIONS.index(row["الحالة"]) if row["الحالة"] in STATUS_OPTIONS else 0
    new_status = st.selectbox("النتيجة النهائية:", STATUS_OPTIONS,
                               index=cur_idx, key=f"status_{username}")
    if st.button("💾 حفظ المراجعة النهائية", use_container_width=True,
                 key=f"save_{username}"):
        if _save_review(username, new_scores, new_total, new_status):
            st.success(f"✅ تم الحفظ — المجموع: {new_total:.1f} — الحالة: {new_status}")
            st.rerun()
        else:
            st.error("❌ فشل الحفظ")
    st.markdown('</div>', unsafe_allow_html=True)


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

    _, c2 = st.columns([5,1])
    with c2:
        if st.button("🚪 خروج", use_container_width=True): _logout()

    with st.spinner("جارٍ تحميل الملفات..."):
        raw = _load_all()
        df  = _normalize(raw)

    if df.empty:
        st.markdown('<div class="alert al-in">📭 لا توجد ملفات مقدَّمة بعد.</div>',
                    unsafe_allow_html=True)
        return

    # إحصائيات سريعة
    c1,c2,c3,c4 = st.columns(4)
    for col,(val,color,label) in zip([c1,c2,c3,c4],[
        (len(df),"#1a3a5c","إجمالي الملفات"),
        (len(df[df["الحالة"]=="مقبول"]),"#27ae60","مقبول"),
        (len(df[df["الحالة"]=="قيد المراجعة"]),"#c8973a","قيد المراجعة"),
        (len(df[df["الحالة"]=="مرفوض"]),"#e74c3c","مرفوض"),
    ]):
        with col:
            st.markdown(f'<div class="card"><div style="font-size:1.8rem;font-weight:800;color:{color};">{val}</div><div style="font-size:.82rem;color:#6b7f96;">{label}</div></div>', unsafe_allow_html=True)

    # تبويب لكل صيغة + تصدير
    tab_labels = list(SILKS.keys()) + ["📥 تصدير"]
    tabs = st.tabs(tab_labels)

    for tab, (tab_label, silk_val) in zip(tabs[:-1], SILKS.items()):
        with tab:
            silk_df = df[df["السلك"]==silk_val].copy() if not df.empty else pd.DataFrame()

            if silk_df.empty:
                st.markdown('<div class="alert al-in">📭 لا توجد ملفات لهذه الصيغة بعد.</div>',
                            unsafe_allow_html=True)
                continue

            # جدول ملخص
            st.markdown(f"**{len(silk_df)} ملف مقدَّم**")

            # عرض كل مترشح كبطاقة قابلة للتوسع
            for _, row in silk_df.iterrows():
                status_colors = {
                    "مقبول":"#27ae60","مرفوض":"#e74c3c",
                    "قائمة انتظار":"#185fa5","قيد المراجعة":"#c8973a"
                }
                sc = status_colors.get(row["الحالة"],"#6b7f96")
                with st.expander(
                    f"👤 {row['الاسم_الكامل']} — {row['الرتبة']} | "
                    f"النقاط: {row['النقاط_الكلية']:.1f} | "
                    f"الحالة: {row['الحالة']}"
                ):
                    _candidate_review(row)

    # تبويب التصدير
    with tabs[-1]:
        ex = df.sort_values("النقاط_الكلية", ascending=False).reset_index(drop=True)
        ex.index += 1; ex.index.name = "الترتيب"
        show = ["الاسم_الكامل","السلك","الرتبة","النقاط_الجزئية","نقاط_الرتبة","النقاط_الكلية","الحالة"]
        st.dataframe(ex[show], use_container_width=True)

        c1,c2 = st.columns(2)
        with c1:
            st.download_button(
                "📥 تحميل CSV",
                data=ex[show].to_csv(encoding="utf-8-sig",index=True).encode("utf-8-sig"),
                file_name=f"المترشحون_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True
            )
        with c2:
            try:
                import io, openpyxl
                from openpyxl.styles import Font, PatternFill, Alignment
                from openpyxl.utils import get_column_letter
                wb = openpyxl.Workbook(); ws = wb.active; ws.title = "قائمة المترشحين"
                hdrs = ["الترتيب"] + show
                for ci, h in enumerate(hdrs, 1):
                    c = ws.cell(1, ci, h)
                    c.font = Font(bold=True, color="FFFFFF", name="Arial", size=11)
                    c.fill = PatternFill("solid", fgColor="1A3A5C")
                    c.alignment = Alignment(horizontal="center", vertical="center")
                    ws.column_dimensions[get_column_letter(ci)].width = 20
                STATUS_FILL = {"مقبول":"E8F8F0","مرفوض":"FDECEA",
                               "قائمة انتظار":"E6F1FB","قيد المراجعة":"FEF9EC"}
                for ri, (i, row) in enumerate(ex.iterrows(), 2):
                    vals = [i]+[row.get(c,"") for c in show]
                    fc   = PatternFill("solid", fgColor=STATUS_FILL.get(str(row.get("الحالة","")),"FFFFFF"))
                    for ci, v in enumerate(vals, 1):
                        cell = ws.cell(ri, ci, v)
                        cell.fill = fc
                        cell.alignment = Alignment(horizontal="center", vertical="center")
                buf = io.BytesIO(); wb.save(buf)
                st.download_button(
                    "📥 تحميل Excel", data=buf.getvalue(),
                    file_name=f"المترشحون_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"خطأ Excel: {e}")
