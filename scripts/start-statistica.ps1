# STATISTICA Offline Analysis Tool - Windows launcher
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$ManagedVenv = Join-Path $Root ".venv-statistica"
$ManagedPython = Join-Path $ManagedVenv "Scripts\python.exe"
$DepsStamp = Join-Path $ManagedVenv ".deps_installed"

Set-Location $Root

function Write-Step($Message) {
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Test-Command($Command) {
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

function Invoke-PythonCandidate($Candidate, $Arguments) {
    if ($Candidate -eq "py -3") {
        & py -3 @Arguments
    } else {
        & $Candidate @Arguments
    }
}

function Test-PythonCandidate($Candidate) {
    try {
        Invoke-PythonCandidate $Candidate @("--version") *> $null
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

function Find-BasePython {
    foreach ($candidate in @("python", "python3", "py -3")) {
        if (Test-PythonCandidate $candidate) {
            return $candidate
        }
    }
    return $null
}

function Test-ScientificStack($PythonExe) {
    try {
        & $PythonExe -c "import pandas, numpy, scipy, statsmodels, matplotlib, plotly, openpyxl, sklearn, docx, jinja2, seaborn" *> $null
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

Write-Host "STATISTICA Offline Analysis Tool" -ForegroundColor Green
Write-Host "Project: $Root"

Write-Step "Checking Node.js"
if (-not (Test-Command "node")) {
    Write-Host "Node.js was not found. Install Node.js 20+ first." -ForegroundColor Red
    exit 1
}
if (-not (Test-Command "npm.cmd")) {
    Write-Host "npm was not found. Reinstall Node.js and include npm." -ForegroundColor Red
    exit 1
}

Write-Step "Checking managed Python environment"
$basePython = Find-BasePython
if (-not $basePython) {
    Write-Host "Python 3 was not found. Install Python 3.10+ and enable PATH." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $ManagedPython)) {
    Write-Host "Creating managed environment: $ManagedVenv" -ForegroundColor Yellow
    Invoke-PythonCandidate $basePython @("-m", "venv", $ManagedVenv)
}

if (-not (Test-Path $ManagedPython)) {
    Write-Host "Failed to create managed Python environment." -ForegroundColor Red
    exit 1
}

Write-Step "Installing Python scientific dependencies"
if (-not (Test-ScientificStack $ManagedPython) -or -not (Test-Path $DepsStamp)) {
    & $ManagedPython -m pip install --upgrade pip
    & $ManagedPython -m pip install -r (Join-Path $Root "requirements.txt")
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Python dependency installation failed." -ForegroundColor Red
        exit 1
    }
    New-Item -Path $DepsStamp -ItemType File -Force | Out-Null
}

Write-Step "Installing Node dependencies"
if (-not (Test-Path (Join-Path $Root "node_modules"))) {
    npm.cmd install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Node dependency installation failed." -ForegroundColor Red
        exit 1
    }
}

Write-Step "Preparing local configuration"
if (-not (Test-Path (Join-Path $Root ".env")) -and (Test-Path (Join-Path $Root ".env.example"))) {
    Copy-Item (Join-Path $Root ".env.example") (Join-Path $Root ".env")
}

$env:STATISTICA_PYTHON = $ManagedPython
$env:PORT = if ($env:PORT) { $env:PORT } else { "3000" }
$url = "http://localhost:$env:PORT"

Write-Step "Starting STATISTICA"
Write-Host "Using Python: $ManagedPython" -ForegroundColor DarkGray
Write-Host "Open: $url" -ForegroundColor Green

Start-Process $url | Out-Null
npm.cmd run dev
