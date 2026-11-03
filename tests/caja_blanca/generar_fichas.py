"""Genera Pruebas_Caja_Blanca_CoffeeRen.docx: una ficha por caso del Excel.

Fuentes (en CAJA_BLANCA_DIR):
  Casos_Prueba_Caja_Blanca.xlsx    -> datos de cada caso (hoja Casos)
  Template_Prueba_Caja_Blanca.docx -> ficha oficial; se copia su tabla por caso
  resultados.json                  -> lo escribe tests.caja_blanca.ejecutar
  evidencias/PCB-XX.png            -> imagen bajo la ficha

Uso: python -m tests.caja_blanca.generar_fichas
"""
import copy
import json
from typing import Any

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from tests.caja_blanca.casos import CARPETA, CASOS, EVIDENCIAS, PASOS_COMUNES, leer_casos
from tests.caja_blanca.codigo import marcas
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
    texto_run,
    vaciar_cuerpo,
)

SALIDA = CARPETA / "Pruebas_Caja_Blanca_CoffeeRen.docx"
# Filas de encabezado de sección del template (Datos del requisito, Datos del código
# evaluado, Condiciones, Datos del caso de prueba, Resultado). Con el fragmento de
# código la ficha no cabe en una página A4: el salto solo puede caer en estas filas.
SECCIONES = frozenset({3, 6, 10, 13, 17})
PIE_FIGURA = "Figura {codigo}. Resultado por camino y cobertura de la función evaluada"
ANCHO_EVIDENCIA_CM = 17


def con_marcas(codigo: str, fragmento: str) -> str:
    """Agrega los comentarios # C1, # C2, # C3 a las líneas de las condiciones (solo en el documento)."""
    lineas = fragmento.split("\n")
    for i, comentario in marcas(CASOS[codigo], lineas).items():
        lineas[i] += f"  {comentario}"
    return "\n".join(lineas)


def poner_codigo(tc, texto: str) -> None:
    """Fragmento de código en Consolas 8 pt."""
    poner_valor(tc, 1, texto)
    r = runs(parrafos(tc)[1])[0]
    rpr = r.find(qn("w:rPr"))
    for etiqueta in ("w:rFonts", "w:sz", "w:szCs"):
        for e in rpr.findall(qn(etiqueta)):
            rpr.remove(e)
    fuentes = OxmlElement("w:rFonts")
    for atributo in ("w:ascii", "w:hAnsi", "w:cs"):
        fuentes.set(qn(atributo), "Consolas")
    rpr.insert(0, fuentes)
    for etiqueta in ("w:sz", "w:szCs"):
        tam = OxmlElement(etiqueta)
        tam.set(qn("w:val"), "16")
        rpr.append(tam)


def poner_caminos(tc, caminos: str) -> None:
    """Llena las líneas C1, C2 y C3 del template; borra las que el caso no usa y,
    si el caso tiene más caminos, agrega líneas con el formato de la última."""
    lineas = [l.strip() for l in caminos.split("\n") if l.strip()]
    plantilla = parrafos(tc)[1:]
    for _ in range(len(lineas) - len(plantilla)):
        plantilla.append(copy.deepcopy(plantilla[-1]))
        tc.append(plantilla[-1])
    for i, p in enumerate(plantilla):
        if i < len(lineas):
            texto_run(runs(p)[0], lineas[i])
        else:
            tc.remove(p)


