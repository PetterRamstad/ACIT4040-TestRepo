param(
    [switch] $SkipDataset,
    [switch] $RunSmokeTest
)

$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

Write-Host "Creating local virtual environment..."
python -m venv .venv

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

Write-Host "Installing dependencies..."
& $python -m pip install --upgrade pip
& $python -m pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example"
} else {
    Write-Host ".env already exists"
}

if (-not $SkipDataset) {
    Write-Host ""
    Write-Host "Downloading and validating the Kaggle dataset..."
    & $python prepare_dataset.py
}

if ($RunSmokeTest) {
    Write-Host ""
    Write-Host "Running offline smoke test..."
    & $python smoke_test.py
}

Write-Host ""
Write-Host "Running the full offline application pipeline..."
& $python main.py

Write-Host ""
Write-Host "Setup complete."
Write-Host "Results are in: $PSScriptRoot\outputs\dataset_round_01"
Write-Host "Run commands with: & `"$python`" main.py"
Write-Host "Or activate the environment with: . .\.venv\Scripts\Activate.ps1"
