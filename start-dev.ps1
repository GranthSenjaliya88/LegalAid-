# LegalAId — Complete Dual Development Environment Launcher for Windows
$ErrorActionPreference = "Continue"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "       LegalAId Development Environment         " -ForegroundColor Yellow
Write-Host "  AI Legal Rights Assistant for Litigants in India " -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan

$pythonExe = "C:\Users\grant\AppData\Local\Programs\Python\Python312\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

Write-Host "`nRunning System Doctor Diagnostics..." -ForegroundColor Gray
$env:PYTHONPATH = "$PSScriptRoot\backend"
& $pythonExe "$PSScriptRoot\scripts\doctor.py"

Write-Host "`nLaunching Backend Server (Terminal 1)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-ExecutionPolicy", "Bypass", "-NoExit", "-Command", "& '$PSScriptRoot\start-backend.ps1'"

Write-Host "Launching Frontend Dev Server (Terminal 2)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-ExecutionPolicy", "Bypass", "-NoExit", "-Command", "& '$PSScriptRoot\start-frontend.ps1'"

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "Both servers launched in new windows!" -ForegroundColor Green
Write-Host "Backend API:      http://127.0.0.1:8000/" -ForegroundColor Yellow
Write-Host "Swagger Docs:     http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "Readiness Check:  http://127.0.0.1:8000/api/health/ready" -ForegroundColor Yellow
Write-Host "Frontend Web App: http://localhost:5173/" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