def llenar_ficha(tbl, caso: dict[str, Any], resultado: dict[str, Any]) -> None:
    codigo = caso["Código"]
    molde_run = runs(parrafos(celda(tbl, 1, 0))[1])[0]  # run negro sin formato especial
    poner_valor(celda(tbl, 1, 0), 1, codigo)
    dia, mes, anio = resultado["fecha"].split("/")
    poner_valor(celda(tbl, 2, 0), 1, f"{dia} / {mes} / {anio}")
    poner_valor(celda(tbl, 2, 1), 1, f"{resultado['duracion_min']} min")
    poner_valor(celda(tbl, 4, 0), 1, caso["Módulo"])
    poner_valor(celda(tbl, 4, 1), 1, caso["RF / RNF"])
    poner_valor(celda(tbl, 5, 0), 1, caso["Descripción del requisito"])
    poner_valor(celda(tbl, 7, 0), 1, resultado["archivo"])
    poner_valor(celda(tbl, 7, 1), 1, resultado["funcion"])
    poner_codigo(celda(tbl, 8, 0), con_marcas(codigo, resultado["fragmento"]))
    poner_caminos(celda(tbl, 9, 0), caso["Caminos o condiciones a probar"])
    poner_valor(celda(tbl, 11, 0), 1, caso["Precondiciones"])
    poner_valor(celda(tbl, 14, 0), 1, caso["Caso de prueba"])
    poner_valor(celda(tbl, 15, 0), 1, caso["Datos de entrada"])
    poner_valor(celda(tbl, 15, 1), 1, caso["Resultado esperado"])
    prueba = f"tests/caja_blanca/test_pcb_{codigo[-2:]}.py"
    poner_pasos(celda(tbl, 16, 0), f"1. {CASOS[codigo]['preparar']}\n" + PASOS_COMUNES.format(prueba=prueba))
    poner_valor(celda(tbl, 18, 0), 1, resultado["resultado_obtenido"], molde_run)
    marcar(celda(tbl, 18, 1), [resultado["veredicto"]])
    poner_valor(celda(tbl, 19, 0), 1, resultado["caminos_ejecutados"])
    marcar(celda(tbl, 19, 1), resultado["evidencia"])
    poner_valor(celda(tbl, 20, 0), 1, resultado.get("observaciones") or "", molde_run)
    quitar_guias(tbl)
    no_partir(tbl, SECCIONES)


def generar() -> None:
    casos = leer_casos()
    resultados = json.loads((CARPETA / "resultados.json").read_text(encoding="utf-8"))
    origen = Document(CARPETA / "Template_Prueba_Caja_Blanca.docx")
    plantilla, sect_pr = vaciar_cuerpo(origen)
    doc = Document(SALIDA) if SALIDA.exists() else origen
    plantilla = copiar_ficha_con_imagenes(plantilla, origen, doc)

    if SALIDA.exists():
        sect_pr = conservar_introduccion(doc, (plantilla,))

        # La portada y la guía se conservan; solo se actualizan fecha y resultados.
        total_caminos = sum(len(CASOS[codigo]["obtenido"]) for codigo in resultados)
        aprobados = sum(r["veredicto"] == "Aprobado" for r in resultados.values())
        caminos_ejecutados = sum(len(r["caminos"]) for r in resultados.values())
        valores = {
            "Fecha de ejecución": next(iter(resultados.values()))["fecha"],
            "Casos aprobados": f"{aprobados} de {len(resultados)}",
            "Caminos ejecutados": f"{caminos_ejecutados} de {total_caminos}",
        }
        actualizar_valores_portada(doc, valores)
        for tabla in doc.tables:
            for fila in tabla.rows:
                etiqueta = fila.cells[0].text.strip()
                if etiqueta in resultados and len(fila.cells) == 6:
                    destino, texto = fila.cells[3], str(len(resultados[etiqueta]["caminos"]))
                else:
                    continue
                rs = destino.paragraphs[0].runs
                rs[0].text = texto
                for r in rs[1:]:
                    r.text = ""

    elementos = []
    for i, (codigo, caso) in enumerate(casos.items()):
        if i:
            elementos.append(salto_de_pagina(doc))
        tbl = copy.deepcopy(plantilla)
        llenar_ficha(tbl, caso, resultados[codigo])
        elementos.append(tbl)
        elementos.extend(agregar_evidencia(
            doc, codigo, EVIDENCIAS / f"{codigo}.png", PIE_FIGURA.format(codigo=codigo), ANCHO_EVIDENCIA_CM
        ))

    for e in elementos:
        sect_pr.addprevious(e)
    doc.save(SALIDA)
    print(SALIDA)


if __name__ == "__main__":
    generar()
