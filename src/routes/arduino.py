from typing import Any

from fastapi import APIRouter, Depends

from src.services.arduino_service import arduino_service
from src.utilities.jwt_required import obtener_usuario_actual

arduino_router = APIRouter(prefix="/arduino", tags=["arduino"])


@arduino_router.get("/estado")
async def estado_arduino(_: dict[str, Any] = Depends(obtener_usuario_actual)) -> dict[str, Any]:
    return arduino_service.obtener_estado()


@arduino_router.get("/peso")
async def obtener_peso(_: dict[str, Any] = Depends(obtener_usuario_actual)) -> dict[str, Any]:
    return arduino_service.obtener_peso()


@arduino_router.post("/tare")
async def tarar_bascula(_: dict[str, Any] = Depends(obtener_usuario_actual)) -> dict[str, Any]:
    return arduino_service.tarar_bascula()


@arduino_router.post("/motor/iniciar")
async def iniciar_motor(_: dict[str, Any] = Depends(obtener_usuario_actual)) -> dict[str, Any]:
    return arduino_service.iniciar_motor()


@arduino_router.post("/motor/detener")
async def detener_motor(_: dict[str, Any] = Depends(obtener_usuario_actual)) -> dict[str, Any]:
    return arduino_service.detener_motor()
