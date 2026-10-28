Write-Host "========================================================" -ForegroundColor Green
Write-Host "Starting AccessCraft - Adaptive Accessibility Generator" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green

$Root = $PSScriptRoot

# Start Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$Root'; `$env:PYTHONPATH='.'; & '$Root\backend\.venv\Scripts\python.exe' -m uvicorn backend.main:app --host 127.0.0.1 --port 8008"

# Start Frontend on dedicated port 5180
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$Root\frontend'; npm run dev -- --host 127.0.0.1 --port 5180"

Start-Sleep -Seconds 3

# Launch Browser
Start-Process "http://localhost:5180"

Write-Host "AccessCraft active at http://localhost:5180 (Backend: http://127.0.0.1:8008)" -ForegroundColor Cyan
