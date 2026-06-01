import os

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates

from src.utilities.jwt_required import obtener_usuario_actual
from src.schemas.perfil import (
    ActualizarDatosPersonales,
    ActualizarUsuario,
    CambiarContrasena,
    CambiarContraseñaUsuario,
    CambiarEstadoUsuario,
    CrearUsuario,
)
from src.services.perfil_service import PerfilService

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))

perfil = APIRouter()
perfil_service = PerfilService()


def verificar_admin_o_gerente(user: dict) -> None:
    if user.get("tipo_personal_id") not in [2, 3]:
        raise HTTPException(status_code=403, detail="No tienes permisos para acceder a esta sección")


@perfil.get("/")
async def obtener_pagina_perfil(
    request: Request,
    user: dict = Depends(obtener_usuario_actual),
):
    try:
        datos = perfil_service.obtener_datos_usuario(user["personal_id"])
        return templates.TemplateResponse(
            request=request,
            name="perfil.html",
            context={"request": request, "user": user, "datos": datos},
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error al cargar el perfil") from exc


@perfil.patch("/datos-personales")
async def actualizar_datos_personales(
    body: ActualizarDatosPersonales,
    user: dict = Depends(obtener_usuario_actual),
):
    try:
        return perfil_service.actualizar_datos_personales(
            personal_id=user["personal_id"],
            nombre=body.nombre,
            ape_paterno=body.ape_paterno,
            ape_materno=body.ape_materno,
            telefono=body.telefono,
            correo=body.correo,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error al actualizar los datos") from exc


@perfil.patch("/cambiar-contrasena")
async def cambiar_contrasena(
    body: CambiarContrasena,
    user: dict = Depends(obtener_usuario_actual),
):
    try:
        return perfil_service.cambiar_contrasena(
            personal_id=user["personal_id"],
            clave_actual=body.clave_actual,
            clave_nueva=body.clave_nueva,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error al cambiar la contraseña") from exc


@perfil.get("/usuarios/personas-disponibles")
async def obtener_personas_sin_usuario(
    user: dict = Depends(obtener_usuario_actual),
):
    try:
        verificar_admin_o_gerente(user)
        return {"personas": perfil_service.obtener_personas_sin_usuario()}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error al obtener personas disponibles") from exc


@perfil.get("/usuarios")
async def listar_usuarios(
    user: dict = Depends(obtener_usuario_actual),
):
    try:
        verificar_admin_o_gerente(user)
        return {"usuarios": perfil_service.listar_usuarios()}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error al listar usuarios") from exc


@perfil.get("/usuarios/{personal_id}")
async def obtener_usuario(
    personal_id: str,
    user: dict = Depends(obtener_usuario_actual),
):
    try:
        verificar_admin_o_gerente(user)
        usuario = perfil_service.obtener_usuario(personal_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return usuario
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error al obtener el usuario") from exc


@perfil.patch("/usuarios/{personal_id}/estado")
async def cambiar_estado_usuario(
    personal_id: str,
    body: CambiarEstadoUsuario,
    user: dict = Depends(obtener_usuario_actual),
):
    try:
        verificar_admin_o_gerente(user)
        return perfil_service.cambiar_estado_usuario(personal_id, body.estado)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error al cambiar el estado") from exc


@perfil.patch("/usuarios/{personal_id}/cambiar-contrasena")
async def cambiar_contrasena_usuario(
    personal_id: str,
    body: CambiarContraseñaUsuario,
    user: dict = Depends(obtener_usuario_actual),
):
    try:
        verificar_admin_o_gerente(user)
        return perfil_service.cambiar_contrasena_usuario(
            personal_id=personal_id,
            clave_nueva=body.clave_nueva,
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error al cambiar la contraseña") from exc


@perfil.patch("/usuarios/{personal_id}")
async def actualizar_usuario(
    personal_id: str,
    body: ActualizarUsuario,
    user: dict = Depends(obtener_usuario_actual),
):
    try:
        verificar_admin_o_gerente(user)
        return perfil_service.actualizar_usuario(
            personal_id=personal_id,
            nombre=body.nombre,
            ape_paterno=body.ape_paterno,
            ape_materno=body.ape_materno,
            sexo=body.sexo,
            fecha_nacimiento=body.fecha_nacimiento,
            telefono=body.telefono,
            correo=body.correo,
            ubigeo=body.ubigeo,
            tipo_personal_id=body.tipo_personal_id,
            clave_nueva=body.clave_nueva,
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error al actualizar el usuario") from exc


@perfil.post("/usuarios/crear")
async def crear_usuario(
    body: CrearUsuario,
    user: dict = Depends(obtener_usuario_actual),
):
    try:
        verificar_admin_o_gerente(user)
        return perfil_service.crear_usuario(
            nombre=body.nombre,
            ape_paterno=body.ape_paterno,
            ape_materno=body.ape_materno,
            sexo=body.sexo,
            fecha_nacimiento=body.fecha_nacimiento,
            tipo_documento_id=body.tipo_documento_id,
            num_documento=body.num_documento,
            telefono=body.telefono,
            correo=body.correo,
            ubigeo=body.ubigeo,
            tipo_personal_id=body.tipo_personal_id,
            clave=body.clave,
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error al crear el usuario") from exc
