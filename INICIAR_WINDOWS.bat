@echo off
chcp 65001 > nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo Preparando entorno virtual Python 3.11...
 py -3.11 -m venv .venv
 if errorlevel 1 (python -m venv .venv)
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
 echo Error instalando dependencias. Compruebe internet y Python.
 pause
 exit /b 1
)
echo Swagger: http://127.0.0.1:8000/docs
echo Para terminar, pulse Ctrl+C.
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
