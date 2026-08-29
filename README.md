# Rawnaq FastAPI V11

FastAPI is now a real backend in the project.

## Run
1. `python -m venv .venv`
2. Windows: `.venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. `python -m uvicorn backend.main:app --reload`
5. Open `http://127.0.0.1:8000`

## API
- `GET /api/health`
- `POST /ask`

Example request:
```json
{"query":"عايزة عطر صيفي حريمي","exclude":[],"context":{}}
```

Gemini is optional. Add `GEMINI_API_KEY` to the environment to enable AI-generated advice. Without it, FastAPI still works with local recommendation replies.
