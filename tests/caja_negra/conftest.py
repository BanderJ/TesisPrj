"""Infraestructura de las pruebas de caja negra (PCN-XX).

Requisitos: la app corriendo en local (uvicorn src.main:app) contra la base de
desarrollo, y precios de café registrados con la fecha de hoy.

Cada prueba registra su resultado con `registro.guardar(...)`; al terminar la
sesión se fusiona con resultados.json de CAJA_NEGRA_DIR, así una corrida
parcial no borra los casos ya ejecutados.
"""
import io
import json
import math
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

import httpx
import pytest
from argon2 import PasswordHasher
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import Browser, Page, sync_playwright

from src.database.bd import Connection

BASE_URL: str = os.environ.get("CAJA_NEGRA_URL", "http://localhost:8000")
SALIDA: Path = Path(os.environ.get(
    "CAJA_NEGRA_DIR", r"D:\Ciclo 10\Tesis1\Documentacion\Pruebas\CajaNegra"
))
EVIDENCIAS: Path = SALIDA / "evidencias"

CLAVE_PRUEBA: str = "PruebaPCN#2026"
# usuario, documento de la persona, estado de la cuenta
USUARIOS_PRUEBA: dict[str, tuple[str, str, str]] = {
    "operario":    ("pcn_operario", "90000001", "A"),
    "desactivado": ("pcn_desactivado", "90000002", "I"),
}
TIPO_EVALUADOR: int = 1

# Caficultor activo ya registrado en la base de desarrollo.
DOC_CAFICULTOR: str = "99988877"
# Datos de la muestra comunes a los casos (unidades del sistema): peso total en kg,
# pesos de muestra en gramos. 300 kg con 5 sacos respeta el máximo de 70 kg por saco.
MUESTRA_BASE: dict[str, Any] = {
    "num_documento": DOC_CAFICULTOR,
    "num_sacos": 5,
    "peso_bruto": 300,
    "humedad": 12,
    "peso_muestra": 300,
    "peso_trillado": 240,
    "num_tamiz": 15,
    "peso_tamizado": 240,
    "tipo_grano_id": 1,
}


def _crear_usuarios_prueba() -> None:
    """Crea o restablece los usuarios de prueba en la base de desarrollo."""
    hasher = PasswordHasher(memory_cost=65536, time_cost=3, parallelism=4)
    db = Connection()
    try:
        cooperativa = db.obtener_uno("SELECT id FROM cooperativa LIMIT 1", ())
        for usuario, documento, estado in USUARIOS_PRUEBA.values():
            persona = db.obtener_uno("SELECT id FROM persona WHERE num_documento = %s", (documento,))
            if not persona:
                persona = db.obtener_uno(
                    """
                    INSERT INTO persona (nombre, ape_paterno, ape_materno, sexo, fecha_nacimiento,
                                         tipo_documento_id, num_documento, estado, cooperativa_id)
                    VALUES (%s, %s, %s, 'M', '1990-01-01', 1, %s, 'A', %s)
                    RETURNING id
                    """,
                    ("Operario", "Prueba", usuario.split("_")[1].capitalize(), documento, cooperativa["id"]),
                )
            db.ejecutar(
                """
                INSERT INTO personal (personal_id, tipo_personal_id, usuario, clave, estado)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (usuario) DO UPDATE SET clave = EXCLUDED.clave, estado = EXCLUDED.estado
                """,
                (persona["id"], TIPO_EVALUADOR, usuario, hasher.hash(CLAVE_PRUEBA), estado),
            )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def consultar(sql: str, params: tuple[Any, ...]) -> dict[str, Any] | None:
    """Consulta de verificación contra la base (evidencia 'Consulta BD')."""
    db = Connection()
    try:
        return db.obtener_uno(sql, params)
    finally:
        db.close()


class Registro:
    """Acumula los resultados de la sesión y los fusiona con resultados.json."""

    def __init__(self) -> None:
        self.resultados: dict[str, dict[str, Any]] = {}
        self.inicios: dict[str, float] = {}

    def iniciar(self, codigo: str) -> None:
        self.inicios[codigo] = time.monotonic()

    def guardar(
        self,
        codigo: str,
        resultado_obtenido: str,
        aprobado: bool,
        evidencia: list[str],
        observaciones: str = "",
        datos_entrada: str = "",
    ) -> None:
        """`datos_entrada`: valores reales usados; en la ficha reemplazan a los del Excel."""
        segundos = time.monotonic() - self.inicios.get(codigo, time.monotonic())
        self.resultados[codigo] = {
            "fecha": datetime.now().strftime("%d/%m/%Y"),
            "duracion_min": max(1, math.ceil(segundos / 60)),
            "resultado_obtenido": resultado_obtenido,
            "veredicto": "Aprobado" if aprobado else "Fallido",
            "evidencia": evidencia,
            "observaciones": observaciones,
        }
        if datos_entrada:
            self.resultados[codigo]["datos_entrada"] = datos_entrada

    def volcar(self) -> None:
        ruta = SALIDA / "resultados.json"
        previos: dict[str, Any] = {}
        if ruta.exists():
            previos = json.loads(ruta.read_text(encoding="utf-8"))
        previos.update(self.resultados)
        ordenados = dict(sorted(previos.items()))
        ruta.write_text(json.dumps(ordenados, ensure_ascii=False, indent=2), encoding="utf-8")


