import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer

from settings import (
    CHROMA_PATH,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
)


model = SentenceTransformer(
    EMBEDDING_MODEL
)

client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)

try:
    collection = client.get_collection(
        name=COLLECTION_NAME
    )
except Exception as exc:
    raise RuntimeError(
        "قاعدة Chroma غير جاهزة. "
        "شغّل python prepare_data.py ثم "
        "python build_index.py قبل تشغيل الـ API."
    ) from exc


SEASON_ANCHORS = {
    "صيفي": "عطر مناسب لأجواء الصيف والحر",
    "شتوي": "عطر مناسب لأجواء الشتاء والبرد",
    "خريفي": "عطر مناسب لأجواء الخريف",
    "ربيعي": "عطر مناسب لأجواء الربيع",
}

SEASON_KEYWORDS = {
    "صيفي": [
        "صيف",
        "صيفي",
        "summer",
        "été",
        "ete",
    ],
    "شتوي": [
        "شتا",
        "شتاء",
        "شتوي",
        "winter",
        "hiver",
    ],
    "خريفي": [
        "خريف",
        "خريفي",
        "autumn",
        "fall",
        "automne",
    ],
    "ربيعي": [
        "ربيع",
        "ربيعي",
        "spring",
        "printemps",
    ],
}

_season_names = list(
    SEASON_ANCHORS.keys()
)

_season_embeddings = model.encode(
    list(SEASON_ANCHORS.values())
)

SEASON_SIMILARITY_THRESHOLD = 0.45


def cosine_similarity(a, b):
    denominator = (
        np.linalg.norm(a)
        * np.linalg.norm(b)
    )

    if denominator == 0:
        return 0.0

    return float(
        np.dot(a, b) / denominator
    )


def detect_season(user_query):
    text = str(user_query).lower()

    for season, keywords in (
        SEASON_KEYWORDS.items()
    ):
        if any(
            keyword.lower() in text
            for keyword in keywords
        ):
            return season

    query_embedding = model.encode(
        [user_query]
    )[0]

    best_season = None
    best_score = 0.0

    for (
        season,
        season_embedding,
    ) in zip(
        _season_names,
        _season_embeddings,
    ):
        score = cosine_similarity(
            query_embedding,
            season_embedding,
        )

        if score > best_score:
            best_score = score
            best_season = season

    if (
        best_score
        >= SEASON_SIMILARITY_THRESHOLD
    ):
        return best_season

    return None


def matches_season(
    product_season,
    target_season,
):
    if not product_season:
        return False

    value = str(product_season)

    return (
        target_season in value
        or "كل المواسم" in value
        or "كل موسم" in value
        or "يصلح لكل المواسم" in value
    )


def search_perfumes(
    user_query,
    top_k=3,
):
    if not str(user_query).strip():
        return []

    detected_season = detect_season(
        user_query
    )

    query_embedding = model.encode(
        [user_query]
    ).tolist()

    total_products = collection.count()

    if total_products == 0:
        return []

    initial_k = (
        min(20, total_products)
        if detected_season
        else min(top_k, total_products)
    )

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=initial_k,
    )

    if not results.get("ids"):
        return []

    all_matches = []

    for i in range(
        len(results["ids"][0])
    ):
        all_matches.append(
            {
                "product":
                    results["metadatas"][0][i],

                "distance":
                    results["distances"][0][i],
            }
        )

    if not detected_season:
        return all_matches[:top_k]

    filtered = [
        match
        for match in all_matches
        if matches_season(
            match["product"].get(
                "الموسم"
            ),
            detected_season,
        )
    ]

    if len(filtered) >= top_k:
        return filtered[:top_k]

    remaining = [
        match
        for match in all_matches
        if match not in filtered
    ]

    return (
        filtered + remaining
    )[:top_k]


if __name__ == "__main__":
    queries = [
        "عايز عطر دافي للشتا",
        "night summer perfume",
        "un parfum d'été",
    ]

    for query in queries:
        results = search_perfumes(
            query,
            top_k=3,
        )

        print(
            f"سؤال المستخدم: {query}\n"
        )

        for rank, match in enumerate(
            results,
            start=1,
        ):
            product = match["product"]

            print(
                f"{rank}. "
                f"{product['اسم_المنتج']} "
                f"| الموسم: "
                f"{product.get('الموسم', '')}"
            )

        print("-" * 50)
