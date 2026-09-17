param(
    [string]$Instrument = "usa500idxusd",
    [string]$Start = "2019-01-02T00:00:00Z",
    [string]$End = "2026-09-01T00:00:00Z",
    [int]$Workers = 2,
    [switch]$PlanOnly,
    [switch]$Overwrite
)

$ErrorActionPreference = "Stop"
Set-Location "C:\QUANT_LAB"

$args = @("-m", "quantlab.cli.main", "acquisition")
if ($PlanOnly) { $args += @("plan") } else { $args += @("download") }
$args += @("--instrument", $Instrument, "--start", $Start, "--end", $End, "--root", "data", "--workers", $Workers)
if ($Overwrite) { $args += "--overwrite" }

& ".\.venv\Scripts\python.exe" @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
