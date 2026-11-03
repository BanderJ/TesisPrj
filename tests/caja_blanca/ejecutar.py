"""Ejecuta las pruebas de caja blanca PCB-01 a PCB-12 y guarda la evidencia.

Por cada caso corre pytest con cobertura de ramas (pytest-cov, --cov-branch) del
módulo evaluado y deja en CAJA_BLANCA_DIR:
  evidencias/PCB-XX.log  -> salida completa de pytest (respaldo)
  evidencias/PCB-XX.png  -> resultado por camino y cobertura de la función (evidencia.py)
  resultados.json        -> fecha, duración, archivo, función, fragmento, caminos y veredicto

Uso: python -m tests.caja_blanca.ejecutar [PCB-01 PCB-05 ...]
"""
import json
import math
import os
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from typing import Any

from tests.caja_blanca import evidencia
from tests.caja_blanca.casos import CARPETA, CASOS, EVIDENCIAS, leer_casos
from tests.caja_blanca.codigo import RAIZ, fragmento

EVIDENCIA_USADA = ["Captura de pantalla", "Fragmento de código", "Log de ejecución"]


def _cobertura_funciones(ruta_json: Path, caso: dict[str, Any]) -> list[str]:
    """Una línea por función evaluada: sentencias, ramas y porcentaje de la función."""
    datos = json.loads(ruta_json.read_text(encoding="utf-8"))
    archivo = next(
        v for k, v in datos["files"].items()
        if Path(k).as_posix().endswith(caso["archivo"])
    )
    lineas = []
    for nombre in caso["funciones_cov"]:
        r = archivo["functions"][nombre]["summary"]
        lineas.append(
            f"{nombre}(): sentencias {r['covered_lines']}/{r['num_statements']} · "
            f"ramas {r['covered_branches']}/{r['num_branches']} · {r['percent_covered']:.0f} %"
        )
    return lineas


def _caminos(ruta_junit: Path) -> dict[str, str]:
    """{C1: 'Aprobado' | 'Fallido: <mensaje>'} a partir del XML de JUnit."""
    caminos: dict[str, str] = {}
    for tc in ET.parse(ruta_junit).getroot().iter("testcase"):
        camino = tc.get("name", "").split("_")[1].upper()  # test_c1_... -> C1
        fallo = tc.find("failure")
        if fallo is None:
            fallo = tc.find("error")
        if fallo is None and tc.find("skipped") is None:
            caminos[camino] = "Aprobado"
        else:
            mensaje = (fallo.get("message") if fallo is not None else "omitido") or ""
            caminos[camino] = f"Fallido: {mensaje.splitlines()[0] if mensaje else 'sin mensaje'}"
    return caminos


def ejecutar(codigo: str, fila_excel: dict[str, Any]) -> dict[str, Any]:
    caso = CASOS[codigo]
    prueba = f"tests/caja_blanca/test_pcb_{codigo[-2:]}.py"
    comando_visible = f"python -m pytest {prueba} -v --cov={caso['modulo_cov']} --cov-branch"
    with tempfile.TemporaryDirectory() as tmp:
        ruta_cov, ruta_junit, ruta_html = Path(tmp) / "cov.json", Path(tmp) / "junit.xml", Path(tmp) / "html"
        comando = [
            sys.executable, "-m", "pytest", prueba, "-v", "--color=no", "-p", "no:cacheprovider",
            f"--cov={caso['modulo_cov']}", "--cov-branch", "--cov-report=term",
            f"--cov-report=json:{ruta_cov}", f"--cov-report=html:{ruta_html}", f"--junitxml={ruta_junit}",
        ]
        inicio = time.monotonic()
        salida = subprocess.run(
            comando, cwd=RAIZ, capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        segundos = time.monotonic() - inicio
        caminos = _caminos(ruta_junit)
        cobertura = _cobertura_funciones(ruta_cov, caso)

        obtenido = {
            c: texto if caminos.get(c) == "Aprobado" else caminos.get(c, "no ejecutado")
            for c, texto in caso["obtenido"].items()
        }
        # El reporte HTML de un módulo es z_<hash>_<archivo>_py.html.
        reporte = next(ruta_html.glob(f"*{Path(caso['archivo']).stem}_py.html"))
        evidencia.generar(
            codigo, caso, fila_excel,
            {c: v == "Aprobado" for c, v in caminos.items()},
            obtenido, comando_visible, reporte, cobertura,
        )

    # Se guarda solo la salida de pytest: sin los prints del tracker (stdout capturado por pytest).
    salida_pytest = (salida.stdout.replace(str(ruta_junit), "junit.xml")
                     .replace(str(ruta_cov), "coverage.json").replace(str(ruta_html), "htmlcov"))
    (EVIDENCIAS / f"{codigo}.log").write_text(
        f"$ {comando_visible}\n{salida_pytest.rstrip()}\n\n"
        "Cobertura de la función evaluada:\n" + "\n".join(f"  {l}" for l in cobertura) + "\n",
        encoding="utf-8",
    )

    aprobado = all(v == "Aprobado" for v in caminos.values()) and len(caminos) == len(obtenido)
    observaciones = " ".join(filter(None, [
        caso["observaciones"],
        "Cobertura medida con pytest-cov --cov-branch: " + "; ".join(cobertura) + ".",
    ]))
    return {
        "fecha": date.today().strftime("%d/%m/%Y"),
        "duracion_min": max(1, math.ceil(segundos / 60)),
        "duracion_s": round(segundos, 1),
        "archivo": caso["archivo"],
        "funcion": caso["funcion"],
        "fragmento": fragmento(caso),
        "caminos": caminos,
        "caminos_ejecutados": f"{len(caminos)} de {len(obtenido)}",
        "resultado_obtenido": "\n".join(f"{c}: {t}" for c, t in obtenido.items()),
        "veredicto": "Aprobado" if aprobado else "Fallido",
        "evidencia": EVIDENCIA_USADA,
        "cobertura": cobertura,
        "observaciones": observaciones,
    }


def main(codigos: list[str]) -> None:
    EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    excel = leer_casos()
    ruta = CARPETA / "resultados.json"
    resultados = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}
    for codigo in codigos:
        resultados[codigo] = ejecutar(codigo, excel[codigo])
        r = resultados[codigo]
        print(f"{codigo}: {r['veredicto']} ({r['caminos_ejecutados']}) {r['caminos']}")
    resultados = dict(sorted(resultados.items()))
    ruta.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:] or list(CASOS))
