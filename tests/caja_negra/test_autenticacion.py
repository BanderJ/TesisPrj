"""PCN-01 a PCN-06: autenticación (RF01, RNF06)."""
from urllib.parse import urlparse

from playwright.sync_api import Page

from tests.caja_negra.conftest import (
    CLAVE_PRUEBA, USUARIOS_PRUEBA, Registro, captura, captura_compuesta, iniciar_sesion,
)

EVIDENCIA = ["Captura de pantalla"]
# Las contraseñas no se transcriben en la ficha.
CLAVE_REGISTRADA = "contraseña registrada del usuario (no se transcribe)"
OBS_CAPTURA_DOBLE = (
    "La captura muestra el formulario con el usuario ingresado antes de presionar \"Iniciar Sesión\" (arriba) "
    "y la respuesta del sistema (abajo). Tras el rechazo, el sistema vacía el campo usuario."
)


def _mensaje_login(page: Page) -> str:
    """Texto del mensaje de error que la plantilla de login muestra al fallar."""
    error = page.get_by_text("Credenciales incorrectas")
    return error.first.inner_text().strip() if error.count() else ""


def _login_rechazado(page: Page, codigo: str, usuario: str, clave: str) -> dict[str, str | bool]:
    """Intenta iniciar sesión y guarda la captura doble: formulario lleno y respuesta."""
    page.goto("/auth/login")
    page.fill("#usuario", usuario)
    page.fill("#clave", clave)
    antes = page.screenshot()
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")
    despues = page.screenshot()
    captura_compuesta(codigo, [
        ("Antes de presionar \"Iniciar Sesión\"", antes),
        ("Respuesta del sistema", despues),
    ])
    return {
        "mensaje": _mensaje_login(page),
        "en_login": "/auth/login" in page.url,
        "cookie": any(c["name"] == "access_token" for c in page.context.cookies()),
    }


def test_pcn01_credenciales_validas(page: Page, registro: Registro) -> None:
    registro.iniciar("PCN-01")
    usuario = USUARIOS_PRUEBA["operario"][0]
    iniciar_sesion(page, usuario, CLAVE_PRUEBA)
    # El nombre del usuario se muestra en el menú del avatar de la cabecera.
    page.click("#avatarBtn")
    page.wait_for_timeout(400)
    nombre = page.locator(".dropdown-user-name").inner_text().strip()
    handle = page.locator(".dropdown-user-handle").inner_text().strip()
    captura(page, "PCN-01")
    ok = "/auth/login" not in page.url and handle == usuario and bool(nombre)
    obtenido = (
        f"El sistema concedió el acceso y redirigió a la página de inicio ({urlparse(page.url).path}). "
        f"El menú del usuario en la cabecera muestra el nombre \"{nombre}\" y el usuario \"{handle}\"."
        if ok else f"No se concedió el acceso. URL final: {page.url}."
    )
    registro.guardar("PCN-01", obtenido, ok, EVIDENCIA,
                     datos_entrada=f"usuario = {usuario}\ncontraseña = {CLAVE_REGISTRADA}")
    assert ok, obtenido


def test_pcn02_clave_incorrecta(page: Page, registro: Registro) -> None:
    registro.iniciar("PCN-02")
    usuario = USUARIOS_PRUEBA["operario"][0]
    r = _login_rechazado(page, "PCN-02", usuario, "ClaveIncorrecta#1")
    mensaje = r["mensaje"]
    ok = r["en_login"] and not r["cookie"] and bool(mensaje)
    obtenido = (
        f"Acceso denegado: el sistema permanece en la pantalla de inicio de sesión y muestra "
        f"el mensaje \"{mensaje}\"." if ok else f"Resultado inesperado. URL final: {page.url}; mensaje: \"{mensaje}\"."
    )
    registro.guardar("PCN-02", obtenido, ok, EVIDENCIA, OBS_CAPTURA_DOBLE,
                     f"usuario = {usuario}\ncontraseña = distinta de la registrada (no se transcribe)")
    assert ok, obtenido


