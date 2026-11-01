"""Convierte los manuales Markdown de docs/manuales/ a Word (.docx).

Uso:
    python convert_md_to_docx.py                       # todos los .md de docs/manuales/
    python convert_md_to_docx.py docs/manuales/X.md    # uno o varios archivos

El .docx se guarda junto al .md, con el mismo nombre.

Además del Markdown básico (títulos, listas, tablas, código, negrita):
    <!-- indice -->              índice de Word en ese lugar y títulos numerados (I., 1.1., 1.1.1.)
    <!-- comentario -->          notas internas: no pasan al .docx
    ![Pie de figura](img/x.png){ancho=8}
                                 imagen relativa al .md, ancho opcional en cm. Si el archivo no
                                 existe se inserta un recuadro "IMAGEN PENDIENTE" con el pie y la ruta.
    **Organización:** valor      en el encabezado, se usa como subtítulo de la portada.

Word pide actualizar el índice al abrir el documento (los campos se calculan al abrirlo).
"""

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docx.text.paragraph import Paragraph

CARPETA_MANUALES = Path(__file__).resolve().parent / "docs" / "manuales"

VERDE = RGBColor(21, 128, 61)
GRIS_TEXTO = RGBColor(64, 64, 64)
FONDO_ENCABEZADO = "15803D"
FONDO_FILA_PAR = "F2F7F3"
FONDO_CODIGO = "F3F4F6"
FUENTE = "Calibri"
FUENTE_CODIGO = "Consolas"
ANCHO_TABLA_CM = 16.0
ANCHO_IMAGEN_CM = 15.0
ORGANIZACION_POR_DEFECTO = "Cooperativa Agraria Line Coffee Marañón"
MARCA_INDICE = "<!-- indice -->"

PATRON_IMAGEN = re.compile(r"^!\[(.*?)\]\((.+?)\)(?:\{ancho=([\d.]+)\})?$")
PATRON_INLINE = re.compile(r"\*\*(.+?)\*\*|`([^`]+)`|\[([^\]]+)\]\(([^)]+)\)")
PATRON_NUMERADA = re.compile(r"^(\s*)(\d+)\.\s+(.*)$")
PATRON_VIÑETA = re.compile(r"^(\s*)[-*]\s+(.*)$")


def sombrear(elemento, color: str) -> None:
    """Aplica color de fondo a una celda o párrafo."""
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    if hasattr(elemento, "_tc"):
        elemento._tc.get_or_add_tcPr().append(shd)
    else:
        elemento._p.get_or_add_pPr().append(shd)


def agregar_inline(parrafo: Paragraph, texto: str, negrita: bool = False, color: RGBColor | None = None) -> None:
    """Escribe texto con **negrita**, `código` y [enlaces](#ancla) de Markdown."""
    ultimo = 0
    for m in PATRON_INLINE.finditer(texto):
        if m.start() > ultimo:
            run = parrafo.add_run(texto[ultimo:m.start()])
            run.bold = negrita or None
            if color:
                run.font.color.rgb = color
        if m.group(1) is not None:
            run = parrafo.add_run(m.group(1))
            run.bold = True
            if color:
                run.font.color.rgb = color
        elif m.group(2) is not None:
            run = parrafo.add_run(m.group(2))
            run.font.name = FUENTE_CODIGO
            run.font.size = Pt(9.5)
            run.bold = negrita or None
        else:
            # Los enlaces internos del índice no navegan en Word: se deja el texto.
            run = parrafo.add_run(m.group(3))
            run.bold = negrita or None
        ultimo = m.end()
    if ultimo < len(texto):
        run = parrafo.add_run(texto[ultimo:])
        run.bold = negrita or None
        if color:
            run.font.color.rgb = color


