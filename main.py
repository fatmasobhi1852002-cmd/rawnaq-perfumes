from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from generate_advice import generate_advice
from search import search_perfumes
from settings import CORS_ORIGINS


app = FastAPI(
    title="Rawnaq Perfume Recommendation API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=500,
    )

    exclude: list[str] = Field(
        default_factory=list
    )


def clean_value(value: Any):
    if value in (None, ""):
        return None

    return value


def format_product(product_dict):
    return {
        "name": clean_value(
            product_dict.get(
                "اسم_المنتج"
            )
        ),

        "type": clean_value(
            product_dict.get(
                "النوع"
            )
        ),

        "season": clean_value(
            product_dict.get(
                "الموسم"
            )
        ),

        "scent_family": clean_value(
            product_dict.get(
                "التصنيف العطري"
            )
        ),

        "price_premium_50ml":
            clean_value(
                product_dict.get(
                    "بريميوم 50 مل"
                )
            ),
    }


@app.post("/ask")
def ask(request: AskRequest):
    query = request.query.strip()

    results = search_perfumes(
        query,
        top_k=10,
    )

    excluded = {
        name.strip()
        for name in request.exclude
        if name and name.strip()
    }

    filtered = [
        match
        for match in results
        if (
            match["product"]
            .get("اسم_المنتج")
            not in excluded
        )
    ]

    if not filtered:
        return {
            "query": query,
            "product": None,
            "advice":
                "للأسف مفيش عطور تانية "
                "تناسب طلبك في الوقت الحالي.",

            "other_products": [],
            "has_more": False,
        }

    top_match = filtered[0]
    backup_matches = filtered[1:3]

    advice = generate_advice(
        query,
        [top_match],
    )

    return {
        "query": query,

        "product":
            format_product(
                top_match["product"]
            ),

        "advice": advice,

        "other_products": [
            format_product(
                match["product"]
            )
            for match in backup_matches
        ],

        "has_more":
            len(filtered) > 1,
    }


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message":
            "Rawnaq Perfume Recommendation "
            "API is running!",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