def test_pcn03_usuario_no_registrado(page: Page, registro: Registro) -> None:
    registro.iniciar("PCN-03")
    usuario = "usuario_inexistente_pcn"
    r = _login_rechazado(page, "PCN-03", usuario, "CualquierValor1")
    mensaje = r["mensaje"]
    ok = r["en_login"] and not r["cookie"] and bool(mensaje)
    obtenido = (
        f"Acceso denegado: el sistema permanece en la pantalla de inicio de sesión y muestra "
        f"el mensaje \"{mensaje}\"." if ok else f"Resultado inesperado. URL final: {page.url}; mensaje: \"{mensaje}\"."
    )
    registro.guardar("PCN-03", obtenido, ok, EVIDENCIA, OBS_CAPTURA_DOBLE,
                     f"usuario = {usuario}\ncontraseña = cualquier valor (no se transcribe)")
    assert ok, obtenido


def test_pcn04_campos_vacios(page: Page, registro: Registro) -> None:
    registro.iniciar("PCN-04")
    page.goto("/auth/login")
    page.click("button[type=submit]")
    page.wait_for_timeout(500)
    campo_invalido = page.eval_on_selector("#usuario", "el => !el.checkValidity()")
    clave_invalida = page.eval_on_selector("#clave", "el => !el.checkValidity()")
    captura(page, "PCN-04")
    ok = "/auth/login" in page.url and campo_invalido and clave_invalida
    obtenido = (
        "El formulario no se envía: ambos campos están marcados como obligatorios (atributo required) "
        "y el navegador muestra su aviso de campo obligatorio sobre el campo usuario. No se concede el acceso."
        if ok else f"Resultado inesperado. URL final: {page.url}."
    )
    registro.guardar(
        "PCN-04", obtenido, ok, EVIDENCIA,
        "El aviso lo genera la validación nativa del navegador, en el idioma del navegador. La captura "
        "se tomó con Chromium sin interfaz, que no dibuja la burbuja del aviso.",
    )
    assert ok, obtenido


def test_pcn05_registro_sin_sesion(page: Page, registro: Registro) -> None:
    registro.iniciar("PCN-05")
    page.goto("/registro")
    page.wait_for_load_state("networkidle")
    captura(page, "PCN-05")
    ok = "/auth/login" in page.url
    obtenido = (
        "Al ingresar directamente la URL /registro sin sesión, el sistema bloqueó el acceso y "
        "redirigió a la pantalla de inicio de sesión (/auth/login)."
        if ok else f"El sistema no redirigió al inicio de sesión. URL final: {page.url}."
    )
    registro.guardar("PCN-05", obtenido, ok, EVIDENCIA)
    assert ok, obtenido


def test_pcn06_cuenta_desactivada(page: Page, registro: Registro) -> None:
    registro.iniciar("PCN-06")
    usuario = USUARIOS_PRUEBA["desactivado"][0]
    r = _login_rechazado(page, "PCN-06", usuario, CLAVE_PRUEBA)
    mensaje = r["mensaje"]
    # Con la cuenta desactivada, una ruta protegida también debe negar el acceso.
    page.goto("/registro")
    page.wait_for_load_state("networkidle")
    sigue_en_login = "/auth/login" in page.url
    ok = not r["cookie"] and sigue_en_login
    obtenido = (
        f"Acceso impedido: el sistema no emitió la cookie de sesión, mostró el mensaje \"{mensaje}\" "
        "y, al intentar abrir /registro, redirigió al inicio de sesión."
        if ok else "El sistema concedió una sesión a la cuenta desactivada."
    )
    registro.guardar(
        "PCN-06", obtenido, ok, EVIDENCIA,
        "El mensaje es el mismo que para credenciales incorrectas; no indica que la cuenta está desactivada. "
        + OBS_CAPTURA_DOBLE,
        f"usuario = {usuario}\ncontraseña = {CLAVE_REGISTRADA}",
    )
    assert ok, obtenido