def configurar_documento(doc: Document) -> None:
    seccion = doc.sections[0]
    seccion.page_width, seccion.page_height = Cm(21), Cm(29.7)
    for lado in ("top_margin", "bottom_margin"):
        setattr(seccion, lado, Cm(2.5))
    for lado in ("left_margin", "right_margin"):
        setattr(seccion, lado, Cm(2.5))

    normal = doc.styles["Normal"]
    normal.font.name = FUENTE
    normal.font.size = Pt(11)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), FUENTE)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.15

    for nivel, tamaño in ((1, 16), (2, 13), (3, 11.5)):
        estilo = doc.styles[f"Heading {nivel}"]
        estilo.font.name = FUENTE
        estilo.font.size = Pt(tamaño)
        estilo.font.bold = True
        estilo.font.color.rgb = VERDE
        # Sin esto Word usa la fuente del tema en lugar de FUENTE.
        fuentes = estilo.element.rPr.rFonts
        for atributo in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
            fuentes.attrib.pop(qn(atributo), None)
        estilo.paragraph_format.space_before = Pt(18 if nivel == 1 else 12)
        estilo.paragraph_format.space_after = Pt(6)
        estilo.paragraph_format.keep_with_next = True

    agregar_numero_pagina(seccion)


def agregar_numero_pagina(seccion) -> None:
    parrafo = seccion.footer.paragraphs[0]
    parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    agregar_campo(parrafo, "PAGE", "1")
    for run in parrafo.runs:
        run.font.size = Pt(9)
        run.font.color.rgb = GRIS_TEXTO


def agregar_campo(parrafo: Paragraph, instruccion: str, texto_previo: str) -> None:
    """Inserta un campo de Word (índice, número de página) con un texto hasta que se actualice."""
    for tipo, contenido in (("begin", None), ("instr", instruccion), ("separate", None),
                            ("texto", texto_previo), ("end", None)):
        run = parrafo.add_run()
        if tipo == "instr":
            elemento = OxmlElement("w:instrText")
            elemento.set(qn("xml:space"), "preserve")
            elemento.text = contenido
        elif tipo == "texto":
            run.text = contenido
            continue
        else:
            elemento = OxmlElement("w:fldChar")
            elemento.set(qn("w:fldCharType"), tipo)
        run._r.append(elemento)


def agregar_indice(doc: Document) -> None:
    p = doc.add_paragraph()
    run = p.add_run("Tabla de contenido")
    run.bold = True
    run.font.size = Pt(16)
    run.font.color.rgb = VERDE
    agregar_campo(doc.add_paragraph(), 'TOC \\o "1-3" \\h \\z \\u',
                  "Clic derecho aquí y elija Actualizar campo para generar el índice.")
    # Word recalcula los campos al abrir el documento.
    actualizar = OxmlElement("w:updateFields")
    actualizar.set(qn("w:val"), "true")
    doc.settings.element.append(actualizar)
    doc.add_page_break()


def numero_romano(n: int) -> str:
    valores = ((10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"))
    resultado = ""
    for valor, letra in valores:
        while n >= valor:
            resultado += letra
            n -= valor
    return resultado


def agregar_imagen(doc: Document, carpeta_md: Path, pie: str, ruta: str, ancho_cm: float | None,
                   numero: int) -> None:
    archivo = carpeta_md / ruta
    if archivo.is_file():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True
        p.add_run().add_picture(str(archivo), width=Cm(ancho_cm or ANCHO_IMAGEN_CM))
    else:
        tabla = doc.add_table(rows=1, cols=1)
        tabla.style = "Table Grid"
        tabla.alignment = WD_TABLE_ALIGNMENT.CENTER
        celda = tabla.rows[0].cells[0]
        celda.width = Cm(ANCHO_TABLA_CM)
        sombrear(celda, FONDO_CODIGO)
        p = celda.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.keep_with_next = True
        run = p.add_run("IMAGEN PENDIENTE")
        run.bold = True
        run.font.color.rgb = GRIS_TEXTO
        p = celda.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True
        agregar_inline(p, pie, color=GRIS_TEXTO)
        p = celda.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(18)
        run = p.add_run(f"Archivo: {ruta}")
        run.font.name = FUENTE_CODIGO
        run.font.size = Pt(9)
        run.font.color.rgb = GRIS_TEXTO

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"Figura {numero}. ")
    run.bold = True
    run.font.size = Pt(9.5)
    agregar_inline(p, pie)
    for run in p.runs[1:]:
        run.italic = True
        run.font.size = Pt(9.5)


def agregar_portada(doc: Document, titulo: str, organizacion: str, metadatos: list[str]) -> None:
    for _ in range(6):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(titulo)
    run.bold = True
    run.font.size = Pt(26)
    run.font.color.rgb = VERDE

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(organizacion)
    run.font.size = Pt(13)
    run.font.color.rgb = GRIS_TEXTO

    for _ in range(4):
        doc.add_paragraph()
    for linea in metadatos:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)
        agregar_inline(p, linea)
    doc.add_page_break()


