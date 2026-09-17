$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    throw "Quant_Lab .venv not found. Expected C:\QUANT_LAB\.venv\Scripts\python.exe"
}
& ".\.venv\Scripts\python.exe" -m quantlab.cli.main doctor --root (Get-Location).Path
if ($LASTEXITCODE -ne 0) {
    Write-Host "FOUNDATION_DOCTOR=FAIL" -ForegroundColor Red
    exit $LASTEXITCODE
}
Write-Host "FOUNDATION_DOCTOR=PASS" -ForegroundColor Green
