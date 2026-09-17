# Quant_Lab Full Setup

Run in Windows PowerShell:

Set-ExecutionPolicy -Scope Process Bypass
cd C:\QUANT_LAB
.\setup_quant_lab.ps1

Optional:
.\setup_quant_lab.ps1 -SkipGitPush
.\setup_quant_lab.ps1 -SkipInstall

The procedure is idempotent and does not delete Quant_Lab, .venv, raw data, or archives.
