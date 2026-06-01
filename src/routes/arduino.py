"""
GET  /arduino/estado        → estado del sensor ultrasónico (tapa cerrada)
GET  /arduino/peso          → lectura de la celda de carga (gramos)
POST /arduino/tare          → tara la báscula (poner en cero)
POST /arduino/motor/iniciar → envía ON  al Arduino (faja arranca)
POST /arduino/motor/detener → envía OFF al Arduino (faja para)
"""
from typing import Any

from fastapi import APIRouter, Depends

from src.config import Config
from src.utilities.arduino_serial import arduino_serial
from src.utilities.jwt_required import obtener_usuario_actual

arduino_router = APIRouter(prefix="/arduino", tags=["arduino"])

_UMBRAL_CM = 20.0


@arduino_router.get("/estado")
async def estado_arduino(
    _: dict[str, Any] = Depends(obtener_usuario_actual),
) -> dict[str, Any]:
    """
    Consulta el sensor ultrasónico del Arduino.
    Retorna si la muestra está correctamente posicionada en la banda
    (distancia < 20 cm) para habilitar el paso a la pantalla de monitoreo.
    """
    estado = arduino_serial.obtener_estado()

    if not estado.conectado:
        return {
            "listo": False,
            "distancia": None,
            "conectado": False,
            "mensaje": f"Arduino no conectado ({Config.ARDUINO_PORT}). Verifique el cable USB.",
        }

    if estado.error and estado.distancia is None:
        return {
            "listo": False,
            "distancia": None,
            "conectado": True,
            "mensaje": "No se recibió lectura del sensor. Verifique el Arduino.",
        }

    dist = estado.distancia
    dist_str = f"{dist:.1f} cm" if dist is not None and dist >= 0 else "sin lectura"

    if estado.listo:
        return {
            "listo": True,
            "distancia": dist,
            "conectado": True,
            "mensaje": f"Muestra detectada a {dist_str}. Lista para iniciar.",
        }

    return {
        "listo": False,
        "distancia": dist,
        "conectado": True,
        "mensaje": "Debe cerrar la tapa luego de haber ingresado los granos de café para continuar al monitoreo.",
    }


@arduino_router.get("/peso")
async def obtener_peso(
    _: dict[str, Any] = Depends(obtener_usuario_actual),
) -> dict[str, Any]:
    """
    Retorna el último peso leído de la celda de carga (HX711).
    El valor es el promedio deslizante de las últimas 5 muestras.
    """
    estado = arduino_serial.obtener_estado()
    if not estado.conectado:
        return {
            "peso": None,
            "conectado": False,
            "mensaje": f"Arduino no conectado ({Config.ARDUINO_PORT}).",
        }

    peso = arduino_serial.obtener_peso()
    if peso is None:
        return {
            "peso": None,
            "conectado": True,
            "mensaje": "Esperando lectura de la báscula...",
        }

    return {
        "peso": round(peso, 2),
        "conectado": True,
        "mensaje": f"{round(peso, 2)} g",
    }


@arduino_router.post("/tare")
async def tarar_bascula(
    _: dict[str, Any] = Depends(obtener_usuario_actual),
) -> dict[str, Any]:
    """Envía comando TARE al Arduino: pone la báscula en cero."""
    ok = arduino_serial.enviar_comando("TARE")
    return {
        "ok": ok,
        "mensaje": "Tara enviada. La báscula se está calibrando." if ok else "No se pudo enviar tara. Verifique la conexión Arduino.",
    }


@arduino_router.post("/motor/iniciar")
async def iniciar_motor(
    _: dict[str, Any] = Depends(obtener_usuario_actual),
) -> dict[str, Any]:
    """Envía comando ON al Arduino: arranca la faja transportadora."""
    ok = arduino_serial.enviar_comando("ON")
    return {
        "activo": ok,
        "mensaje": "Faja iniciada." if ok else "No se pudo iniciar la faja. Verifique la conexión Arduino.",
    }


@arduino_router.post("/motor/detener")
async def detener_motor(
    _: dict[str, Any] = Depends(obtener_usuario_actual),
) -> dict[str, Any]:
    """Envía comando OFF al Arduino: detiene la faja transportadora."""
    ok = arduino_serial.enviar_comando("OFF")
    return {
        "activo": False,
        "mensaje": "Faja detenida." if ok else "No se pudo detener la faja. Verifique la conexión Arduino.",
    }
