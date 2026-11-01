"""Utilidades comunes para llenar las fichas Word de pruebas (caja negra y caja blanca).

Cada generador copia la tabla de su template por caso (deepcopy) y la llena con
estas funciones, que trabajan sobre el XML de la tabla para no alterar el formato
de la ficha oficial.
"""
import copy
from io import BytesIO
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from docx.text.paragraph import Paragraph

GRIS = "808080"
CASILLA_VACIA, CASILLA_MARCADA = "☐", "☒"


def celda(tbl, fila: int, col: int):
    return tbl.findall(qn("w:tr"))[fila].findall(qn("w:tc"))[col]


def parrafos(tc) -> list:
    return tc.findall(qn("w:p"))


def runs(p) -> list:
    return p.findall(qn("w:r"))


def texto_run(r, texto: str) -> None:
    """Pone el texto en el run; los saltos de línea pasan a <w:br/>."""
    for hijo in r.findall(qn("w:t")) + r.findall(qn("w:br")):
        r.remove(hijo)
    for i, linea in enumerate(texto.split("\n")):
        if i:
            r.append(OxmlElement("w:br"))
        t = OxmlElement("w:t")
        t.set(qn("xml:space"), "preserve")
        t.text = linea
        r.append(t)


def _formato_normal(r) -> None:
    """Quita el formato de texto guía (gris, 8 pt) para que el valor use el de la ficha."""
    rpr = r.find(qn("w:rPr"))
    if rpr is None:
        return
    for etiqueta in ("w:color", "w:sz", "w:szCs", "w:i", "w:iCs"):
        for e in rpr.findall(qn(etiqueta)):
            rpr.remove(e)
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "000000")
    rpr.append(color)


def poner_valor(tc, indice: int, texto: str, molde_run=None) -> None:
    """Reemplaza el párrafo de valor de la celda (índice) por `texto`."""
    p = parrafos(tc)[indice]
    rs = runs(p)
    if not rs:
        r = copy.deepcopy(molde_run)
        p.append(r)
        rs = [r]
    for sobrante in rs[1:]:
        p.remove(sobrante)
    _formato_normal(rs[0])
    texto_run(rs[0], texto)


def poner_pasos(tc, pasos: str) -> None:
    """Sustituye las líneas numeradas del template por los pasos del caso."""
    molde = parrafos(tc)[1]
    for p in parrafos(tc)[1:]:
        tc.remove(p)
    for linea in [l.strip() for l in pasos.split("\n") if l.strip()]:
        numero, _, texto = linea.partition(" ")
        nuevo = copy.deepcopy(molde)
        r_numero = runs(nuevo)[0]
        texto_run(r_numero, f"{numero} ")
        # El número conserva el formato del template; el texto del paso va sin negrita.
        r_texto = copy.deepcopy(r_numero)
        rpr = r_texto.find(qn("w:rPr"))
        if rpr is not None:
            for etiqueta in ("w:b", "w:bCs"):
                for e in rpr.findall(qn(etiqueta)):
                    rpr.remove(e)
        texto_run(r_texto, texto)
        r_numero.addnext(r_texto)
        tc.append(nuevo)


def marcar(tc, etiquetas: list[str]) -> None:
    """Cambia ☐ por ☒ en las casillas cuyo texto siguiente empieza por una de las etiquetas."""
    for p in parrafos(tc):
        rs = runs(p)
        for i, r in enumerate(rs):
            texto = "".join(t.text or "" for t in r.findall(qn("w:t")))
            if texto != CASILLA_VACIA:
                continue
            siguiente = "".join(
                "".join(t.text or "" for t in x.findall(qn("w:t"))) for x in rs[i + 1:i + 3]
            ).strip()
            if any(siguiente.startswith(e) for e in etiquetas):
                texto_run(r, CASILLA_MARCADA)


def quitar_guias(tbl) -> None:
    """Borra cualquier texto guía gris entre corchetes que haya quedado."""
    for r in tbl.iter(qn("w:r")):
        color = r.find(f"{qn('w:rPr')}/{qn('w:color')}")
        texto = "".join(t.text or "" for t in r.findall(qn("w:t")))
        if color is not None and color.get(qn("w:val")) == GRIS and texto.strip().startswith("["):
            r.getparent().remove(r)


