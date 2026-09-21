param(
    [switch] $RunSmokeTest,
    [switch] $NoBrowser
)

$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

if (Test-Path ".venv\Scripts\python.exe") {
    $python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
} else {
    $python = "python"
}

Write-Host "Apartment SwarmUI MVP"
Write-Host ""
if ($RunSmokeTest) {
    & $python -u smoke_test.py
} else {
    & $python -u main.py

    if ($LASTEXITCODE -ne 0) {
        throw "The offline pipeline failed with exit code $LASTEXITCODE."
    }

    Write-Host ""
    Write-Host "Starting the web review interface..."
    $webProcess = Start-Process -FilePath $python `
        -ArgumentList "-u", "web_app.py" `
        -WorkingDirectory $PSScriptRoot `
        -PassThru

    Write-Host "Web interface: http://localhost:5000"
    if (-not $NoBrowser) {
        Start-Process "http://localhost:5000"
    }
}

Write-Host ""
Write-Host "Results are written under: $PSScriptRoot\outputs"
Write-Host "To run the smoke test explicitly:"
Write-Host "  .\run_windows.ps1 -RunSmokeTest"
Write-Host "Use -NoBrowser to start the interface without opening a browser."