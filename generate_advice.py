import os
try:
    from google import genai
except Exception:
    genai=None

def fallback(q,p):
    s=f"أرشحلك {p.get('name','المنتج ده')} ✨"
    if p.get('scent_family'): s+=f" طابعه {p['scent_family']}."
    if p.get('season'): s+=f" ومناسب لـ {p['season']}."
    return s+" تحب الاقتراح ده ولا أشوفلك اختيار تاني؟"

def generate_advice(q,p):
    key=os.getenv('GEMINI_API_KEY')
    if not key or genai is None: return fallback(q,p)
    try:
        client=genai.Client(api_key=key)
        prompt=(
            "أنت مساعد خدمة عملاء لمتجر رونق للعطور. اكتب رد عربي قصير وودود واعتمد فقط على البيانات التالية بدون اختراع معلومات.\n"
            f"سؤال العميل: {q}\nالاسم: {p.get('name')}\nالنوع: {p.get('type')}\nالموسم: {p.get('season')}\n"
            f"التصنيف: {p.get('scent_family')}\nالنوتات: {p.get('notes')}\nاختم بسؤال هل يريد اقتراحًا آخر."
        )
        r=client.models.generate_content(model=os.getenv('GEMINI_MODEL','gemini-2.5-flash'),contents=prompt)
        return (r.text or '').strip() or fallback(q,p)
    except Exception:
        return fallback(q,p)
