"""PCN-07 a PCN-10: registro de la muestra (RF02).

Mapeo de los datos del caso a la pantalla de registro:
  peso total                 -> campo "Peso total" (kg) y "Peso de muestra" = 300 g
  peso trillado y tamizado   -> campos "Peso trillado" y "Peso tamizado" con el mismo valor
Los campos que el caso no menciona llevan los valores de MUESTRA_BASE.
"""
from typing import Any

import pytest
from playwright.sync_api import Page

from tests.caja_negra.conftest import (
    MUESTRA_BASE, USUARIOS_PRUEBA, Registro, captura, consultar,
)

# El botón de registro consulta el sensor de la tapa (Arduino) antes de enviar.
# Sin el prototipo conectado se simula la tapa cerrada: el caso prueba el registro,
# no el hardware.
OBS_SENSOR = (
    "Ejecutado sin el prototipo: la respuesta del sensor de la tapa (GET /arduino/estado) "
    "se simuló como 'tapa cerrada' para poder enviar el formulario."
)


@pytest.fixture(autouse=True)
def _precios(precios_de_hoy: None) -> None:
    return None


def _llenar_formulario(page: Page, peso_total: str, peso_trillado_tamizado: str) -> None:
    page.goto("/registro")
    page.wait_for_load_state("networkidle")
    page.evaluate("""() => {
        const sel = document.getElementById('tipoDocumento');
        const op = [...sel.options].find(o => /DNI/i.test(o.textContent));
        sel.value = op.value;
        sel.dispatchEvent(new Event('change', { bubbles: true }));
    }""")
    page.fill("#numDocumento", MUESTRA_BASE["num_documento"])
    page.wait_for_function("document.getElementById('nombreCaficultor').value.trim() !== ''", timeout=15000)
    page.select_option("#tipoGrano", str(MUESTRA_BASE["tipo_grano_id"]))
    page.fill("#numSacos", str(MUESTRA_BASE["num_sacos"]))
    page.fill("#pesoTotal", peso_total)
    page.fill("#humedad", str(MUESTRA_BASE["humedad"]))
    page.select_option("#pesoMuestra", str(MUESTRA_BASE["peso_muestra"]))
    page.fill("#pesoTrillado", peso_trillado_tamizado)
    page.select_option("#numTamiz", str(MUESTRA_BASE["num_tamiz"]))
    page.fill("#pesoTamizado", peso_trillado_tamizado)


def _simular_tapa_cerrada(page: Page) -> None:
    page.route("**/arduino/estado", lambda ruta: ruta.fulfill(
        status=200, content_type="application/json",
        body='{"listo": true, "mensaje": "Tapa cerrada"}',
    ))


def _enviar(page: Page) -> dict[str, Any]:
    """Presiona el botón y devuelve lo que ocurrió: redirección o mensaje de rechazo."""
    # El sistema enfoca el campo inválido y luego abre el aviso, que toma el foco:
    # se guarda el último campo del formulario que recibió el foco.
    page.evaluate("""() => {
        window.__focos = [];
        document.addEventListener('focusin', e => window.__focos.push(e.target.id || ''));
    }""")
    page.click("#startMonitoringBtn")
    # El aviso se cierra solo a los pocos segundos: se lee apenas aparece.
    mensaje = ""
    for _ in range(75):
        if "/monitoreo/" in page.url:
            # El monitoreo consulta el estado de la cámara de forma periódica: la red
            # nunca queda inactiva, se espera la carga y un margen para que se dibuje.
            page.wait_for_load_state("load")
            page.wait_for_timeout(2000)
            return {"registrado": True, "evaluacion_id": page.url.rstrip("/").split("/")[-1]}
        if page.locator("#cm-msg").is_visible():
            mensaje = page.locator("#cm-msg").inner_text()
            break
        if page.locator("#submitError").count() and page.locator("#submitError").inner_text().strip():
            mensaje = page.locator("#submitError").inner_text()
            break
        page.wait_for_timeout(200)
    campo = page.evaluate(
        "() => [...window.__focos].reverse().find(id => id && !id.startsWith('cm-') && id !== 'startMonitoringBtn') || ''"
    )
    etiqueta, ayuda = page.evaluate("""id => [
        document.querySelector(`label[for='${id}']`)?.textContent.trim() || id,
        document.getElementById(`${id}Hint`)?.textContent.trim() || ''
    ]""", campo) if campo else ("", "")
    return {"registrado": False, "mensaje": " ".join(mensaje.split()), "campo": etiqueta, "ayuda": ayuda}


