"""Imagen de evidencia PCB-XX.png: resultado por camino y cobertura de la función evaluada.

Parte 1: tabla con una fila por camino (condición, dato, esperado, obtenido, estado)
y el comando ejecutado. Parte 2: captura del reporte HTML de coverage recortada a
las líneas de la función (los mismos segmentos que el fragmento de la ficha), con
las etiquetas C1/C2/C3, la cobertura de la función y la leyenda de colores.
"""
import base64
import html
import re
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, sync_playwright

from tests.caja_blanca.casos import EVIDENCIAS
from tests.caja_blanca.codigo import fuente, marcas, segmentos

LEYENDA = "Verde: línea ejecutada · Rojo: línea no ejecutada · Amarillo: rama ejecutada parcialmente"

ESTILO_REPORTE = """
#header, #index, footer, #scroll_marker, .button_show_hide_help { display: none !important; }
#source { padding-top: 0 !important; margin-top: 0 !important; }
#source p { line-height: 1.3 !important; }
.etiqueta { margin-left: 14px; padding: 0 6px; border-radius: 3px; background: #1f3a5f;
            color: #fff; font-weight: bold; font-family: Consolas, monospace; }
"""

ESTILO_PAGINA = """
body { margin: 0; background: #fff; }
#evidencia { width: 1100px; padding: 12px 16px; background: #fff; color: #111; line-height: 1.3;
             font-family: "Segoe UI", Arial, sans-serif; font-size: 15px; }
h2 { font-size: 17px; margin: 0 0 6px; }
h2.cobertura { margin-top: 14px; }
table { width: 100%; border-collapse: collapse; table-layout: fixed; }
th, td { border: 1px solid #9a9a9a; padding: 4px 7px; vertical-align: top; text-align: left; }
th { background: #e9ecef; }
col.camino { width: 70px; } col.estado { width: 88px; }
.passed { color: #1a7f37; font-weight: bold; } .failed { color: #cf222e; font-weight: bold; }
.comando { font-family: Consolas, monospace; font-size: 13px; margin: 5px 0 0; color: #333; }
.archivo { font-family: Consolas, monospace; font-size: 13px; margin-bottom: 6px; color: #333; }
.codigo { border: 1px solid #c8c8c8; }
.codigo img { display: block; width: 100%; }
.salto { font-family: Consolas, monospace; color: #777; padding: 2px 8px; background: #f6f6f6;
         border-top: 1px solid #ddd; border-bottom: 1px solid #ddd; }
.resumen { margin: 6px 0 2px; font-weight: bold; }
.leyenda { margin: 0; color: #333; font-size: 14px; }
"""


def por_camino(texto: str, caminos: list[str]) -> dict[str, str]:
    """Reparte un campo del Excel ("C1: ...", "C1 y C3: ...") por camino. Las líneas
    sin prefijo son comunes a todos los caminos y van primero."""
    comunes: list[str] = []
    propios: dict[str, list[str]] = {c: [] for c in caminos}
    for linea in (l.strip() for l in str(texto).split("\n") if l.strip()):
        m = re.match(r"^(C\d(?:\s*y\s*C\d)*)\s*:\s*(.*)$", linea)
        if m:
            for c in re.findall(r"C\d", m.group(1)):
                propios[c].append(m.group(2))
        else:
            comunes.append(linea)
    return {c: "; ".join(comunes + propios[c]) for c in caminos}


def _rangos(bloque: list[int]) -> list[tuple[int, int]]:
    """Líneas consecutivas de un segmento como (inicio, fin); un docstring omitido parte el rango."""
    rangos: list[tuple[int, int]] = []
    for n in bloque:
        if rangos and n == rangos[-1][1] + 1:
            rangos[-1] = (rangos[-1][0], n)
        else:
            rangos.append((n, n))
    return rangos


