@echo off
setlocal enabledelayedexpansion
cd /d %~dp0

set "PYTHON_CMD="
where python >nul 2>&1 && set "PYTHON_CMD=python"
if not defined PYTHON_CMD (
    where py >nul 2>&1 && set "PYTHON_CMD=py -3"
)
if not defined PYTHON_CMD (
    echo [ERROR] 未找到 Python，請先運行 setup.bat 或安裝 Python。
    goto :pause
)

if not exist .venv (
    echo [ERROR] 未檢測到 .venv，請先運行 setup.bat。
    goto :pause
)

call .venv\Scripts\activate
if %errorlevel% neq 0 (
    echo [ERROR] 無法激活虛擬環境 .venv。
    goto :pause
)

echo [INFO] 啟動後端 API (http://127.0.0.1:8000)...
%PYTHON_CMD% -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
if %errorlevel% neq 0 (
    echo [ERROR] 後端啟動失敗，請檢查上方日誌。
)

:pause
pause
endlocal
