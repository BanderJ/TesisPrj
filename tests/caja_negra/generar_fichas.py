"""Genera Pruebas_Caja_Negra_CoffeeRen.docx: una ficha por caso del Excel.

Fuentes (en CAJA_NEGRA_DIR):
  Casos_Prueba_Caja_Negra.xlsx  -> datos de cada caso (hoja Casos)
  Template_Prueba_Caja_Negra.docx -> ficha oficial; se copia su tabla por caso
  resultados.json               -> fecha, duración, resultado, veredicto, evidencia, observaciones
  evidencias/PCN-XX.png         -> imagen bajo la ficha

Uso: python -m tests.caja_negra.generar_fichas
"""
import copy
import json
import os
from pathlib import Path
from typing import Any

import openpyxl
from docx import Document

from tests.fichas_word import (
    actualizar_valores_portada,
    agregar_evidencia,
    celda,
    conservar_introduccion,
    copiar_ficha_con_imagenes,
    marcar,
    no_partir,
    parrafos,
    poner_pasos,
    poner_valor,
    quitar_guias,
    runs,
    salto_de_pagina,
    vaciar_cuerpo,
)

CARPETA = Path(os.environ.get(
    "CAJA_NEGRA_DIR", r"D:\Ciclo 10\Tesis1\Documentacion\Pruebas\CajaNegra"
))
SALIDA = CARPETA / "Pruebas_Caja_Negra_CoffeeRen.docx"


def leer_casos() -> list[dict[str, Any]]:
    ws = openpyxl.load_workbook(CARPETA / "Casos_Prueba_Caja_Negra.xlsx")["Casos"]
    columnas = [c.value for c in ws[1]]
    return [dict(zip(columnas, (c.value for c in fila))) for fila in ws.iter_rows(min_row=2) if fila[0].value]


def llenar_ficha(tbl, caso: dict[str, Any], resultado: dict[str, Any] | None) -> None:
    molde_run = runs(parrafos(celda(tbl, 1, 0))[1])[0]  # run negro sin formato especial
    poner_valor(celda(tbl, 1, 0), 1, caso["Código"])
    poner_valor(celda(tbl, 4, 0), 1, caso["Módulo"])
    poner_valor(celda(tbl, 4, 1), 1, caso["RF / RNF"])
    poner_valor(celda(tbl, 5, 0), 1, caso["Descripción del requisito"])
    poner_valor(celda(tbl, 7, 0), 1, caso["Precondiciones"])
    poner_valor(celda(tbl, 8, 0), 1, caso["Hardware"])
    poner_valor(celda(tbl, 10, 0), 1, f"{caso['Caso de prueba']} · {caso['Técnica · clase']}")
    # Los valores realmente usados en la ejecución reemplazan a los genéricos del Excel.
    poner_valor(celda(tbl, 11, 0), 1, (resultado or {}).get("datos_entrada") or caso["Datos de entrada"])
    poner_valor(celda(tbl, 11, 1), 1, caso["Resultado esperado"])
    poner_pasos(celda(tbl, 12, 0), caso["Pasos de la prueba"])

    if resultado:
        dia, mes, anio = resultado["fecha"].split("/")
        poner_valor(celda(tbl, 2, 0), 1, f"{dia} / {mes} / {anio}")
        poner_valor(celda(tbl, 2, 1), 1, f"{resultado['duracion_min']} min")
        poner_valor(celda(tbl, 14, 0), 1, resultado["resultado_obtenido"], molde_run)
        poner_valor(celda(tbl, 15, 0), 1, resultado.get("observaciones") or "", molde_run)
        marcar(celda(tbl, 14, 1), [resultado["veredicto"]])
        marcar(celda(tbl, 15, 1), resultado["evidencia"])
    elif caso.get("Nota"):
        poner_valor(celda(tbl, 15, 0), 1, caso["Nota"], molde_run)

    quitar_guias(tbl)
    no_partir(tbl)


def generar() -> Path:
    casos = leer_casos()
    ruta_res = CARPETA / "resultados.json"
    resultados = json.loads(ruta_res.read_text(encoding="utf-8")) if ruta_res.exists() else {}

    origen = Document(CARPETA / "Template_Prueba_Caja_Negra.docx")
    plantilla, sect_pr = vaciar_cuerpo(origen)
    doc = Document(SALIDA) if SALIDA.exists() else origen
    plantilla = copiar_ficha_con_imagenes(plantilla, origen, doc)

    fichas_manuales = {}
    if SALIDA.exists():
        manuales = {c["Código"] for c in casos if str(c["Ejecución"]).startswith("Manual")}
        for tabla in doc.tables:
            if "Código de la prueba" in "".join(tabla._tbl.itertext()):
                codigo = tabla.cell(1, 0).text.strip().splitlines()[-1].strip()
                if codigo in manuales:
                    fichas_manuales[codigo] = copy.deepcopy(tabla._tbl)
        sect_pr = conservar_introduccion(doc, (plantilla, *fichas_manuales.values()))
        aprobados = sum(resultados.get(c["Código"], {}).get("veredicto") == "Aprobado" for c in casos)
        fallidos = sum(resultados.get(c["Código"], {}).get("veredicto") == "Fallido" for c in casos)
        actualizar_valores_portada(doc, {
            "Alcance": f"{len(casos)} casos ({casos[0]['Código']} a {casos[-1]['Código']})",
            "Casos aprobados": f"{aprobados} de {len(casos)}",
            "Casos fallidos": str(fallidos),
            "Casos pendientes": str(len(casos) - aprobados - fallidos),
        })
        if resultados:
            actualizar_valores_portada(doc, {
                "Fecha de ejecución": next(iter(resultados.values()))["fecha"],
            })

    elementos = []
    for i, caso in enumerate(casos):
        codigo = caso["Código"]
        manual = str(caso["Ejecución"]).startswith("Manual")
        resultado = None if manual else resultados.get(codigo)
        if i:
            elementos.append(salto_de_pagina(doc))
        if manual and codigo in fichas_manuales:
            tbl = fichas_manuales[codigo]
        else:
            tbl = copy.deepcopy(plantilla)
            llenar_ficha(tbl, caso, resultado)
        elementos.append(tbl)
        imagen = CARPETA / "evidencias" / f"{codigo}.png"
        if imagen.exists():
            elementos.extend(agregar_evidencia(
                doc, codigo, imagen, pie=f"Figura {codigo}. {caso['Caso de prueba']}"
            ))
        else:
            # Página editable para incorporar la evidencia que falta.
            elementos.append(salto_de_pagina(doc))
            elementos.append(doc.add_paragraph()._p)

    for e in elementos:
        sect_pr.addprevious(e)
    doc.save(SALIDA)
    return SALIDA


if __name__ == "__main__":
    print(generar())
