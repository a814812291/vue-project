@echo off
setlocal enabledelayedexpansion
cd /d %~dp0

:: Detect python executable (python -> py -3)
set "PYTHON_CMD="
where python >nul 2>&1 && set "PYTHON_CMD=python"
if not defined PYTHON_CMD (
    where py >nul 2>&1 && set "PYTHON_CMD=py -3"
)
if not defined PYTHON_CMD (
    echo [ERROR] 未找到 Python 3.9+，请先安裝或將其加入 PATH。
    goto :pause
)

echo [INFO] Python 使用: %PYTHON_CMD%
if not exist .venv (
    echo [INFO] 正在创建虛擬環境 .venv ...
    %PYTHON_CMD% -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] 創建虛擬環境失敗。
        goto :pause
    )
)

call .venv\Scripts\activate
if %errorlevel% neq 0 (
    echo [ERROR] 無法激活虛擬環境 .venv。
    goto :pause
)

echo [INFO] 升級 pip 並安裝依賴...
%PYTHON_CMD% -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [ERROR] pip 升級失敗。
    goto :pause
)
%PYTHON_CMD% -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] 依賴安裝失敗，請檢查網絡或鏡像源。
    goto :pause
)

echo [INFO] 初始化 SQLite 數據庫...
%PYTHON_CMD% backend\init_db.py
if %errorlevel% neq 0 (
    echo [ERROR] 數據庫初始化失敗。
    goto :pause
)

echo [DONE] 安裝與初始化完成。
:pause
pause
endlocal
