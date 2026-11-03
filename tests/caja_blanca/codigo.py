"""Código fuente de cada caso PCB-XX: segmentos que se muestran, fragmento de la
ficha y ubicación de las marcas C1/C2/C3. Lo usan la ficha Word y la imagen de
cobertura, así las dos muestran las mismas líneas y las mismas etiquetas.
"""
import ast
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[2]


def _lineas_docstring(fuente: str) -> set[int]:
    """Números de línea (1-based) de los docstrings de funciones y clases."""
    lineas: set[int] = set()
    for nodo in ast.walk(ast.parse(fuente)):
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and ast.get_docstring(nodo):
            doc = nodo.body[0]
            lineas.update(range(doc.lineno, doc.end_lineno + 1))
    return lineas


def fuente(caso: dict[str, Any]) -> list[str]:
    return (RAIZ / caso["archivo"]).read_text(encoding="utf-8").splitlines()


def segmentos(caso: dict[str, Any]) -> list[list[int]]:
    """Números de línea (1-based) de cada segmento de casos.py, sin docstrings."""
    lineas = fuente(caso)
    docstrings = _lineas_docstring("\n".join(lineas))
    bloques: list[list[int]] = []
    cursor = 0
    for desde, hasta, extra in caso["fragmento"]:
        ini = next(i for i in range(cursor, len(lineas)) if desde in lineas[i])
        fin = next(i for i in range(ini, len(lineas)) if hasta in lineas[i]) + extra
        bloques.append([i + 1 for i in range(ini, fin + 1) if i + 1 not in docstrings])
        cursor = fin + 1
    return bloques


def fragmento(caso: dict[str, Any]) -> str:
    """Fragmento de la ficha: los segmentos unidos con "...", sin marcas."""
    lineas = fuente(caso)
    bloques = [[lineas[n - 1] for n in b] for b in segmentos(caso)]
    # Sangría común fuera; los segmentos conservan su sangría relativa, salvo que
    # vengan de funciones distintas (cada uno se alinea por separado).
    grupos = [[b] for b in bloques] if caso.get("sangria_por_segmento") else [bloques]
    salida = []
    for grupo in grupos:
        sangria = min(len(l) - len(l.lstrip()) for b in grupo for l in b if l.strip())
        salida.extend("\n".join(l[sangria:] for l in b) for b in grupo)
    return "\n...\n".join(salida)


def marcas(caso: dict[str, Any], lineas: list[str]) -> dict[int, str]:
    """Índice en `lineas` -> comentario ("# C1", ...) de cada marca de casos.py.
    Marca: (texto de la línea, comentario[, n-ésima aparición])."""
    ubicadas: dict[int, str] = {}
    for marca in caso["marcas"]:
        texto, comentario, n = (*marca, 1) if len(marca) == 2 else marca
        indices = [i for i, l in enumerate(lineas) if texto in l]
        ubicadas[indices[n - 1]] = comentario
    return ubicadas
