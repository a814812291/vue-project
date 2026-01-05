@echo off
setlocal
if not exist .venv (python -m venv .venv)
call .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python - <<PY
from backend.app.services import cache
cache.init_db()
print("DB ready at backend/app/data/cache.db")
PY
endlocal
