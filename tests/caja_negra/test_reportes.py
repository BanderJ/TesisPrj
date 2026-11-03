"""PCN-19 a PCN-21: reportes e historial (RF09, RF10, RNF07).

Usan la evaluación completada más reciente del operario de prueba (la deja PCN-11,
PCN-13 o PCN-14), buscada desde la pantalla "Buscar reportes".
"""
import html
import re
from decimal import Decimal
from typing import Any

import openpyxl
import pdfplumber
import pytest
from playwright.sync_api import Page

from tests.caja_negra.conftest import (
    EVIDENCIAS, USUARIOS_PRUEBA, Registro, captura, captura_compuesta, consultar,
)


@pytest.fixture(scope="module")
def evaluacion() -> dict[str, Any]:
    fila = consultar(
        """
        SELECT e.id::text AS evaluacion_id, e.codigo, e.fecha, p.usuario
        FROM evaluacion e JOIN personal p ON p.personal_id = e.personal_id
        WHERE p.usuario = %s AND e.factor_rendimiento IS NOT NULL
        ORDER BY e.fecha DESC LIMIT 1
        """,
        (USUARIOS_PRUEBA["operario"][0],),
    )
    if not fila:
        pytest.skip("No hay una evaluación finalizada del operario de prueba; ejecutar antes PCN-11.")
    return fila


def _buscar(page: Page, codigo: str) -> None:
    page.goto("/reporte")
    page.wait_for_load_state("networkidle")
    page.click("#inputCodigo")
    page.keyboard.type(codigo.removeprefix("EVA"))
    page.click("#btnBuscar")
    page.wait_for_function(f"document.getElementById('tdCodigo').textContent.trim() === '{codigo}'",
                           timeout=15000)
    page.wait_for_timeout(500)


def test_pcn19_exportar_pdf(page_operario: Page, registro: Registro, evaluacion: dict[str, Any]) -> None:
    registro.iniciar("PCN-19")
    page = page_operario
    # "Exportar PDF" abre el diálogo de impresión del navegador; en Chromium sin interfaz
    # el diálogo no existe, así que se registra la llamada y el PDF se genera con la
    # misma hoja de estilos de impresión que usa ese diálogo.
    page.add_init_script("window.print = () => { window.__imprimio = true; };")
    _buscar(page, evaluacion["codigo"])
    page.click(".btn-export.pdf:visible")
    imprimio = page.evaluate("() => window.__imprimio === true")
    page.emulate_media(media="print")
    ruta_pdf = EVIDENCIAS / f"PCN-20_{evaluacion['codigo']}.pdf"
    page.pdf(path=str(ruta_pdf), format="A4", print_background=True)
    captura(page, "PCN-19", full_page=True)
    with pdfplumber.open(ruta_pdf) as pdf:
        texto = "\n".join(p.extract_text() or "" for p in pdf.pages)
        paginas = len(pdf.pages)
    ok = imprimio and evaluacion["codigo"] in texto
    obtenido = (
        f"Al presionar \"Exportar PDF\" sobre la evaluación {evaluacion['codigo']}, el sistema abrió el "
        "diálogo de impresión del navegador, desde el que se guarda como PDF. El PDF generado "
        f"({paginas} página(s)) contiene el código de la evaluación y sus datos."
        if ok else
        f"Exportar PDF no produjo un documento con los datos de la evaluación (impresión invocada: {imprimio})."
    )
    registro.guardar(
        "PCN-19", obtenido, ok, ["Captura de pantalla"],
        "El sistema no descarga el archivo directamente: usa el diálogo de impresión del navegador "
        "(opción \"Guardar como PDF\"). En la prueba automatizada el PDF se generó con el modo de impresión de "
        f"Chromium y se guardó como evidencias/{ruta_pdf.name}.",
        f"Evaluación = {evaluacion['codigo']}\nformato = PDF",
    )
    assert ok, obtenido


def _tabla_html(filas: list[tuple[Any, ...]], titulo: str) -> str:
    celdas = "".join(
        "<tr>" + "".join(f"<td>{html.escape('' if v is None else str(v))}</td>" for v in fila) + "</tr>"
        for fila in filas
    )
    return (
        "<html><body style='font-family:Calibri,Arial;font-size:15px;margin:16px'>"
        f"<p style='font-weight:bold'>{html.escape(titulo)}</p>"
        "<table style='border-collapse:collapse' border='1' cellpadding='4'>" + celdas + "</table></body></html>"
    )


