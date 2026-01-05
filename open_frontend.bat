@echo off
setlocal
cd /d %~dp0
echo [INFO] 打開瀏覽器 http://127.0.0.1:8000 （請先運行 start_api.bat）
start http://127.0.0.1:8000
pause
endlocal
