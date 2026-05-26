from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import os

from src.utilities.jwt_required import obtener_usuario_actual, jwt_token_requerido
from src.schemas.perfil import (
    ActualizarDatosPersonales,
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
    """Verifica que el usuario sea admin (3) o gerente (2)."""
    if user.get("tipo_personal_id") not in [2, 3]:
        raise HTTPException(status_code=403, detail="No tienes permisos para acceder a esta sección")


@perfil.get("/")
async def obtener_pagina_perfil(
    request: Request,
    user: dict = Depends(obtener_usuario_actual),
):
    """
    GET /perfil
    Retorna la página HTML del perfil con los datos del usuario.
    """
    try:
        datos = perfil_service.obtener_datos_usuario(user["personal_id"])

        return templates.TemplateResponse(
            request=request,
            name="perfil.html",
            context={
                "request": request,
                "user": user,
                "datos": datos,
            },
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@perfil.patch("/datos-personales")
async def actualizar_datos_personales(
    body: ActualizarDatosPersonales,
    user: dict = Depends(obtener_usuario_actual),
):
    """
    PATCH /perfil/datos-personales
    Actualiza los datos personales del usuario (nombre, apellidos, teléfono).
    """
    try:
        resultado = perfil_service.actualizar_datos_personales(
            personal_id=user["personal_id"],
            nombre=body.nombre,
            ape_paterno=body.ape_paterno,
            ape_materno=body.ape_materno,
            telefono=body.telefono,
            correo=body.correo,
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@perfil.patch("/cambiar-contrasena")
async def cambiar_contrasena(
    body: CambiarContrasena,
    user: dict = Depends(obtener_usuario_actual),
):
    """
    PATCH /perfil/cambiar-contrasena
    Cambia la contraseña del usuario después de verificar la contraseña actual.
    """
    try:
        resultado = perfil_service.cambiar_contrasena(
            personal_id=user["personal_id"],
            clave_actual=body.clave_actual,
            clave_nueva=body.clave_nueva,
        )
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@perfil.get("/usuarios/personas-disponibles")
async def obtener_personas_sin_usuario(
    user: dict = Depends(obtener_usuario_actual),
):
    """
    GET /perfil/usuarios/personas-disponibles
    Obtiene lista de personas sin usuario asignado (solo para admin/gerente).
    """
    try:
        verificar_admin_o_gerente(user)
        personas = perfil_service.obtener_personas_sin_usuario()
        return {"personas": personas}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@perfil.get("/usuarios")
async def listar_usuarios(
    user: dict = Depends(obtener_usuario_actual),
):
    """
    GET /perfil/usuarios
    Lista todos los usuarios del sistema (solo para admin/gerente).
    """
    try:
        verificar_admin_o_gerente(user)
        usuarios = perfil_service.listar_usuarios()
        return {"usuarios": usuarios}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@perfil.get("/usuarios/{personal_id}")
async def obtener_usuario(
    personal_id: str,
    user: dict = Depends(obtener_usuario_actual),
):
    """
    GET /perfil/usuarios/{personal_id}
    Obtiene los datos de un usuario específico (solo para admin/gerente).
    """
    try:
        verificar_admin_o_gerente(user)
        usuario = perfil_service.obtener_usuario(personal_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return usuario
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@perfil.patch("/usuarios/{personal_id}/estado")
async def cambiar_estado_usuario(
    personal_id: str,
    body: CambiarEstadoUsuario,
    user: dict = Depends(obtener_usuario_actual),
):
    """
    PATCH /perfil/usuarios/{personal_id}/estado
    Cambia el estado de un usuario a activo (A) o inactivo (I).
    """
    try:
        verificar_admin_o_gerente(user)
        resultado = perfil_service.cambiar_estado_usuario(personal_id, body.estado)
        return resultado
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@perfil.patch("/usuarios/{personal_id}/cambiar-contrasena")
async def cambiar_contrasena_usuario(
    personal_id: str,
    body: CambiarContraseñaUsuario,
    user: dict = Depends(obtener_usuario_actual),
):
    """
    PATCH /perfil/usuarios/{personal_id}/cambiar-contrasena
    Cambia la contraseña de un usuario (sin verificación de contraseña actual).
    """
    try:
        verificar_admin_o_gerente(user)
        resultado = perfil_service.cambiar_contrasena_usuario(
            personal_id=personal_id,
            clave_nueva=body.clave_nueva,
        )
        return resultado
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@perfil.post("/usuarios/crear")
async def crear_usuario(
    body: CrearUsuario,
    user: dict = Depends(obtener_usuario_actual),
):
    """
    POST /perfil/usuarios/crear
    Crea un nuevo usuario en el sistema (solo para admin/gerente).
    """
    try:
        verificar_admin_o_gerente(user)
        resultado = perfil_service.crear_usuario(
            nombre=body.nombre,
            ape_paterno=body.ape_paterno,
            ape_materno=body.ape_materno,
            sexo=body.sexo,
            fecha_nacimiento=body.fecha_nacimiento,
            tipo_documento_id=body.tipo_documento_id,
            num_documento=body.num_documento,
            telefono=body.telefono,
            correo=body.correo,
            tipo_personal_id=body.tipo_personal_id,
            clave=body.clave,
        )
        return resultado
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
