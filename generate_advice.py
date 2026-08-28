import os
import time

from google import genai

from settings import GEMINI_MODEL


_api_key = os.getenv("GEMINI_API_KEY")

client = (
    genai.Client(api_key=_api_key)
    if _api_key
    else None
)


def fallback_advice(user_query, product):
    name = product.get(
        "اسم_المنتج",
        "العطر المقترح",
    )

    season = product.get(
        "الموسم",
        "كل المواسم",
    )

    scent_family = product.get(
        "التصنيف العطري",
        "تصنيف متنوع",
    )

    return (
        f"أرشحلك {name} لأنه من فئة "
        f"{scent_family} ومناسب لـ {season}. "
        "اختيار لطيف كبداية حسب المواصفات "
        "اللي طلبتها. "
        "تحب تشوف اقتراح تاني؟"
    )


def generate_advice(
    user_query,
    matched_products,
    max_retries=3,
):
    if not matched_products:
        return (
            "مش لاقي منتج مناسب حالياً."
        )

    match = matched_products[0]
    product = match["product"]

    if client is None:
        return fallback_advice(
            user_query,
            product,
        )

    product_context = f"""
المنتج: {product.get('اسم_المنتج', '')}
- النوع: {product.get('النوع', '')}
- الموسم المناسب: {product.get('الموسم', '')}
- التصنيف العطري: {product.get('التصنيف العطري', '')}
- النوتات: {product.get('النوتات الرئيسية', '')}
- درجة الحلاوة: {product.get('درجة الحلاوة', '')}
"""

    prompt = f"""
أنت مستشار عطور محترف لمتجر رونق.
اكتب نصيحة قصيرة وودودة بالعربي المصري
للعميل عن منتج واحد فقط.

سؤال العميل:
"{user_query}"

هذا هو المنتج المقترح.
اعتمد فقط على المعلومات الموجودة هنا،
ولا تخترع أي معلومة غير موجودة:

{product_context}

اشرح باختصار لماذا هذا العطر مناسب
لسؤال العميل، ومتى يفضل استخدامه
استناداً إلى بيانات الموسم والنوع فقط.

اكتب من 3 إلى 5 جمل كحد أقصى.
لا تذكر سعراً أو معلومة غير موجودة.
اختم بسؤال ودود:
هل يعجبه الاقتراح أم يريد خياراً آخر؟
""".strip()

    last_error = None

    for attempt in range(max_retries):
        try:
            response = (
                client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt,
                )
            )

            text = getattr(
                response,
                "text",
                None,
            )

            if text:
                return text.strip()

        except Exception as exc:
            last_error = exc

            print(
                f"محاولة {attempt + 1} "
                "فشلت في Gemini:",
                exc,
            )

            if attempt < max_retries - 1:
                time.sleep(2)

    print(
        "تم استخدام النص الاحتياطي "
        "بسبب خطأ Gemini:",
        last_error,
    )

    return fallback_advice(
        user_query,
        product,
    )