def agregar_tabla(doc: Document, filas: list[list[str]]) -> None:
    columnas = max(len(f) for f in filas)
    tabla = doc.add_table(rows=len(filas), cols=columnas)
    tabla.style = "Table Grid"
    tabla.alignment = WD_TABLE_ALIGNMENT.CENTER
    tabla.autofit = False

    # Ancho de cada columna proporcional a su texto más largo, con mínimo y tope.
    pesos = [
        min(max(max((len(f[j]) for f in filas if j < len(f)), default=0), 10), 60)
        for j in range(columnas)
    ]
    anchos = [Cm(ANCHO_TABLA_CM * p / sum(pesos)) for p in pesos]

    for i, fila in enumerate(filas):
        if i == 0:
            # Repite el encabezado en cada página y no lo deja solo al pie.
            tr_pr = tabla.rows[0]._tr.get_or_add_trPr()
            encabezado = OxmlElement("w:tblHeader")
            encabezado.set(qn("w:val"), "true")
            tr_pr.append(encabezado)
        for j in range(columnas):
            celda = tabla.rows[i].cells[j]
            celda.width = anchos[j]
            parrafo = celda.paragraphs[0]
            parrafo.paragraph_format.space_after = Pt(0)
            parrafo.paragraph_format.line_spacing = 1.0
            texto = fila[j] if j < len(fila) else ""
            if i == 0:
                parrafo.paragraph_format.keep_with_next = True
                sombrear(celda, FONDO_ENCABEZADO)
                agregar_inline(parrafo, texto, negrita=True, color=RGBColor(255, 255, 255))
            else:
                if i % 2 == 0:
                    sombrear(celda, FONDO_FILA_PAR)
                agregar_inline(parrafo, texto)
            for run in parrafo.runs:
                if run.font.size is None:
                    run.font.size = Pt(10)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def agregar_codigo(doc: Document, lineas: list[str]) -> None:
    p = doc.add_paragraph()
    sombrear(p, FONDO_CODIGO)
    p.paragraph_format.left_indent = Cm(0.5)
    run = p.add_run("\n".join(lineas))
    run.font.name = FUENTE_CODIGO
    run.font.size = Pt(9)


def agregar_numerada(doc: Document, numero: str, texto: str, nivel: int) -> None:
    # Número escrito a mano: la numeración automática de Word continuaría entre listas.
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.9 + 0.7 * nivel)
    p.paragraph_format.first_line_indent = Cm(-0.6)
    p.paragraph_format.space_after = Pt(3)
    p.add_run(f"{numero}.\t")
    agregar_inline(p, texto)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(0.9 + 0.7 * nivel))


def agregar_viñeta(doc: Document, texto: str, nivel: int) -> None:
    p = doc.add_paragraph(style="List Bullet 2" if nivel else "List Bullet")
    p.paragraph_format.space_after = Pt(3)
    agregar_inline(p, texto)


