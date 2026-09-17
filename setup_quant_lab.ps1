[CmdletBinding()]
param(
    [string]$Root = "C:\QUANT_LAB",
    [string]$GitHubRemote = "https://github.com/aiakunriset-dot/Quant_Lab.git",
    [switch]$SkipInstall,
    [switch]$SkipGitPush
)
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Step([string]$Message) { Write-Host "`n==> $Message" -ForegroundColor Cyan }
function Need([string]$Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command not found: $Name"
    }
}
function Ensure-Directory([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) { New-Item -ItemType Directory -Path $Path -Force | Out-Null }
}
function File([string]$Path,[string]$Content) {
    Ensure-Directory (Split-Path -Parent $Path)
    [IO.File]::WriteAllText($Path,$Content,[Text.UTF8Encoding]::new($false))
}
function Normalize-PathForComparison([string]$Path) {
    $resolved = [IO.Path]::GetFullPath($Path)
    if ($true) {
        $resolved = $resolved.Replace("/", "\")
        $resolved = $resolved.TrimEnd("\")
        return $resolved.ToUpperInvariant()
    }
    return $resolved.TrimEnd("/")
}

Step "Validate canonical Quant_Lab identity"
if ($Root -ne "C:\QUANT_LAB") { throw "Canonical root is locked to C:\QUANT_LAB" }
if (-not (Test-Path -LiteralPath $Root)) { throw "Missing canonical root: $Root" }
Need python
Need git

Step "Create canonical directories"
@(
".github\workflows","config","data\raw","data\processed","data\datasets",
"data\manifests","data\artifacts","data\logs","data\control",
"research\experiments","research\notebooks","research\models","research\reports",
"strategies\candidates","strategies\validated","strategies\production",
"tests\unit","tests\integration","tests\property","tests\regression",
"tools","docs\architecture","docs\data","docs\research",
"docs\superpowers\specs","docs\superpowers\plans","src\quantlab"
) | % { Ensure-Directory (Join-Path $Root $_) }

Step "Install canonical control-plane configuration"
File (Join-Path $Root ".aider.conf.yml") @"
auto-commits: false
dirty-commits: false
verify-ssl: true
"@
File (Join-Path $Root ".aiderignore") @"
.venv/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
data/raw/
data/processed/
data/datasets/
data/artifacts/
data/logs/
"@
File (Join-Path $Root "config\control_plane.yaml") @"
project:
  name: Quant_Lab
  root: C:\QUANT_LAB
  python_package: quantlab
  distribution: quant-lab
  github_repository: aiakunriset-dot/Quant_Lab
  default_branch: main

planes:
  code_authority: git
  remote_authority: github
  data_artifact_plane: google_drive
  compute_plane: google_colab
  agents: [gpt, claude, aider]

historical_data:
  source: dukascopy
  timeframe: M1
  interval: "[start,end)"
  start: "2019-01-02"
  end: "2026-09-01"
  instruments:
    - usa30idxusd
    - usa500idxusd
    - usatechidxusd
    - deuidxeur
    - gbridxgbp
    - jpnidxjpy
    - xauusd
    - dollaridxusd
    - volidxusd

provenance:
  hash: SHA-256
  timestamps: UTC
  synthetic_data: forbidden
  silent_repair: forbidden
  partial_is_validated: false
"@
File (Join-Path $Root "docs\architecture\CANONICAL_IDENTITY.md") @"
# Quant_Lab Canonical Identity

Project and repository identity are fixed.

- Project: Quant_Lab
- Local root: C:\QUANT_LAB
- Python package: quantlab
- Distribution: quant-lab
- GitHub: aiakunriset-dot/Quant_Lab
- Main branch: main

Authority:
Git commit -> code/config
GitHub -> remote source of truth
Google Drive -> datasets/artifacts
Google Colab -> compute
GPT/Claude/Aider -> agent layer

Legacy aliases and alternate Quant_Lab roots are prohibited. The installer performs a fail-closed identity scan without embedding legacy aliases in active documentation.

Reproducibility:
BacktestResult = f(GitCommit, DatasetVersion, Configuration, Environment)
"@
File (Join-Path $Root "README.md") @"
# Quant_Lab

Canonical quantitative research and algorithmic trading platform.

Root: C:\QUANT_LAB
Package: quantlab
Distribution: quant-lab
GitHub: aiakunriset-dot/Quant_Lab

Git/GitHub is the code authority.
Google Drive stores large datasets and artifacts.
Google Colab is the compute plane.
GPT, Claude and Aider operate as controlled agents.

No agent output, notebook, cache or generated artifact supersedes a Git commit.
"@

Step "Normalize project metadata"
$py = Join-Path $Root "pyproject.toml"
if (Test-Path -LiteralPath $py) {
    $t = Get-Content -LiteralPath $py -Raw
    $legacy_distribution = 'quant' + '-lab-fresh'
    $legacy_project = 'Quant_Lab_' + 'Fresh'
    $t = $t -replace [regex]::Escape($legacy_distribution),'quant-lab'
    $t = $t -replace [regex]::Escape($legacy_project),'Quant_Lab'
    File $py $t
}

Step "Initialize canonical Git"
Push-Location $Root
try {
    if (-not (Test-Path -LiteralPath (Join-Path $Root ".git"))) { git init -b main | Out-Host }
    if (@(git remote) -notcontains "origin") { git remote add origin $GitHubRemote }
    else { git remote set-url origin $GitHubRemote }
    git branch -M main
    Write-Host "ROOT=$(git rev-parse --show-toplevel)"
    Write-Host "BRANCH=$(git branch --show-current)"
    Write-Host "ORIGIN=$(git remote get-url origin)"
} finally { Pop-Location }

if (-not $SkipInstall) {
    Step "Create/validate Python environment"
    $vp = Join-Path $Root ".venv\Scripts\python.exe"
    if (-not (Test-Path -LiteralPath $vp)) { python -m venv (Join-Path $Root ".venv") }
    & $vp -m pip install --upgrade pip setuptools wheel
    if (Test-Path -LiteralPath $py) { & $vp -m pip install -e $Root; & $vp -m pip check }
}

Step "Canonical identity audit"
$legacy_distribution = 'quant' + '-lab-fresh'
$legacy_project = 'Quant_Lab_' + 'Fresh'
$legacy_versioned = $legacy_project + '_0.1.0'
$bad = @($legacy_distribution, $legacy_project, $legacy_versioned)
$hits = Get-ChildItem -LiteralPath $Root -Recurse -File -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch '\\.git\\|\\.venv\\|\\data\\raw\\' } |
    Select-String -Pattern $bad -SimpleMatch -List -ErrorAction SilentlyContinue
if ($hits) { $hits | % { Write-Host "FORBIDDEN: $($_.Path)" -ForegroundColor Red }; throw "Identity audit failed" }

Step "Python and source verification"
$vp = Join-Path $Root ".venv\Scripts\python.exe"
if (Test-Path -LiteralPath $vp) {
    & $vp -c "import quantlab; print('quantlab_import=PASS'); print('quantlab_file=' + quantlab.__file__)"
    & $vp -m compileall -q (Join-Path $Root "src")
}

Step "Commit canonical foundation"
Push-Location $Root
try {
    git add -A
    if (-not (git diff --cached --quiet)) { git commit -m "chore: establish canonical Quant_Lab foundation" | Out-Host }
    git diff --check
    if (-not $SkipGitPush) { git push -u origin main }
    git status --short
} finally { Pop-Location }

Step "Final verification"
Push-Location $Root
try {
    $r=(git rev-parse --show-toplevel).Trim()
    $b=(git branch --show-current).Trim()
    $o=(git remote get-url origin).Trim()
    Write-Host "ROOT=$r"
    Write-Host "BRANCH=$b"
    Write-Host "ORIGIN=$o"
    $canonicalGitRoot = Normalize-PathForComparison $r
    $canonicalRoot = Normalize-PathForComparison $Root
    if ($canonicalGitRoot -ne $canonicalRoot) {
        Write-Host "CANONICAL_GIT_ROOT=$canonicalGitRoot" -ForegroundColor Red
        Write-Host "CANONICAL_ROOT=$canonicalRoot" -ForegroundColor Red
        throw "Git root mismatch"
    }
    if ($b -ne "main") { throw "Branch mismatch" }
    if ($o -ne $GitHubRemote) { throw "Origin mismatch" }
} finally { Pop-Location }

Write-Host "`nSETUP PROCEDURE COMPLETED; use the command output as the verification record." -ForegroundColor Green
