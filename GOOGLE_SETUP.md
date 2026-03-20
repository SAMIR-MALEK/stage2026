# دليل إعداد Google API
# كلية الحقوق والعلوم السياسية — جامعة برج بوعريريج

## ما ستحصل عليه بعد الإعداد
- **Google Sheets**: يُنشأ تلقائياً باسم `منصة_الانتقاء_BJB_2026`
  - ورقة `الطلبات`: كل بيانات المترشحين + نقاطهم
  - ورقة `المستخدمون`: أسماء المستخدمين وكلمات المرور
- **Google Drive**: مجلد `منصة_الانتقاء_BJB_2026`
  - مجلد لكل مترشح يحتوي وثائقه مرتبة

---

## الخطوات (20 دقيقة)

### 1. إنشاء مشروع Google Cloud
1. اذهب إلى: https://console.cloud.google.com
2. انقر **Select a project** ← **NEW PROJECT**
3. الاسم: `منصة-انتقاء-bjb` ← انقر **CREATE**

### 2. تفعيل APIs
1. من القائمة: **APIs & Services** ← **Library**
2. ابحث عن **Google Sheets API** ← انقر **ENABLE**
3. ابحث عن **Google Drive API** ← انقر **ENABLE**

### 3. إنشاء Service Account
1. اذهب إلى: **APIs & Services** ← **Credentials**
2. انقر: **+ CREATE CREDENTIALS** ← **Service Account**
3. الاسم: `منصة-bjb-service`
4. انقر **CREATE AND CONTINUE**
5. Role: اختر **Editor** ← انقر **DONE**

### 4. تحميل ملف JSON
1. انقر على الـ Service Account الذي أنشأته
2. تبويب **KEYS** ← **ADD KEY** ← **Create new key**
3. اختر **JSON** ← انقر **CREATE**
4. سيُحمَّل ملف JSON تلقائياً — **لا تشاركه مع أحد!**

### 5. إضافة Secrets في Streamlit Cloud
1. اذهب إلى تطبيقك على share.streamlit.io
2. انقر **Settings** ← **Secrets**
3. الصق هذا المحتوى (مع بياناتك الحقيقية من ملف JSON):

```toml
[google_credentials]
type = "service_account"
project_id = "YOUR_PROJECT_ID"
private_key_id = "YOUR_KEY_ID"
private_key = "-----BEGIN RSA PRIVATE KEY-----\nYOUR_KEY\n-----END RSA PRIVATE KEY-----\n"
client_email = "منصة-bjb-service@YOUR_PROJECT.iam.gserviceaccount.com"
client_id = "YOUR_CLIENT_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "YOUR_CERT_URL"
```

4. انقر **Save** ← أعد تشغيل التطبيق

### 6. التحقق من الإعداد
بعد إعادة التشغيل:
- ادخل بحساب **admin** ← **Adm@2026**
- اذهب إلى لوحة الإدارة ← تبويب **Google API**
- يجب أن تظهر ✅ بجانب Sheets و Drive

---

## ما يحدث تلقائياً عند أول دخول
1. المنصة تُنشئ الشيت `منصة_الانتقاء_BJB_2026` تلقائياً
2. تُضاف ورقتان: `الطلبات` و `المستخدمون`
3. تُضاف بيانات المستخدمين الأوليين
4. عند رفع أي وثيقة → تُحفظ في Drive تحت مجلد المترشح

---

## للتطوير المحلي (على جهازك)
ضع ملف JSON في: `config/google_credentials.json`

```
منصة_bjb/
  └── config/
        └── google_credentials.json   ← لا ترفعه على GitHub!
```

ملف `.gitignore` يمنع رفعه تلقائياً.
