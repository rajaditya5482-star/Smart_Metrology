@echo off
echo =======================================================
echo Starting SmartMetrology System
echo AI-Powered Legal Metrology Compliance Inspection & Tamper-Evident Ledger
echo =======================================================

start cmd /k "title SmartMetrology Backend && .\venv\Scripts\python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 3 /nobreak > nul
start cmd /k "title SmartMetrology Frontend && cd frontend && npm run dev"

echo.
echo Backend running on: http://127.0.0.1:8000
echo Frontend running on: http://localhost:5173
echo.
pause
