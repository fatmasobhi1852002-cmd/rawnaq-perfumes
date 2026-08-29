import json,re
from pathlib import Path
CATALOG=json.loads((Path(__file__).parent/'data'/'catalog.json').read_text(encoding='utf-8'))

def norm(t):
    t=str(t or '').strip().lower()
    t=re.sub(r'[\u064b-\u065f\u0670]','',t)
    t=t.replace('أ','ا').replace('إ','ا').replace('آ','ا').replace('ى','ي').replace('ة','ه')
    t=re.sub(r'[^\u0600-\u06FFA-Za-z0-9\s]',' ',t)
    return re.sub(r'\s+',' ',t).strip()

INTENTS={
 'season':{'صيفي':['صيفي','صيف','summer','منعش'],'شتوي':['شتوي','شتا','شتاء','winter','دافي','دافئ'],'ربيعي':['ربيعي','ربيع','spring'],'خريفي':['خريفي','خريف','autumn','fall']},
 'gender':{'حريمي':['حريمي','نسائي','بناتي','women','woman','female'],'رجالي':['رجالي','للرجال','راجل','رجل','men','man','male'],'يونيسكس':['يونيسكس','للجنسين','للجميع','unisex']},
 'family':{'فريش':['فريش','منعش','fresh','اكواتك','بحري'],'فاكهي':['فاكهي','فواكه','fruity'],'زهري':['زهري','زهور','ورد','فلاوري','floral'],'خشبي':['خشبي','خشب','عودي','عود','woody'],'مسكي':['مسك','مسكي','musk'],'عنبري':['عنبر','عنبري','amber'],'حمضي':['حمضي','حمضيات','citrus'],'بودري':['بودري','بودرة','powdery'],'فانيليا':['فانيليا','vanilla'],'قهوة':['قهوة','قهوه','coffee']},
 'sweetness':{'حلو':['حلو','حلوة','سكري','شوغري','sweet'],'خفيف':['خفيف','هادي','هادئ','light'],'قوي':['قوي','تقيل','ثقيل','strong']}}

def detect(q):
    q=norm(q); out={}
    for g,vals in INTENTS.items():
        for v,ws in vals.items():
            if any(norm(w) in q for w in ws): out[g]=v; break
    return out

def ptext(p):
    return norm(' '.join(str(p.get(k,'')) for k in ['name','type','season','scent_family','notes','sweetness','search_text']))

def search_perfumes(query,top_k=3,exclude=None,context=None):
    ex=set(exclude or []); ctx=dict(context or {}); q=norm(query)
    cand=[p for p in CATALOG if p.get('name') not in ex]
    exact=[p for p in cand if norm(p.get('name'))==q]
    starts=[p for p in cand if norm(p.get('name')).startswith(q)]
    contains=[p for p in cand if q and q in norm(p.get('name'))]
    names=exact or starts or contains
    if names: return names[:top_k],ctx
    ctx.update(detect(query))
    if not ctx: return [],ctx
    scored=[]
    for p in cand:
        hay=ptext(p); req=mat=score=0
        for k,v in ctx.items():
            if not v: continue
            req+=1; vals=[v]
            if k=='season': vals += ['كل المواسم','يصلح لكل المواسم']
            if k=='gender': vals += ['يونيسكس','يناسب الجميع','للجنسين']
            if any(norm(x) in hay for x in vals): mat+=1; score+=20
        if req and mat==req: score+=100
        if mat: scored.append((score,mat,p))
    scored.sort(key=lambda x:(-x[0],-x[1],norm(x[2].get('name'))))
    return [x[2] for x in scored[:top_k]],ctx
