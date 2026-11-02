# Recrea la base tesis_prj desde src\database\script.sql.
# La contraseña no se guarda aquí: psql la pide, o la toma de $env:PGPASSWORD si ya está definida.
param(
    [string]$BaseDeDatos = 'tesis_prj'
)

$ErrorActionPreference = 'Stop'
$psql = (Get-Command psql -ErrorAction SilentlyContinue).Source
if (-not $psql) { $psql = 'C:\Program Files\PostgreSQL\18\bin\psql.exe' }
$scriptSql = Join-Path $PSScriptRoot 'src\database\script.sql'

& $psql -X -v ON_ERROR_STOP=1 -U postgres -h localhost -p 5432 -d $BaseDeDatos -f $scriptSql

if ($LASTEXITCODE -ne 0) {
    throw "No se pudo reconstruir la base de datos. Revisa el error de psql (código $LASTEXITCODE)."
}
Write-Host "Base de datos reconstruida correctamente." -ForegroundColor Green
