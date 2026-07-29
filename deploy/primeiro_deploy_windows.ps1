param(
    [string]$PythonPath = ".\venv\Scripts\python.exe"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $PythonPath)) {
    throw "Python do ambiente virtual nao encontrado em $PythonPath"
}

$env:DJANGO_SETTINGS_MODULE = "config.settings.prod"

& $PythonPath -m pip install -r requirements.txt

$EnvFile = ".\.env"
if (Test-Path $EnvFile) {
    $SqliteLine = Get-Content $EnvFile |
        Where-Object { $_ -match "^\s*DJANGO_SQLITE_PATH\s*=" } |
        Select-Object -First 1

    if ($SqliteLine) {
        $SqlitePath = ($SqliteLine -split "=", 2)[1].Trim().Trim('"').Trim("'")
        if ($SqlitePath) {
            $SqliteDir = Split-Path -Parent $SqlitePath
            if ($SqliteDir -and -not (Test-Path $SqliteDir)) {
                New-Item -ItemType Directory -Force $SqliteDir | Out-Null
            }
        }
    }
}

& $PythonPath manage.py check
& $PythonPath manage.py check --deploy --fail-level ERROR
& $PythonPath manage.py migrate
& $PythonPath manage.py collectstatic --noinput

Write-Host ""
Write-Host "Deploy preparado. Crie o primeiro usuario com:"
Write-Host "$PythonPath manage.py createsuperuser"
Write-Host ""
Write-Host "Para iniciar o servidor:"
Write-Host ".\deploy\start_waitress.ps1"
