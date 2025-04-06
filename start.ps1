$VENV_PATH = "$PSScriptRoot\.venv\Scripts\Activate.ps1"

if (!(Test-Path $VENV_PATH)) {
    Write-Host "Shared virtual environment not found: $VENV_PATH"
    exit
}

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "& {`"cd '$PSScriptRoot';",
    ". '$VENV_PATH';",
    "cd src/AI/model_service;",
    "python __main__.py`"}"
)

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "& {`"cd '$PSScriptRoot';",
    ". '$VENV_PATH';",
    "cd src/web/backend;",
    "python __main__.py`"}"
)

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "& {`"cd '$PSScriptRoot/src/web/frontend';",
    "npm run dev`"}"
)

Write-Host "All services started successfully!"