@pytest.fixture(scope="session")
def registro() -> Iterator[Registro]:
    EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    reg = Registro()
    yield reg
    reg.volcar()


@pytest.fixture(scope="session", autouse=True)
def usuarios_prueba() -> dict[str, tuple[str, str, str]]:
    _crear_usuarios_prueba()
    return USUARIOS_PRUEBA


@pytest.fixture(scope="session")
def browser() -> Iterator[Browser]:
    with sync_playwright() as pw:
        navegador = pw.chromium.launch(args=["--lang=es-PE"])
        yield navegador
        navegador.close()


@pytest.fixture()
def page(browser: Browser) -> Iterator[Page]:
    contexto = browser.new_context(
        base_url=BASE_URL, viewport={"width": 1366, "height": 900}, accept_downloads=True, locale="es-PE",
    )
    pagina = contexto.new_page()
    yield pagina
    contexto.close()


def iniciar_sesion(page: Page, usuario: str, clave: str) -> None:
    page.goto("/auth/login")
    page.fill("#usuario", usuario)
    page.fill("#clave", clave)
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")


@pytest.fixture()
def page_operario(page: Page) -> Page:
    iniciar_sesion(page, USUARIOS_PRUEBA["operario"][0], CLAVE_PRUEBA)
    return page


def captura(page: Page, codigo: str, full_page: bool = False) -> None:
    page.screenshot(path=str(EVIDENCIAS / f"{codigo}.png"), full_page=full_page)


def captura_compuesta(codigo: str, partes: list[tuple[str, bytes]]) -> None:
    """Une varias capturas en una sola imagen, una debajo de otra, cada una con su rótulo."""
    imagenes = [(rotulo, Image.open(io.BytesIO(png)).convert("RGB")) for rotulo, png in partes]
    alto_rotulo = 44
    ancho = max(img.width for _, img in imagenes)
    alto = sum(img.height + alto_rotulo for _, img in imagenes)
    lienzo = Image.new("RGB", (ancho, alto), "white")
    dibujo = ImageDraw.Draw(lienzo)
    try:
        fuente = ImageFont.truetype("arial.ttf", 24)
    except OSError:
        fuente = ImageFont.load_default()
    y = 0
    for rotulo, img in imagenes:
        dibujo.rectangle([0, y, ancho, y + alto_rotulo], fill="#e5e5e5")
        dibujo.text((14, y + 9), rotulo, fill="black", font=fuente)
        lienzo.paste(img, (0, y + alto_rotulo))
        y += alto_rotulo + img.height
    lienzo.save(EVIDENCIAS / f"{codigo}.png")


@pytest.fixture(scope="session")
def api() -> Iterator[httpx.Client]:
    """Cliente HTTP con la sesión del operario de prueba."""
    with httpx.Client(base_url=BASE_URL, timeout=30) as cliente:
        r = cliente.post("/auth/login", data={
            "usuario": USUARIOS_PRUEBA["operario"][0], "clave": CLAVE_PRUEBA,
        })
        assert "access_token" in cliente.cookies, f"No se pudo iniciar sesión por API ({r.status_code})"
        yield cliente


@pytest.fixture(scope="session")
def precios_de_hoy() -> None:
    fila = consultar("SELECT count(*) AS n FROM valor_cafe WHERE fecha::date = CURRENT_DATE", ())
    if not fila or fila["n"] == 0:
        pytest.exit("No hay precios de café con la fecha de hoy en la base de desarrollo.", returncode=2)


def evaluacion_finalizada(api: httpx.Client) -> dict[str, Any]:
    """Precondición de PCN-11 a PCN-15 y PCN-22 a PCN-24: muestra registrada
    (MUESTRA_BASE) y monitoreo finalizado. Devuelve evaluacion_id y codigo.

    El conteo que se guarda al finalizar lo toma el servidor de su tracker, así
    que se abre y se cierra un monitoreo de la evaluación (necesita la cámara
    conectada); sin granos en la faja el lote queda con 0 defectos y 0 sanos."""
    r = api.post("/evaluacion/registrar", json=MUESTRA_BASE)
    assert r.status_code == 201, f"Registro de la precondición falló: {r.status_code} {r.text}"
    evaluacion_id = r.json()["data"]["evaluacion_id"]
    r = api.post("/video/iniciar", json={"evaluacion_id": evaluacion_id})
    assert r.status_code == 200, f"Iniciar el monitoreo de la precondición falló: {r.status_code} {r.text}"
    r = api.post("/video/detener", json={"evaluacion_id": evaluacion_id})
    assert r.status_code == 200, f"Detener el monitoreo de la precondición falló: {r.status_code} {r.text}"
    r = api.patch(f"/evaluacion/{evaluacion_id}/finalizar", json={})
    assert r.status_code == 200, f"Finalizar la precondición falló: {r.status_code} {r.text}"
    return {"evaluacion_id": evaluacion_id, "codigo": r.json()["codigo"]}
