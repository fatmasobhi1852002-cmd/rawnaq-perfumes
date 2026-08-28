import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
SOURCE_EXCEL = DATA_DIR / "كتالوج_بيع_البرفانات_والمسكات.xlsx"
CLEAN_EXCEL = DATA_DIR / "catalog_clean.xlsx"
CHROMA_PATH = BASE_DIR / "chroma_db"

COLLECTION_NAME = "perfumes"
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "paraphrase-multilingual-mpnet-base-v2",
)
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash",
)

CORS_ORIGINS = [
    item.strip()
    for item in os.getenv("CORS_ORIGINS", "*").split(",")
    if item.strip()
]
