from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from backend.search import search_perfumes,detect
from backend.generate_advice import generate_advice

BASE=Path(__file__).resolve().parent.parent
FRONT=BASE/'frontend'
app=FastAPI(title='Rawnaq Perfume Recommendation API',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_methods=['*'],allow_headers=['*'])

class AskRequest(BaseModel):
    query:str=Field(min_length=1)
    exclude:list[str]=[]
    context:dict={}

def fmt(p):
    return {'name':p.get('name'),'type':p.get('type'),'season':p.get('season'),'scent_family':p.get('scent_family'),'price_premium_50ml':p.get('price_premium_50ml')}

def natural(q):
    s=' '.join(q.strip().lower().split())
    if 'السلام عليكم' in s: return 'وعليكم السلام ورحمة الله وبركاته 🤍 أهلاً بحضرتك في رونق للعطور، أقدر أساعد حضرتك إزاي؟'
    if any(x in s for x in ['اهلا','أهلا','هاي','hello','hi']) and len(s.split())<=4: return 'أهلاً بحضرتك في رونق للعطور 🤍 منورنا، أقدر أساعد حضرتك إزاي؟'
    if 'صباح الخير' in s: return 'صباح النور على حضرتك 🤍 أهلاً بيك في رونق. تحب أساعدك في اختيار عطر مناسب؟'
    if 'مساء الخير' in s: return 'مساء النور على حضرتك 🤍 أهلاً بيك في رونق. أقدر أساعد حضرتك إزاي؟'
    if any(x in s for x in ['ازيك','إزيك','عامل ايه','عامله ايه','اخبارك']): return 'الحمد لله بخير 🤍 منور رونق. تحب أساعدك تختار عطر مناسب ليك؟'
    if any(x in s for x in ['ساعدني','ساعديني','محتاج مساعده','محتاج مساعدة','عايز مساعدة']): return 'طبعاً، أنا موجود لمساعدتك ✨ قولي العطر لمين أو بتحب أي نوع من الروائح، ونختار سوا.'
    if any(x in s for x in ['شكرا','شكراً','متشكر','ميرسي','thanks']): return 'العفو، تحت أمرك في أي وقت 🤍 ونورت رونق.'
    if s in {'اه','ايوه','أيوه','تمام','ماشي','اوكي','أوكي','okay'}: return 'تمام 🤍 قولي تحب أساعدك تختار عطر، ولا عندك اسم عطر معين بتدور عليه؟'
    if s in {'لا','لأ'}: return 'تمام، تحت أمرك 🤍 لو احتجت أي مساعدة في العطور أنا موجود.'

@app.get('/api/health')
def health(): return {'status':'ok','service':'Rawnaq FastAPI'}

@app.post('/ask')
def ask(r:AskRequest):
    n=natural(r.query)
    if n: return {'query':r.query,'product':None,'advice':n,'other_products':[],'has_more':False,'context':r.context}
    res,ctx=search_perfumes(r.query,10,r.exclude,r.context)
    if not res:
        msg='مش لاقي اختيار مطابق للوصف ده حاليًا 🤍 بس أقدر أساعدك بطريقة تانية.' if (detect(r.query) or ctx) else 'أقدر أساعدك إزاي؟ ✨ ممكن تسألني عن اسم عطر أو تقولي مثلاً: صيفي حريمي، رجالي فريش.'
        return {'query':r.query,'product':None,'advice':msg,'other_products':[],'has_more':False,'context':ctx}
    top=res[0]
    return {'query':r.query,'product':fmt(top),'advice':generate_advice(r.query,top),'other_products':[fmt(p) for p in res[1:3]],'has_more':len(res)>1,'context':ctx}

app.mount('/assets',StaticFiles(directory=FRONT/'assets'),name='assets')

@app.get('/catalog.js')
def catalog(): return FileResponse(FRONT/'catalog.js',media_type='application/javascript')

@app.get('/')
def home(): return FileResponse(FRONT/'index.html')

@app.get('/{path:path}')
def fallback(path:str):
    f=FRONT/path
    return FileResponse(f if f.exists() and f.is_file() else FRONT/'index.html')
