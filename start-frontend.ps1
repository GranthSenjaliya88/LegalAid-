# LegalAId — Frontend Web App Launcher for Windows PowerShell
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyans
Write-Host "Starting LegalAId Frontend Web App..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyans

Set-Location -Path "$PSScriptRoot\frontend"

$env:Path = "C:\Program Files\nodejs;" + $env:Path

Write-Host "Web Application: http://localhost:5173/" -ForegroundColor Yellow
Write-Host "Press CTRL+C to stop the dev server.`n" -ForegroundColor Gray

& "C:\Program Files\nodejs\npm.cmd" run dev -- --host localhost --port 5173
