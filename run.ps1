Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "Starting SmartMetrology System" -ForegroundColor Green
Write-Host "AI-Powered Legal Metrology Compliance Inspection & Tamper-Evident Ledger" -ForegroundColor Yellow
Write-Host "======================================================="

# Launch backend in separate window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { Write-Host 'Starting SmartMetrology Backend...' -ForegroundColor Cyan; .\venv\Scripts\python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload }"

Start-Sleep -Seconds 3

# Launch frontend in separate window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { Write-Host 'Starting SmartMetrology Frontend...' -ForegroundColor Green; cd frontend; npm run dev }"

Write-Host "`nBackend active at: http://127.0.0.1:8000 (API Docs at http://127.0.0.1:8000/docs)" -ForegroundColor Cyan
Write-Host "Frontend active at: http://localhost:5173" -ForegroundColor Green
