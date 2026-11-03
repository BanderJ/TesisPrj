"""PCN-11 a PCN-15: peso final y Factor de Rendimiento (RF06, RF07).

Precondición común: evaluación con peso total = 300, peso de muestra = 300 g,
peso trillado y tamizado = 240 g, y monitoreo finalizado (se arma por API).
FR = peso final / (peso de muestra / 100). Los rangos de precio se aplican al FR.
"""
from decimal import Decimal
from typing import Any

import httpx
import pytest
from playwright.sync_api import Page

from tests.caja_negra.conftest import Registro, captura, consultar, evaluacion_finalizada


@pytest.fixture(autouse=True)
def _precios(precios_de_hoy: None) -> None:
    return None


def _ingresar_peso_final(page: Page, evaluacion_id: str, peso: int) -> dict[str, Any]:
    page.goto(f"/analisis/{evaluacion_id}")
    page.wait_for_selector("#inputPesoBuenoAnalisis", state="visible")
    page.fill("#inputPesoBuenoAnalisis", str(peso))
    page.click("#btnGuardarPesoBuenoAnalisis")
    page.wait_for_function(
        "() => !document.getElementById('pesoBuenoErrorAnalisis').hidden"
        " || document.getElementById('rendFactor').textContent.trim() !== '—'",
        timeout=15000,
    )
    page.wait_for_timeout(500)
    error = page.locator("#pesoBuenoErrorAnalisis")
    mensaje = error.inner_text().strip() if error.is_visible() else ""
    factor = page.locator("#rendFactor").inner_text().strip()
    fila = consultar("SELECT factor_rendimiento FROM evaluacion WHERE id = %s", (evaluacion_id,))
    return {"mensaje": mensaje, "factor": factor, "factor_bd": fila["factor_rendimiento"] if fila else None}


def _acepta(page: Page, api: httpx.Client, registro: Registro, codigo: str, peso: int, esperado: str) -> None:
    registro.iniciar(codigo)
    eva = evaluacion_finalizada(api)
    r = _ingresar_peso_final(page, eva["evaluacion_id"], peso)
    captura(page, codigo, full_page=True)
    ok = not r["mensaje"] and r["factor_bd"] is not None and Decimal(str(r["factor_bd"])) == Decimal(esperado)
    if ok:
        obtenido = (
            f"El sistema aceptó el peso final de {peso} g en la evaluación {eva['codigo']} y calculó "
            f"automáticamente el Factor de Rendimiento = {r['factor']}. La consulta a la base de datos "
            f"confirma factor_rendimiento = {r['factor_bd']}."
        )
    else:
        obtenido = (
            f"Con un peso final de {peso} g (evaluación {eva['codigo']}) el sistema "
            + (f"mostró el mensaje \"{r['mensaje']}\" y no completó el cálculo." if r["mensaje"]
               else f"calculó FR = {r['factor']} (base de datos: {r['factor_bd']}), distinto de {esperado}.")
        )
    registro.guardar(codigo, obtenido, ok, ["Captura de pantalla", "Consulta BD"])
    assert ok, obtenido


def _rechaza(page: Page, api: httpx.Client, registro: Registro, codigo: str, peso: int,
             observaciones: str = "") -> None:
    registro.iniciar(codigo)
    eva = evaluacion_finalizada(api)
    r = _ingresar_peso_final(page, eva["evaluacion_id"], peso)
    captura(page, codigo, full_page=True)
    ok = bool(r["mensaje"]) and r["factor_bd"] is None
    if ok:
        obtenido = (
            f"Con un peso final de {peso} g (evaluación {eva['codigo']}) el sistema mostró el mensaje "
            f"\"{r['mensaje']}\" y no completó el cálculo: el Factor de Rendimiento sigue sin registrar "
            "en la base de datos."
        )
    else:
        obtenido = (
            f"El sistema aceptó el peso final de {peso} g (evaluación {eva['codigo']}) y calculó "
            f"FR = {r['factor_bd']}."
        )
    registro.guardar(codigo, obtenido, ok, ["Captura de pantalla"], observaciones)
    assert ok, obtenido


def test_pcn11_calculo_fr(page_operario: Page, api: httpx.Client, registro: Registro) -> None:
    _acepta(page_operario, api, registro, "PCN-11", 200, "66.67")


def test_pcn12_peso_final_mayor_trillado(page_operario: Page, api: httpx.Client, registro: Registro) -> None:
    _rechaza(page_operario, api, registro, "PCN-12", 250)


def test_pcn13_peso_final_igual_trillado(page_operario: Page, api: httpx.Client, registro: Registro) -> None:
    _acepta(page_operario, api, registro, "PCN-13", 240, "80.00")


def test_pcn14_peso_final_minimo(page_operario: Page, api: httpx.Client, registro: Registro) -> None:
    _acepta(page_operario, api, registro, "PCN-14", 120, "40.00")


def test_pcn15_peso_final_bajo_minimo(page_operario: Page, api: httpx.Client, registro: Registro) -> None:
    _rechaza(page_operario, api, registro, "PCN-15", 119,
             "FR = 119 / (300 / 100) = 39.67; no hay rango de precio registrado por debajo de 40.")
