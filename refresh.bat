@echo off
setlocal enabledelayedexpansion
cd /d %~dp0

set DATE_ARG=%1
if "%DATE_ARG%"=="" set DATE_ARG=auto

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

echo [INFO] 正在刷新交易日 %DATE_ARG% 數據...
%PYTHON_CMD% backend\refresh.py --date %DATE_ARG%
if %errorlevel% neq 0 (
    echo [WARN] 刷新時出現錯誤，請檢查上方日誌（已降級可繼續使用）。
)

echo [DONE] 刷新流程結束。
:pause
pause
endlocal
