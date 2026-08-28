import math

import chromadb
import pandas as pd
from sentence_transformers import SentenceTransformer

from settings import (
    CLEAN_EXCEL,
    CHROMA_PATH,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
)


def sanitize_metadata(record):
    clean = {}

    for key, value in record.items():
        if pd.isna(value):
            clean[str(key)] = ""
            continue

        if isinstance(value, (str, int, float, bool)):
            if (
                isinstance(value, float)
                and not math.isfinite(value)
            ):
                clean[str(key)] = ""
            else:
                clean[str(key)] = value
        else:
            clean[str(key)] = str(value)

    return clean


def main():
    if not CLEAN_EXCEL.exists():
        raise FileNotFoundError(
            f"الملف النظيف غير موجود: {CLEAN_EXCEL}\n"
            "شغّل أولاً: python prepare_data.py"
        )

    df = pd.read_excel(CLEAN_EXCEL)

    if "نص_البحث" not in df.columns:
        raise ValueError(
            "عمود نص_البحث غير موجود في catalog_clean.xlsx"
        )

    print(f"عدد المنتجات: {len(df)}")
    print("جاري تحميل موديل الـ embeddings...")

    model = SentenceTransformer(
        EMBEDDING_MODEL
    )

    print("تم تحميل الموديل بنجاح")

    texts = (
        df["نص_البحث"]
        .fillna("")
        .astype(str)
        .tolist()
    )

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=False,
    )

    print(
        f"شكل المتجهات: {embeddings.shape}"
    )

    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH)
    )

    try:
        client.delete_collection(
            COLLECTION_NAME
        )
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={
            "embedding_model":
                EMBEDDING_MODEL
        },
    )

    metadata_records = [
        sanitize_metadata(record)
        for record
        in df.to_dict(orient="records")
    ]

    collection.add(
        ids=[
            str(i)
            for i in range(len(df))
        ],
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=metadata_records,
    )

    print(
        f"تم تخزين {collection.count()} منتج "
        "في قاعدة البيانات المتجهية بنجاح"
    )


if __name__ == "__main__":
    main()
