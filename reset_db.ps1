# Recrea la base tesis_prj desde src\database\script.sql.
# La contraseña no se guarda aquí: psql la pide, o la toma de $env:PGPASSWORD si ya está definida.
$psql = (Get-Command psql -ErrorAction SilentlyContinue).Source
if (-not $psql) { $psql = 'C:\Program Files\PostgreSQL\18\bin\psql.exe' }

& $psql -U postgres -h localhost -p 5432 -d tesis_prj -f src\database\script.sql

if ($LASTEXITCODE -eq 0) {
    Write-Host "Base de datos actualizada correctamente." -ForegroundColor Green
} else {
    Write-Host "Error al ejecutar el script. Revisa los mensajes anteriores." -ForegroundColor Red
}