def _usuario_de(evaluacion_id: str) -> str | None:
    fila = consultar(
        "SELECT p.usuario FROM evaluacion e JOIN personal p ON p.personal_id = e.personal_id WHERE e.id = %s",
        (evaluacion_id,),
    )
    return fila["usuario"] if fila else None


def _caso_exitoso(page: Page, registro: Registro, codigo: str, peso_total: str, peso_tt: str) -> None:
    registro.iniciar(codigo)
    _simular_tapa_cerrada(page)
    _llenar_formulario(page, peso_total, peso_tt)
    resultado = _enviar(page)
    captura(page, codigo)
    operario = USUARIOS_PRUEBA["operario"][0]
    if resultado["registrado"]:
        usuario = _usuario_de(resultado["evaluacion_id"])
        ok = usuario == operario
        obtenido = (
            f"La muestra se registró (peso total = {peso_total} kg, peso de muestra = 300 g, peso trillado "
            f"y tamizado = {peso_tt} g) y el sistema pasó a la pantalla de monitoreo. La consulta a la base "
            f"de datos confirma que la evaluación {resultado['evaluacion_id']} quedó asociada al usuario "
            f"\"{usuario}\"."
        )
    else:
        ok = False
        obtenido = (
            f"La muestra no se registró. El sistema mostró el mensaje \"{resultado['mensaje']}\""
            + (f" y señaló el campo \"{resultado['campo']}\"." if resultado["campo"] else ".")
        )
    registro.guardar(codigo, obtenido, ok, ["Captura de pantalla", "Consulta BD"], OBS_SENSOR,
                     datos_formulario(peso_total, peso_tt))
    assert ok, obtenido


def datos_formulario(peso_total: str, peso_tt: str) -> str:
    """Pesos tal como se ingresaron en el formulario de registro."""
    return (
        f"peso total = {peso_total} kg\n"
        f"peso de muestra = {MUESTRA_BASE['peso_muestra']} g\n"
        f"peso trillado = {peso_tt} g\n"
        f"peso tamizado = {peso_tt} g"
    )


def _caso_rechazo(page: Page, registro: Registro, codigo: str, peso_total: str, peso_tt: str,
                  campo_esperado: str) -> None:
    registro.iniciar(codigo)
    _simular_tapa_cerrada(page)
    _llenar_formulario(page, peso_total, peso_tt)
    resultado = _enviar(page)
    captura(page, codigo)
    if resultado["registrado"]:
        ok = False
        obtenido = (f"El sistema registró la muestra (evaluación {resultado['evaluacion_id']}) "
                    "en lugar de rechazarla.")
    else:
        ok = bool(resultado["mensaje"]) and campo_esperado.lower() in resultado["campo"].lower()
        obtenido = (
            f"El registro se rechazó. El sistema mostró el aviso \"{resultado['mensaje']}\" y llevó el "
            f"foco al campo \"{resultado['campo']}\""
            + (f", que muestra debajo la indicación \"{resultado['ayuda']}\"." if resultado["ayuda"] else ".")
        )
    registro.guardar(codigo, obtenido, ok, ["Captura de pantalla"])
    assert ok, obtenido


def test_pcn07_pesos_validos(page_operario: Page, registro: Registro) -> None:
    _caso_exitoso(page_operario, registro, "PCN-07", "300", "240")


def test_pcn08_peso_total_cero(page_operario: Page, registro: Registro) -> None:
    _caso_rechazo(page_operario, registro, "PCN-08", "0", "240", "Peso total")


def test_pcn09_peso_negativo(page_operario: Page, registro: Registro) -> None:
    _caso_rechazo(page_operario, registro, "PCN-09", "300", "-50", "Peso trillado")


def test_pcn10_trillado_maximo(page_operario: Page, registro: Registro) -> None:
    _caso_exitoso(page_operario, registro, "PCN-10", "300", "249")
