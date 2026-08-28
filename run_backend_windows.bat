@echo off
cd /d "%~dp0backend"

if not exist .venv (
    python -m venv .venv
)

call .venv\Scripts\activate
pip install -r requirements.txt

if not exist .env (
    copy .env.example .env
    echo.
    echo تم إنشاء .env - ضع GEMINI_API_KEY ثم شغل الملف مرة أخرى.
    pause
    exit /b
)

if not exist data\catalog_clean.xlsx (
    python prepare_data.py
)

if not exist chroma_db (
    python build_index.py
)

uvicorn main:app --reload
