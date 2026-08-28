# Rawnaq Perfume AI

مشروع رونق متكامل:
- Frontend HTML/CSS/JavaScript.
- زر "اطلب الآن" يفتح واتساب.
- مساعد عطور داخل الموقع.
- FastAPI Backend.
- Semantic Search باستخدام Sentence Transformers + ChromaDB.
- توليد نصيحة باستخدام Gemini.
- تنظيف وتجهيز بيانات Excel.

## 1. هيكل المشروع

```text
rawnaq-perfume-ai-project/
├── frontend/
│   ├── index.html
│   └── config.js
└── backend/
    ├── data/
    │   └── README.txt
    ├── main.py
    ├── search.py
    ├── generate_advice.py
    ├── prepare_data.py
    ├── build_index.py
    ├── inspect_excel.py
    ├── settings.py
    ├── requirements.txt
    └── .env.example
```

## 2. ضع ملف Excel

ضع الملف هنا:

```text
backend/data/كتالوج_بيع_البرفانات_والمسكات.xlsx
```

## 3. إنشاء البيئة وتثبيت المكتبات

من داخل مجلد `backend`:

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 4. إعداد Gemini

انسخ:

```text
.env.example
```

إلى:

```text
.env
```

ثم ضع المفتاح:

```env
GEMINI_API_KEY=YOUR_REAL_KEY
GEMINI_MODEL=gemini-3.6-flash
CORS_ORIGINS=*
```

لا ترفع `.env` إلى GitHub.

## 5. تجهيز البيانات وبناء ChromaDB

من داخل `backend`:

```bash
python prepare_data.py
python build_index.py
```

يتم إنشاء:

```text
backend/data/catalog_clean.xlsx
backend/chroma_db/
```

## 6. تشغيل الـ API

```bash
uvicorn main:app --reload
```

اختبار:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/docs
```

## 7. تشغيل الموقع

افتح Terminal داخل `frontend`:

```bash
python -m http.server 5500
```

ثم افتح:

```text
http://127.0.0.1:5500
```

الموقع مضبوط افتراضياً على:

```text
http://127.0.0.1:8000
```

## 8. بعد رفع الـ Backend

افتح:

```text
frontend/config.js
```

وغيّر:

```javascript
window.RAWNAQ_API_URL = "http://127.0.0.1:8000";
```

إلى رابط الـ Backend الحقيقي، مثل:

```javascript
window.RAWNAQ_API_URL = "https://your-api.onrender.com";
```

## 9. CORS عند النشر

في `.env` للـ Backend يفضل تغيير:

```env
CORS_ORIGINS=*
```

إلى دومين الموقع:

```env
CORS_ORIGINS=https://YOUR_USERNAME.github.io
```

لو عندك أكثر من origin افصل بينهم بفاصلة.

## 10. تجربة Endpoint مباشرة

```json
POST /ask

{
  "query": "عايز عطر رجالي صيفي فريش",
  "exclude": []
}
```

الـ frontend يحفظ أسماء الاقتراحات التي تم عرضها في جلسة الشات،
وعند الضغط على "اقتراح تاني" يرسلها في `exclude` حتى لا يكرر المنتج.

## ملاحظات

- ملف Excel الأصلي غير مرفق داخل النسخة لأن الملف نفسه لم يكن ضمن الملفات المرسلة هنا.
- لو `GEMINI_API_KEY` غير موجود، النظام لا يتوقف: سيعرض نصيحة احتياطية مبنية على بيانات المنتج.
- يجب بناء ChromaDB قبل تشغيل الـ API لأول مرة.
- `GEMINI_API_KEY` يجب أن يبقى في الـ Backend فقط، وليس في HTML أو JavaScript.