def _capturar_reporte(page: Page, reporte: Path, caso: dict[str, Any]) -> list[str]:
    """Recortes PNG (base64) del reporte HTML de coverage, uno por rango de líneas."""
    bloques = segmentos(caso)
    lineas = fuente(caso)
    numeros = [n for b in bloques for n in b]
    etiquetas = {
        str(numeros[i]): comentario.removeprefix("# ")
        for i, comentario in marcas(caso, [lineas[n - 1] for n in numeros]).items()
    }

    page.goto(reporte.as_uri())
    boton = page.locator("button.button_toggle_run")
    if "show_run" not in (boton.get_attribute("class") or ""):
        boton.click()  # coverage pinta de verde las líneas ejecutadas solo con este botón activo
    page.add_style_tag(content=ESTILO_REPORTE)
    page.evaluate(
        """(etiquetas) => {
            for (const [n, texto] of Object.entries(etiquetas)) {
                const s = document.createElement('span');
                s.className = 'etiqueta';
                s.textContent = texto;
                document.getElementById('t' + n).closest('p').querySelector('.t').appendChild(s);
            }
        }""",
        etiquetas,
    )
    # Una etiqueta al final de una línea larga puede salir del párrafo: se ensancha
    # la ventana para que quede dentro del recorte junto con la anotación de rama.
    derecha = page.evaluate(
        "Math.max(0, ...[...document.querySelectorAll('.etiqueta')].map(e => e.getBoundingClientRect().right))"
    )
    if derecha + 140 > page.viewport_size["width"]:
        page.set_viewport_size({"width": int(derecha + 140), "height": page.viewport_size["height"]})
    recortes = []
    for ini, fin in (r for b in bloques for r in _rangos(b)):
        # Desde el número de línea (a la izquierda del párrafo) hasta el borde derecho,
        # donde coverage pone la anotación de rama parcial ("640 ↛ 641").
        caja = page.evaluate(
            """([ini, fin]) => {
                const pa = document.getElementById('t' + ini).closest('p');
                const a = pa.getBoundingClientRect();
                const n = pa.querySelector('.n').getBoundingClientRect();
                const b = document.getElementById('t' + fin).closest('p').getBoundingClientRect();
                return {x: n.left + window.scrollX, y: a.top + window.scrollY,
                        width: a.right - n.left, height: b.bottom - a.top};
            }""",
            [ini, fin],
        )
        png = page.screenshot(full_page=True, clip=caja)
        recortes.append(base64.b64encode(png).decode())
    return recortes


def generar(
    codigo: str,
    caso: dict[str, Any],
    fila_excel: dict[str, Any],
    estados: dict[str, bool],
    obtenido: dict[str, str],
    comando: str,
    reporte: Path,
    cobertura: list[str],
) -> Path:
    """Arma la página de evidencia y la guarda como EVIDENCIAS/PCB-XX.png."""
    caminos = list(obtenido)
    condicion = por_camino(fila_excel["Caminos o condiciones a probar"], caminos)
    dato = por_camino(fila_excel["Datos de entrada"], caminos)
    esperado = por_camino(fila_excel["Resultado esperado"], caminos)
    e = html.escape

    filas = "".join(
        f"<tr><td><b>{c}</b></td><td>{e(condicion[c])}</td><td>{e(dato[c])}</td>"
        f"<td>{e(esperado[c])}</td><td>{e(obtenido[c])}</td>"
        f"<td class='{'passed' if estados.get(c) else 'failed'}'>{'PASSED' if estados.get(c) else 'FAILED'}</td></tr>"
        for c in caminos
    )
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        page = navegador.new_page(viewport={"width": 1100, "height": 900}, device_scale_factor=2)
        recortes = _capturar_reporte(page, reporte, caso)
        codigo_html = "<div class='salto'>⋮</div>".join(
            f"<img src='data:image/png;base64,{r}'>" for r in recortes
        )
        page.set_content(f"""<html><head><meta charset="utf-8"><style>{ESTILO_PAGINA}</style></head><body>
<div id="evidencia">
  <h2>{codigo} · Resultado por camino</h2>
  <table>
    <colgroup><col class="camino"><col><col><col><col><col class="estado"></colgroup>
    <tr><th>Camino</th><th>Condición</th><th>Dato de entrada</th><th>Resultado esperado</th>
        <th>Resultado obtenido</th><th>Estado</th></tr>
    {filas}
  </table>
  <p class="comando">$ {e(comando)}</p>
  <h2 class="cobertura">Cobertura de la función evaluada</h2>
  <div class="archivo">{e(caso['archivo'])} · {e(caso['funcion'])}</div>
  <div class="codigo">{codigo_html}</div>
  {''.join(f"<p class='resumen'>{e(l)}</p>" for l in cobertura)}
  <p class="leyenda">{LEYENDA}</p>
</div></body></html>""")
        salida = EVIDENCIAS / f"{codigo}.png"
        page.locator("#evidencia").screenshot(path=str(salida))
        navegador.close()
    return salida
