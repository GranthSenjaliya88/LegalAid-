# LegalAId — Backend Server Launcher for Windows PowerShell
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyans
Write-Host "Starting LegalAId Backend Service..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyans

Set-Location -Path "$PSScriptRoot\backend"

$pythonExe = "C:\Users\grant\AppData\Local\Programs\Python\Python312\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

$env:PYTHONPATH = "$PSScriptRoot\backend"

Write-Host "Server running at: http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "Swagger OpenAPI Docs: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "Readiness Health Check: http://127.0.0.1:8000/api/health/ready" -ForegroundColor Yellow
Write-Host "Press CTRL+C to stop the server.`n" -ForegroundColor Gray

& $pythonExe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
