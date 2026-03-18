"""دليل الإعداد خطوة بخطوة لـ Google API"""
import streamlit as st


def show():
    st.markdown("""
    <div class="gov-header">
        <h1>📖 دليل الإعداد الكامل</h1>
        <p>ربط المنصة بـ Google Sheets و Google Drive — خطوة بخطوة</p>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs([
        "1️⃣ المتطلبات",
        "2️⃣ Google Cloud",
        "3️⃣ Service Account",
        "4️⃣ الشيت والـ Drive",
        "5️⃣ إعداد المشروع",
        "6️⃣ النشر على الإنترنت",
    ])

    # ── Tab 1: المتطلبات ───────────────────────────────────
    with tabs[0]:
        st.markdown("""
        <div class="form-section">
            <div class="form-section-title">🛠️ ما تحتاجه قبل البدء</div>
        """, unsafe_allow_html=True)

        reqs = [
            ("Python 3.9+", "تحميله من python.org", "✅"),
            ("pip", "مدير حزم Python (يأتي مع Python)", "✅"),
            ("حساب Google", "مفضلاً حساب مؤسساتي", "✅"),
            ("VS Code أو أي محرر", "لتعديل الكود", "✅"),
            ("اتصال بالإنترنت", "لتثبيت الحزم والاتصال بـ Google", "✅"),
        ]
        for name, desc, icon in reqs:
            st.markdown(f"""
            <div style='display:flex;gap:1rem;align-items:center;
                        padding:0.6rem;background:#f4f7fb;border-radius:8px;margin-bottom:0.4rem;'>
                <span style='font-size:1.2rem;'>{icon}</span>
                <div><strong>{name}</strong><br><span style='color:#6b7f96;font-size:0.85rem;'>{desc}</span></div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="form-section">
            <div class="form-section-title">📦 تثبيت المكتبات</div>
            <p>افتح Terminal أو CMD وانتقل لمجلد المشروع ثم نفّذ:</p>
        """, unsafe_allow_html=True)
        st.code("""
# 1. إنشاء بيئة افتراضية (موصى به)
python -m venv venv

# 2. تفعيل البيئة
# Windows:
venv\\Scripts\\activate
# Mac/Linux:
source venv/bin/activate

# 3. تثبيت المكتبات
pip install -r requirements.txt
        """, language="bash")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Tab 2: Google Cloud ────────────────────────────────
    with tabs[1]:
        st.markdown("""
        <div class="form-section">
            <div class="form-section-title">☁️ إنشاء مشروع على Google Cloud Console</div>
        """, unsafe_allow_html=True)

        steps = [
            ("افتح المتصفح وانتقل إلى:", "https://console.cloud.google.com"),
            ("سجّل الدخول بحساب Google الخاص بك.", ""),
            ("انقر على 'Select a project' في أعلى الصفحة", ""),
            ("انقر على 'NEW PROJECT'", ""),
            ("اكتب اسماً للمشروع مثل: `منصة-الانتقاء-2026`", ""),
            ("انقر 'CREATE' وانتظر لحظة", ""),
        ]
        for i, (step, link) in enumerate(steps, 1):
            st.markdown(f"""
            <div style='display:flex;gap:0.8rem;align-items:flex-start;
                        padding:0.7rem;background:#f4f7fb;border-radius:8px;margin-bottom:0.4rem;'>
                <div style='background:#1a3a5c;color:white;border-radius:50%;
                            width:26px;height:26px;display:flex;align-items:center;
                            justify-content:center;font-weight:700;font-size:0.8rem;flex-shrink:0;'>{i}</div>
                <div>{step}{f'<br><code style="color:#c8973a;">{link}</code>' if link else ''}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="form-section">
            <div class="form-section-title">🔌 تفعيل APIs المطلوبة</div>
            <p>من قائمة جانبية: <strong>APIs & Services → Library</strong></p>
            <p>ابحث وفعّل كلاً من:</p>
        """, unsafe_allow_html=True)

        apis = [
            ("Google Sheets API", "للقراءة والكتابة في الجداول"),
            ("Google Drive API", "لرفع وإدارة الملفات"),
        ]
        for api, desc in apis:
            st.markdown(f"""
            <div style='padding:0.6rem 1rem;background:#e8f4fd;border-right:4px solid #1a3a5c;
                        border-radius:8px;margin-bottom:0.4rem;'>
                <strong>{api}</strong> — <span style='color:#6b7f96;'>{desc}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Tab 3: Service Account ─────────────────────────────
    with tabs[2]:
        st.markdown("""
        <div class="form-section">
            <div class="form-section-title">🔑 إنشاء Service Account (حساب الخدمة)</div>
        """, unsafe_allow_html=True)

        steps = [
            "من القائمة: APIs & Services → Credentials",
            "انقر: + CREATE CREDENTIALS → Service Account",
            "أدخل اسماً مثل: `منصة-انتقاء-service`",
            "انقر 'CREATE AND CONTINUE'",
            "في قسم Role: اختر 'Editor' → انقر 'DONE'",
            "انقر على Service Account الذي أنشأته للتو",
            "اذهب إلى تبويب: KEYS",
            "انقر: ADD KEY → Create new key",
            "اختر: JSON → انقر CREATE",
            "سيتم تحميل ملف JSON تلقائياً — احفظه بأمان!",
        ]
        for i, step in enumerate(steps, 1):
            icon = "⚠️" if i == 10 else "▶️"
            st.markdown(f"""
            <div style='display:flex;gap:0.8rem;padding:0.5rem;
                        background:#f4f7fb;border-radius:6px;margin-bottom:3px;'>
                <span style='font-weight:700;color:#1a3a5c;min-width:1.5rem;'>{i}.</span>
                <span>{icon} {step}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="form-section">
            <div class="form-section-title">📋 شكل ملف JSON</div>
            <p>الملف الذي حُمِّل سيكون بهذا الشكل (لا تشاركه مع أحد!):</p>
        """, unsafe_allow_html=True)
        st.code("""{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN RSA PRIVATE KEY-----\\n...\\n-----END RSA PRIVATE KEY-----\\n",
  "client_email": "service@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}""", language="json")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Tab 4: الشيت والـ Drive ────────────────────────────
    with tabs[3]:
        st.markdown("""
        <div class="form-section">
            <div class="form-section-title">📊 إعداد Google Sheets</div>
        """, unsafe_allow_html=True)

        steps = [
            "اذهب إلى: drive.google.com",
            "انقر: + جديد → Google Sheets → جدول بيانات فارغ",
            "سمّه: منصة_الانتقاء_2026",
            "افتح ملف JSON الذي حمّلته وانسخ قيمة `client_email`",
            "في الشيت: انقر 'مشاركة' (زرود أخضر)",
            "الصق البريد الإلكتروني للـ Service Account",
            "اختر صلاحية: 'المحرر' → أرسل",
            "انسخ رابط الشيت (من شريط العنوان)",
        ]
        for i, step in enumerate(steps, 1):
            st.markdown(f"**{i}.** {step}")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="form-section">
            <div class="form-section-title">📁 إعداد Google Drive</div>
        """, unsafe_allow_html=True)

        st.markdown("""
        1. أنشئ مجلداً جديداً باسم: `منصة_الانتقاء_2026`
        2. شاركه مع بريد Service Account بصلاحية **المحرر**
        3. انسخ ID المجلد من الرابط: `https://drive.google.com/drive/folders/`**`FOLDER_ID`**
        """)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Tab 5: إعداد المشروع ──────────────────────────────
    with tabs[4]:
        st.markdown("""
        <div class="form-section">
            <div class="form-section-title">📁 هيكل المجلدات</div>
        """, unsafe_allow_html=True)
        st.code("""
منصة_الانتقاء/
├── app.py                      ← نقطة الدخول الرئيسية
├── requirements.txt            ← المكتبات
├── .streamlit/
│   └── secrets.toml            ← بيانات الاعتماد (لا ترفعها على GitHub!)
├── config/
│   └── google_credentials.json ← ملف JSON (للتطوير المحلي فقط)
├── pages/
│   ├── home.py
│   ├── login.py
│   ├── candidate_form.py
│   ├── my_scores.py
│   ├── committee_view.py
│   ├── admin_dashboard.py
│   └── setup_guide.py
├── utils/
│   ├── scoring.py
│   └── google_integration.py
└── data/                       ← نسخ احتياطية محلية
        """, language="text")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="form-section">
            <div class="form-section-title">🔐 ملف secrets.toml</div>
            <p>أنشئ مجلد <code>.streamlit</code> وداخله ملف <code>secrets.toml</code>:</p>
        """, unsafe_allow_html=True)
        st.code("""
[google_credentials]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "-----BEGIN RSA PRIVATE KEY-----\\n...\\n-----END RSA PRIVATE KEY-----\\n"
client_email = "service@your-project.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
        """, language="toml")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="form-section">
            <div class="form-section-title">▶️ تشغيل المنصة محلياً</div>
        """, unsafe_allow_html=True)
        st.code("""
