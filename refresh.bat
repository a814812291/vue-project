@echo off
setlocal
set DATE_ARG=%1
if "%DATE_ARG%"=="" set DATE_ARG=auto
call .venv\Scripts\activate
python backend\refresh.py --date %DATE_ARG%
endlocal