def test_pcn20_exportar_excel(page_operario: Page, registro: Registro, evaluacion: dict[str, Any]) -> None:
    registro.iniciar("PCN-20")
    page = page_operario
    _buscar(page, evaluacion["codigo"])
    antes = page.screenshot()
    with page.expect_download() as info:
        page.click("#btnExcel")
    descarga = info.value
    ruta_xlsx = EVIDENCIAS / f"PCN-21_{descarga.suggested_filename}"
    descarga.save_as(ruta_xlsx)

    hoja = openpyxl.load_workbook(ruta_xlsx).active
    filas = [tuple(c.value for c in fila) for fila in hoja.iter_rows()]
    valores = {str(f[0]).strip(): str(f[1] or "").strip() for f in filas if f and f[0]}

    # Datos de la evaluación según el sistema (misma consulta que usa la pantalla).
    d = page.request.get(f"/evaluacion/buscar?codigo={evaluacion['codigo']}").json()
    esperados = {
        "Código evaluación": d["codigo"],
        "Caficultor": d["caficultor_nombre"],
        "Documento": d["num_documento"],
        "Registrado por": d["registrado_por"],
        "Peso muestra": f"{Decimal(str(d['peso_muestra'])):.2f}",
        "Peso trillado": f"{Decimal(str(d['peso_trillado'])):.2f}",
        "Peso tamizado": f"{Decimal(str(d['peso_tamizado'])):.2f}",
        "Factor rendimiento": f"{Decimal(str(d['factor_rendimiento'])):.2f}",
    }
    diferencias = [
        f"{campo}: archivo \"{valores.get(campo, '(no está)')}\", sistema \"{valor}\""
        for campo, valor in esperados.items() if valor not in valores.get(campo, "")
    ]

    contenido = page.context.new_page()
    contenido.set_content(_tabla_html(filas, f"Contenido de {descarga.suggested_filename} (hoja \"{hoja.title}\")"))
    contenido.set_viewport_size({"width": 1366, "height": 900})
    tabla = contenido.screenshot(full_page=True)
    contenido.close()
    captura_compuesta("PCN-20", [
        ("Pantalla de la evaluación al presionar \"Exportar Excel\"", antes),
        ("Contenido del archivo descargado", tabla),
    ])

    ok = descarga.suggested_filename.endswith(".xlsx") and not diferencias
    obtenido = (
        f"Al presionar \"Exportar Excel\" sobre la evaluación {evaluacion['codigo']}, el sistema descargó el "
        f"archivo {descarga.suggested_filename} (XLSX, hoja \"{hoja.title}\", {len(filas)} filas). El archivo "
        "contiene los datos de la evaluación y coinciden con los del sistema: "
        + ", ".join(f"{c.lower()} = {valores[c]}" for c in esperados) + "."
        if ok else
        f"El archivo descargado ({descarga.suggested_filename}) no coincide con los datos de la evaluación: "
        + "; ".join(diferencias) + "."
    )
    registro.guardar(
        "PCN-20", obtenido, ok, ["Captura de pantalla"],
        f"El archivo descargado se guardó como evidencias/{ruta_xlsx.name}. La captura muestra la pantalla "
        "(arriba) y el contenido del archivo (abajo).",
        f"Evaluación = {evaluacion['codigo']}\nformato = Excel",
    )
    assert ok, obtenido


def test_pcn21_buscar_historial(page_operario: Page, registro: Registro, evaluacion: dict[str, Any]) -> None:
    registro.iniciar("PCN-21")
    page = page_operario
    _buscar(page, evaluacion["codigo"])
    fecha = page.locator("#tdFecha").inner_text().strip()
    usuario = page.locator("#metaRegistradoPor").inner_text().strip()
    factor = page.locator("#rendFactor").inner_text().strip()
    captura(page, "PCN-21", full_page=True)
    tiene_hora = bool(re.search(r"\d{1,2}:\d{2}", fecha))
    ok = tiene_hora and usuario not in ("", "—") and factor not in ("", "—")
    obtenido = (
        f"Al buscar el código {evaluacion['codigo']} en \"Buscar reportes\", el sistema mostró la evaluación "
        f"con sus datos y su reporte (Factor de Rendimiento = {factor}), la fecha y hora \"{fecha}\" y el "
        f"usuario que la registró \"{usuario}\". En la base de datos la evaluación tiene fecha "
        f"{evaluacion['fecha']:%d/%m/%Y %H:%M} y usuario \"{evaluacion['usuario']}\"."
    )
    if not tiene_hora:
        obtenido += " La fecha mostrada no incluye la hora."
    registro.guardar(
        "PCN-21", obtenido, ok, ["Captura de pantalla", "Consulta BD"],
        "La búsqueda es por código de evaluación; la pantalla no ofrece búsqueda por fecha.",
        f"Criterio de búsqueda = código {evaluacion['codigo']}",
    )
    assert ok, obtenido
