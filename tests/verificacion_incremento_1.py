"""
Pruebas basicas de verificacion - Incremento 1 (HITO 1) - CoffeeRen

Tres comprobaciones sobre la base tecnica del primer incremento:
  1. Health-check del servidor FastAPI  - GET /health (TestClient in-process).
  2. Base de datos PostgreSQL           - conexion + tablas del esquema inicial.
  3. Estructura de carpetas             - arquitectura de 4 capas.

Requisitos previos:
  - PostgreSQL en ejecucion con la base 'tesis_prj' ya creada:
      psql -U postgres -d tesis_prj -f src/database/script.sql
  - Pesos del modelo YOLO presentes en src/ml/models/ (se cargan al importar src.main).

Uso:
    .venv\\Scripts\\activate
    python -m tests.verificacion_incremento_1

Codigo de salida: 0 si las tres pruebas pasan, 1 si alguna falla.
"""
import contextlib
import os
import re
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

CAPAS = ("routes", "services", "models", "schemas")
ENTIDADES = ("persona", "caficultor", "evaluacion", "tipo_documento")

_NULO = open(os.devnull, "w", encoding="utf-8")


@contextlib.contextmanager
def _silencio():
    """Oculta la salida de terceros (carga de YOLO, prints de Connection)."""
    with contextlib.redirect_stdout(_NULO), contextlib.redirect_stderr(_NULO):
        yield


def _linea(indice: int, nombre: str, ok: bool, detalle: str) -> None:
    print(f"  [{indice}] {nombre:<26} {'OK   ' if ok else 'FALLA'}  {detalle}")


def prueba_servidor() -> bool:
    try:
        with _silencio():
            from fastapi.testclient import TestClient

            from src.main import app

            respuesta = TestClient(app).get("/health")
    except Exception as exc:
        _linea(1, "Servidor FastAPI", False, f"no se pudo importar la app: {exc}")
        return False

    ok = respuesta.status_code == 200 and respuesta.json().get("status") == "ok"
    _linea(1, "Servidor FastAPI", ok, f"GET /health -> {respuesta.status_code} status={respuesta.json().get('status')}")
    return ok


def prueba_base_datos() -> bool:
    script_sql = (RAIZ / "src" / "database" / "script.sql").read_text(encoding="utf-8")
    esperadas = {m.group(1).lower() for m in re.finditer(r"CREATE TABLE\s+(\w+)", script_sql, re.IGNORECASE)}

    try:
        from src.config import Config
        from src.database.bd import Connection

        with _silencio():
            db = Connection()
    except Exception as exc:
        _linea(2, "Base de datos PostgreSQL", False, f"sin conexion: {exc}")
        return False

    try:
        motor = db.obtener_uno("SELECT version() AS v")["v"].split(" on ")[0]
        filas = db.obtener(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = %s AND table_type = %s",
            ["public", "BASE TABLE"],
        )
    except Exception as exc:
        _linea(2, "Base de datos PostgreSQL", False, f"consulta fallida: {exc}")
        return False
    finally:
        db.close()

    presentes = {fila["table_name"].lower() for fila in filas}
    ok = esperadas.issubset(presentes)
    detalle = f"{Config.DATABASE} @ {Config.HOST}:{Config.PORT} ({motor}) - {len(esperadas & presentes)}/{len(esperadas)} tablas"
    _linea(2, "Base de datos PostgreSQL", ok, detalle)
    return ok


def prueba_estructura() -> bool:
    src = RAIZ / "src"
    conteo = {c: len([p for p in (src / c).glob("*.py") if p.stem != "__init__"]) for c in CAPAS}
    archivos_base = ("database/bd.py", "database/script.sql", "config-example.py", "main.py")

    base_ok = all(conteo.values()) and all((src / f).is_file() for f in archivos_base)
    traza_ok = all(
        all(any(entidad in p.stem for p in (src / capa).glob("*.py")) for capa in CAPAS)
        for entidad in ENTIDADES
    )
    ok = base_ok and traza_ok
    _linea(3, "Estructura 4 capas", ok, "  ".join(f"{capa}:{n}" for capa, n in conteo.items()))
    return ok


def main() -> int:
    print("CoffeeRen - Verificacion de pruebas basicas del Incremento 1 (HITO 1)")
    print(datetime.now().strftime("  %Y-%m-%d %H:%M"))
    print()

    resultados = [prueba_servidor(), prueba_base_datos(), prueba_estructura()]
    superadas = sum(resultados)
    print()

    if superadas == len(resultados):
        print(f"  Resultado: {superadas}/{len(resultados)} pruebas superadas - HITO 1 verificado.")
        return 0
    print(f"  Resultado: {superadas}/{len(resultados)} pruebas superadas - revisar el detalle.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