def convertir(ruta_md: Path) -> Path:
    lineas = ruta_md.read_text(encoding="utf-8").splitlines()
    doc = Document()
    configurar_documento(doc)

    # Encabezado del manual: título (#) y líneas **Campo:** valor antes del primer ---.
    i = 0
    titulo = ruta_md.stem.replace("_", " ")
    organizacion = ORGANIZACION_POR_DEFECTO
    metadatos: list[str] = []
    while i < len(lineas) and lineas[i].strip() != "---":
        linea = lineas[i].strip()
        if linea.startswith("# "):
            titulo = linea[2:].strip()
        elif linea.startswith("**Organización:**"):
            organizacion = linea.removeprefix("**Organización:**").strip()
        elif linea:
            metadatos.append(linea)
        i += 1
    agregar_portada(doc, titulo, organizacion, metadatos)

    con_indice = any(l.strip() == MARCA_INDICE for l in lineas)
    numeros = [0, 0, 0]  # capítulo, sección, subsección
    figuras = 0
    secciones = 0
    while i < len(lineas):
        linea = lineas[i].rstrip()
        i += 1
        texto = linea.strip()

        if texto == MARCA_INDICE:
            agregar_indice(doc)
            continue

        if texto.startswith("<!--"):
            while "-->" not in texto and i < len(lineas):
                texto = lineas[i]
                i += 1
            continue

        if not texto or texto == "---":
            continue

        imagen = PATRON_IMAGEN.match(texto)
        if imagen:
            figuras += 1
            ancho = float(imagen.group(3)) if imagen.group(3) else None
            agregar_imagen(doc, ruta_md.parent, imagen.group(1), imagen.group(2), ancho, figuras)
            continue

        if texto.startswith("```"):
            codigo: list[str] = []
            while i < len(lineas) and not lineas[i].strip().startswith("```"):
                codigo.append(lineas[i].rstrip())
                i += 1
            i += 1
            agregar_codigo(doc, codigo)
            continue

        if texto.startswith("|"):
            filas: list[list[str]] = []
            while texto.startswith("|"):
                celdas = [c.strip() for c in texto.strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", c) for c in celdas):
                    filas.append(celdas)
                if i >= len(lineas):
                    break
                texto = lineas[i].strip()
                if texto.startswith("|"):
                    i += 1
            agregar_tabla(doc, filas)
            continue

        encabezado = re.match(r"^(#{2,4})\s+(.*)$", texto)
        if encabezado:
            nivel = len(encabezado.group(1)) - 1
            texto_titulo = encabezado.group(2)
            if con_indice:
                numeros[nivel - 1] += 1
                numeros[nivel:] = [0] * (3 - nivel)
                if nivel == 1:
                    prefijo = f"{numero_romano(numeros[0])}."
                else:
                    prefijo = ".".join(str(n) for n in numeros[:nivel]) + "."
                texto_titulo = f"{prefijo} {texto_titulo}"
            elif nivel == 1:
                secciones += 1
                # Sin índice de Word, la primera sección es el índice en Markdown:
                # el contenido empieza en página nueva.
                if secciones == 2:
                    doc.add_page_break()
            doc.add_heading(texto_titulo, level=nivel)
            continue

        numerada = PATRON_NUMERADA.match(linea)
        if numerada:
            agregar_numerada(doc, numerada.group(2), numerada.group(3), len(numerada.group(1)) // 2)
            continue

        viñeta = PATRON_VIÑETA.match(linea)
        if viñeta:
            agregar_viñeta(doc, viñeta.group(2), 1 if len(viñeta.group(1)) >= 2 else 0)
            continue

        if texto.startswith("> "):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.8)
            agregar_inline(p, texto[2:], color=GRIS_TEXTO)
            continue

        agregar_inline(doc.add_paragraph(), texto)

    ruta_docx = ruta_md.with_suffix(".docx")
    doc.save(ruta_docx)
    return ruta_docx


def main() -> None:
    rutas = [Path(a) for a in sys.argv[1:]] or sorted(CARPETA_MANUALES.glob("*.md"))
    for ruta in rutas:
        print(f"{ruta} -> {convertir(ruta)}")


if __name__ == "__main__":
    main()