# في مجلد المشروع
streamlit run app.py
        """, language="bash")
        st.success("✅ ستفتح المنصة تلقائياً على: http://localhost:8501")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Tab 6: النشر ──────────────────────────────────────
    with tabs[5]:
        st.markdown("""
        <div class="form-section">
            <div class="form-section-title">🌐 النشر على Streamlit Community Cloud (مجاناً)</div>
        """, unsafe_allow_html=True)

        steps = [
            ("إنشاء حساب GitHub", "ارفع كود المشروع على مستودع GitHub (بدون ملف secrets.toml أو JSON!)"),
            ("اذهب إلى share.streamlit.io", "سجّل الدخول بحساب GitHub"),
            ("انقر: New app", "اختر المستودع والملف الرئيسي (app.py)"),
            ("إضافة Secrets", "في إعدادات التطبيق → Secrets → الصق محتوى secrets.toml"),
            ("انقر Deploy", "انتظر دقيقتين وسيكون التطبيق متاحاً!"),
        ]
        for i, (title, desc) in enumerate(steps, 1):
            st.markdown(f"""
            <div style='padding:0.8rem;background:#f4f7fb;border-radius:10px;margin-bottom:0.5rem;
                        border-right:4px solid #c8973a;'>
                <strong style='color:#1a3a5c;'>{i}. {title}</strong><br>
                <span style='color:#6b7f96;font-size:0.9rem;'>{desc}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="form-section" style='background:#fef9ec; border:2px solid #c8973a;'>
            <div class="form-section-title" style='color:#7d6010;'>⚠️ ملفات يجب استثناؤها من GitHub</div>
        """, unsafe_allow_html=True)
        st.code("""
# أنشئ ملف .gitignore في جذر المشروع:

.streamlit/secrets.toml
config/google_credentials.json
data/
venv/
__pycache__/
*.pyc
        """, language="text")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="form-section">
            <div class="form-section-title">📞 المساعدة</div>
            <p>إذا واجهت أي مشكلة، يمكنك:</p>
            <ul>
                <li>مراجعة وثائق Streamlit: <code>docs.streamlit.io</code></li>
                <li>مراجعة وثائق gspread: <code>gspread.readthedocs.io</code></li>
                <li>التواصل مع إدارة المؤسسة</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
