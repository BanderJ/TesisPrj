import os

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from fastapi.templating import Jinja2Templates

from src.services.auditoria_service import auditoria_service
from src.utilities.jwt_required import obtener_usuario_actual, require_admin_o_gerente
from src.utilities.jwt_utils import generar_token
from src.utilities.request_utils import get_client_ip
from src.schemas.perfil import (
    ActualizarDatosPersonales,
    ActualizarUsuario,
    CambiarContrasena,
    CambiarEstadoUsuario,
    CrearUsuario,
)
from src.services.perfil_service import PerfilService

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))

perfil = APIRouter()
perfil_service = PerfilService()



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
        raise HTTPException(status_code=500, detail="No se pudo cargar el perfil.") from exc


@perfil.patch("/datos-personales")
async def actualizar_datos_personales(
    request: Request,
    body: ActualizarDatosPersonales,
    user: dict = Depends(obtener_usuario_actual),
):
    try:
        result = perfil_service.actualizar_datos_personales(
            personal_id=user["personal_id"],
            nombre=body.nombre,
            ape_paterno=body.ape_paterno,
            ape_materno=body.ape_materno,
            telefono=body.telefono,
            correo=body.correo,
        )
        auditoria_service.registrar(
            accion="ACTUALIZAR_PERFIL",
            personal_id=user.get("personal_id"),
            usuario=user.get("usuario"),
            tipo_personal_id=user.get("tipo_personal_id"),
            rol=user.get("rol"),
            tabla_afectada="PERSONA",
            registro_id=user.get("personal_id"),
            descripcion="Actualización de datos personales propios",
            ip_cliente=get_client_ip(request),
        )
        nuevo_token = generar_token({
            "personal_id": user["personal_id"],
            "usuario": user["usuario"],
            "tipo_personal_id": user["tipo_personal_id"],
            "rol": user["rol"],
            "nombre": f"{body.nombre} {body.ape_paterno} {body.ape_materno}",
            "is_admin": user.get("is_admin", False),
        })
        response = JSONResponse(content=result)
        response.set_cookie(key="access_token", value=f"Bearer {nuevo_token}", httponly=True)
        return response
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudieron actualizar los datos.") from exc


@perfil.patch("/cambiar-contrasena")
async def cambiar_contrasena(
    request: Request,
    body: CambiarContrasena,
    user: dict = Depends(obtener_usuario_actual),
):
    try:
        result = perfil_service.cambiar_contrasena(
            personal_id=user["personal_id"],
            clave_actual=body.clave_actual,
            clave_nueva=body.clave_nueva,
        )
        auditoria_service.registrar(
            accion="CAMBIAR_CLAVE",
            personal_id=user.get("personal_id"),
            usuario=user.get("usuario"),
            tipo_personal_id=user.get("tipo_personal_id"),
            rol=user.get("rol"),
            tabla_afectada="PERSONAL",
            registro_id=user.get("personal_id"),
            descripcion="Cambio de contraseña propio",
            ip_cliente=get_client_ip(request),
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo cambiar la contraseña.") from exc


@perfil.get("/usuarios")
async def listar_usuarios(
    user: dict = Depends(require_admin_o_gerente),
):
    try:
        return {"usuarios": perfil_service.listar_usuarios()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudieron listar los usuarios.") from exc


@perfil.get("/usuarios/{personal_id}")
async def obtener_usuario(
    personal_id: str,
    user: dict = Depends(require_admin_o_gerente),
):
    try:
        usuario = perfil_service.obtener_usuario(personal_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="No se encontró el usuario.")
        return usuario
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo obtener el usuario.") from exc


@perfil.patch("/usuarios/{personal_id}/estado")
async def cambiar_estado_usuario(
    personal_id: str,
    body: CambiarEstadoUsuario,
    request: Request,
    user: dict = Depends(require_admin_o_gerente),
):
    try:
        result = perfil_service.cambiar_estado_usuario(
            personal_id, body.estado, solicitante_id=user.get("personal_id")
        )
        accion = "ACTIVAR_USUARIO" if body.estado == "A" else "DESACTIVAR_USUARIO"
        auditoria_service.registrar(
            accion=accion,
            personal_id=user.get("personal_id"),
            usuario=user.get("usuario"),
            tipo_personal_id=user.get("tipo_personal_id"),
            rol=user.get("rol"),
            tabla_afectada="PERSONAL",
            registro_id=personal_id,
            descripcion=f"{'Activación' if body.estado == 'A' else 'Desactivación'} de usuario ID {personal_id}",
            ip_cliente=get_client_ip(request),
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo cambiar el estado del usuario.") from exc


@perfil.patch("/usuarios/{personal_id}")
async def actualizar_usuario(
    personal_id: str,
    body: ActualizarUsuario,
    request: Request,
    user: dict = Depends(require_admin_o_gerente),
):
    try:
        result = perfil_service.actualizar_usuario(
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
            usuario_solicitante=user.get("usuario"),
        )
        auditoria_service.registrar(
            accion="ACTUALIZAR_USUARIO",
            personal_id=user.get("personal_id"),
            usuario=user.get("usuario"),
            tipo_personal_id=user.get("tipo_personal_id"),
            rol=user.get("rol"),
            tabla_afectada="PERSONAL",
            registro_id=personal_id,
            descripcion=f"Actualización de datos del usuario ID {personal_id} por {user.get('usuario')}",
            ip_cliente=get_client_ip(request),
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo actualizar el usuario.") from exc


@perfil.post("/usuarios/crear")
async def crear_usuario(
    body: CrearUsuario,
    request: Request,
    user: dict = Depends(require_admin_o_gerente),
):
    try:
        result = perfil_service.crear_usuario(
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
        auditoria_service.registrar(
            accion="CREAR_USUARIO",
            personal_id=user.get("personal_id"),
            usuario=user.get("usuario"),
            tipo_personal_id=user.get("tipo_personal_id"),
            rol=user.get("rol"),
            tabla_afectada="PERSONAL",
            registro_id=str(result.get("personal_id", "")),
            descripcion=f"Nuevo usuario creado: {body.nombre} {body.ape_paterno} por {user.get('usuario')}",
            ip_cliente=get_client_ip(request),
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="No se pudo crear el usuario.") from exc