def no_partir(tbl, secciones: frozenset[int] = frozenset()) -> None:
    """Mantiene la ficha completa en una página: filas indivisibles y unidas a la siguiente.

    `secciones`: índices de las filas de encabezado de sección donde se permite el
    salto de página cuando la ficha no cabe en una sola; cada sección queda entera.
    """
    filas = tbl.findall(qn("w:tr"))
    for i, tr in enumerate(filas):
        trpr = tr.find(qn("w:trPr"))
        if trpr is None:
            trpr = OxmlElement("w:trPr")
            tr.insert(0, trpr)
        if trpr.find(qn("w:cantSplit")) is None:
            trpr.append(OxmlElement("w:cantSplit"))
        if i == len(filas) - 1 or i + 1 in secciones:
            continue
        for p in tr.iter(qn("w:p")):
            ppr = p.find(qn("w:pPr"))
            if ppr is None:
                ppr = OxmlElement("w:pPr")
                p.insert(0, ppr)
            if ppr.find(qn("w:keepNext")) is None:
                ppr.insert(0, OxmlElement("w:keepNext"))


def agregar_evidencia(
    doc: Document, codigo: str, imagen: Path, pie: str | None = None, ancho_cm: float = 15
) -> list:
    """Imagen bajo la ficha (15 cm por defecto) y su pie en Times New Roman 9."""
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(6)
    p_img.paragraph_format.keep_with_next = True
    p_img.add_run().add_picture(str(imagen), width=Cm(ancho_cm))
    p_pie = doc.add_paragraph()
    p_pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_pie = p_pie.add_run(pie or f"Figura {codigo}. Evidencia de la prueba")
    r_pie.font.name = "Times New Roman"
    r_pie._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    r_pie._element.rPr.rFonts.set(qn("w:cs"), "Times New Roman")
    r_pie.font.size = Pt(9)
    return [p_img._p, p_pie._p]


def salto_de_pagina(doc: Document):
    p: Paragraph = doc.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)
    return p._p


def vaciar_cuerpo(doc: Document):
    """Vacía el cuerpo sin tocar sectPr (encabezado, pie y márgenes) y devuelve
    (tabla plantilla, sectPr) para rearmar el documento antes de sectPr."""
    cuerpo = doc.element.body
    plantilla = doc.tables[0]._tbl
    for hijo in list(cuerpo):
        if hijo.tag != qn("w:sectPr"):
            cuerpo.remove(hijo)
    return plantilla, cuerpo.find(qn("w:sectPr"))


def copiar_ficha_con_imagenes(plantilla: Any, origen: Document, destino: Document) -> Any:
    """Copia la ficha y sus imágenes usando las relaciones del documento de destino."""
    ficha = copy.deepcopy(plantilla)
    referencias: dict[str, str] = {}
    for nodo in ficha.iter():
        id_origen = nodo.get(qn("r:embed"))
        if id_origen is None:
            continue
        relacion = origen.part.rels[id_origen]
        if relacion.reltype != RT.IMAGE or relacion.is_external:
            continue
        if id_origen not in referencias:
            id_destino, _ = destino.part.get_or_add_image(BytesIO(relacion.target_part.blob))
            referencias[id_origen] = id_destino
        nodo.set(qn("r:embed"), referencias[id_origen])
    return ficha


def conservar_introduccion(doc: Document, elementos_reutilizados: tuple[Any, ...] = ()) -> Any:
    """Retira las fichas y sus imágenes sin uso, conservando portada, guía y recursos reutilizados."""
    cuerpo = doc.element.body
    inicio = next(
        i for i, e in enumerate(cuerpo)
        if e.tag == qn("w:tbl") and "Código de la prueba" in "".join(e.itertext())
    )
    for e in list(cuerpo)[inicio:]:
        if e.tag != qn("w:sectPr"):
            cuerpo.remove(e)
    atributos_relacion = {qn("r:id"), qn("r:embed"), qn("r:link")}
    for parte in doc.part.package.parts:
        elemento = getattr(parte, "element", None)
        if elemento is None:
            continue
        raices = (elemento, *elementos_reutilizados) if parte is doc.part else (elemento,)
        usados = {
            valor for raiz in raices for e in raiz.iter()
            for atributo, valor in e.attrib.items() if atributo in atributos_relacion
        }
        for id_relacion, relacion in list(parte.rels.items()):
            if relacion.reltype == RT.IMAGE and id_relacion not in usados:
                parte.drop_rel(id_relacion)
    return cuerpo.find(qn("w:sectPr"))


def actualizar_valores_portada(doc: Document, valores: dict[str, str]) -> None:
    """Actualiza valores por su rótulo conservando el formato de las celdas."""
    for tabla in doc.tables:
        for fila in tabla.rows:
            etiqueta = fila.cells[0].text.strip()
            if etiqueta in valores:
                rs = fila.cells[1].paragraphs[0].runs
                rs[0].text = valores[etiqueta]
                for r in rs[1:]:
                    r.text = ""
