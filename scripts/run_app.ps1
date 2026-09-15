# IntelliGrade Classifier - PowerShell Launch Script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path "$ScriptDir\.."
Set-Location $ProjectRoot

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "  IntelliGrade Classifier - Air-Gapped Cognitive Engine" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "Launching Streamlit Dashboard..." -ForegroundColor Yellow

python -m streamlit run app.py
