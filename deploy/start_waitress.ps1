param(
    [string]$HostName = "0.0.0.0",
    [int]$Port = 1200,
    [string]$PythonPath = ".\venv\Scripts\python.exe"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $PythonPath)) {
    throw "Python do ambiente virtual nao encontrado em $PythonPath"
}

$env:DJANGO_SETTINGS_MODULE = "config.settings.prod"

& $PythonPath -m waitress --listen="$HostName`:$Port" config.wsgi:application