@echo off
setlocal
call .venv\Scripts\activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
endlocal
