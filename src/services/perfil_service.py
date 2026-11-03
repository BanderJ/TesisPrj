from datetime import datetime
import re
import unicodedata
from typing import Any

import psycopg2.errors
from pydantic import ValidationError

from src.database.bd import Connection
from src.models.persona import Persona
from src.models.personal import Personal
from src.schemas.perfil import NombreUsuarioGenerado
from src.utilities.documento_validador import validar_documento_por_tipo
from src.utilities.security import hash_password, verify_password, password_validate

# Usuario del gerente de la empresa — no puede ser desactivado
USUARIO_PROTEGIDO = "jbecerrac"


class PerfilService:
    """Servicio que centraliza la lógica de perfil de usuario."""

    def __init__(self) -> None:
        self.personal_model = Personal()
        self.persona_model = Persona()

    def obtener_datos_usuario(self, personal_id: str) -> dict[str, Any] | None:
        """Obtiene los datos del usuario actual para pre-llenar el formulario."""
        db = Connection()
        try:
            return self.persona_model.obtener_datos_perfil_completo(personal_id, db)
        finally:
            db.close()

    def actualizar_datos_personales(
        self,
        personal_id: str,
        nombre: str,
        ape_paterno: str,
        ape_materno: str,
        telefono: str | None,
        correo: str | None = None,
    ) -> dict[str, Any]:
        """Actualiza los datos personales del usuario."""
        actualizado = self.persona_model.actualizar_datos_personales(
            persona_id=personal_id,
            nombre=nombre,
            ape_paterno=ape_paterno,
            ape_materno=ape_materno,
            telefono=telefono,
            correo=correo,
        )

        if not actualizado:
            raise ValueError("No se pudieron actualizar los datos del usuario.")

        return {"mensaje": "Datos personales actualizados correctamente"}

    def cambiar_contrasena(
        self,
        personal_id: str,
        clave_actual: str,
        clave_nueva: str,
    ) -> dict[str, Any]:
        resultado = self.personal_model.obtener_clave_por_id(personal_id)
        if not resultado or not resultado.get("clave"):
            raise ValueError("No se encontró la contraseña del usuario.")

        if not verify_password(resultado["clave"], clave_actual):
            raise ValueError("La contraseña actual es incorrecta.")

        is_valid, validation_msg = password_validate(clave_nueva)
        if not is_valid:
            raise ValueError(validation_msg)

        if not self.personal_model.actualizar_clave(personal_id, hash_password(clave_nueva)):
            raise ValueError("No se pudo actualizar la contraseña.")

        return {"mensaje": "Contraseña actualizada correctamente"}

    def listar_usuarios(self) -> list[dict[str, Any]]:
        """Obtiene lista de todos los usuarios en el sistema."""
        usuarios = self.personal_model.obtener_todos_usuarios()
        return usuarios

    def obtener_usuario(self, personal_id: str) -> dict[str, Any] | None:
        """Obtiene los datos de un usuario específico."""
        return self.personal_model.obtener_usuario_por_id(personal_id)

    def cambiar_estado_usuario(
        self,
        personal_id: str,
        nuevo_estado: str,
        solicitante_id: str | None = None,
    ) -> dict[str, Any]:
        """Cambia el estado de un usuario (A=Activo, I=Inactivo)."""
        if nuevo_estado != "A":
            if solicitante_id is not None and str(personal_id) == str(solicitante_id):
                raise ValueError("No puedes desactivar tu propia cuenta.")
            objetivo = self.personal_model.obtener_usuario_por_id(personal_id)
            if objetivo and objetivo.get("usuario") == USUARIO_PROTEGIDO:
                raise ValueError(
                    f"El usuario {USUARIO_PROTEGIDO} corresponde a la gerente de la empresa y no se puede desactivar."
                )

        actualizado = self.personal_model.cambiar_estado(personal_id, nuevo_estado)

        if not actualizado:
            raise ValueError("No se pudo cambiar el estado del usuario.")

        return {"mensaje": f"Usuario marcado como {'activo' if nuevo_estado == 'A' else 'inactivo'}"}

    def _validar_clave_protegida(self, personal_id: str, usuario_solicitante: str | None) -> None:
        """La contraseña del usuario protegido solo puede cambiarla él mismo."""
        if usuario_solicitante == USUARIO_PROTEGIDO:
            return
        objetivo = self.personal_model.obtener_usuario_por_id(personal_id)
        if objetivo and objetivo.get("usuario") == USUARIO_PROTEGIDO:
            raise ValueError(
                f"El usuario {USUARIO_PROTEGIDO} corresponde a la gerente de la empresa; "
                "solo esa cuenta puede cambiar su propia contraseña."
            )

    @staticmethod
    def generar_nombre_usuario(nombre: str, ape_paterno: str, ape_materno: str) -> str:
        """Aplica la misma composición y limpieza que la vista previa de Cooperativa."""
        nombre, ape_paterno, ape_materno = (
            re.sub(r"[\u0300-\u036f]|\s", "", unicodedata.normalize("NFD", parte)).lower()
            for parte in (nombre, ape_paterno, ape_materno)
        )
        if not (nombre and ape_paterno and ape_materno):
            raise ValueError("Nombre y apellidos son obligatorios para generar el usuario.")
        usuario = nombre[0] + ape_paterno + ape_materno[0]
        try:
            return NombreUsuarioGenerado(usuario=usuario).usuario
        except ValidationError as exc:
            raise ValueError(
                "El nombre de usuario generado supera 30 caracteres; "
                "revise el nombre y los apellidos antes de crear la cuenta."
            ) from exc

    def actualizar_usuario(
        self,
        personal_id: str,
        nombre: str,
        ape_paterno: str,
        ape_materno: str,
        sexo: str,
        fecha_nacimiento: str,
        telefono: str | None,
        correo: str | None,
        ubigeo: str | None,
        tipo_personal_id: int,
        clave_nueva: str | None,
        usuario_solicitante: str | None = None,
    ) -> dict[str, Any]:
        if clave_nueva:
            self._validar_clave_protegida(personal_id, usuario_solicitante)

        db = Connection()
        try:
            fecha_nac = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
            self.persona_model.actualizar_completo(
                persona_id=personal_id,
                nombre=nombre,
                ape_paterno=ape_paterno,
                ape_materno=ape_materno,
                sexo=sexo,
                fecha_nacimiento=fecha_nac,
                telefono=telefono,
                correo=correo,
                ubigeo=ubigeo,
                db=db,
            )
            self.personal_model.actualizar_tipo_personal(personal_id, tipo_personal_id, db)
            if clave_nueva:
                is_valid, msg = password_validate(clave_nueva)
                if not is_valid:
                    raise ValueError(msg)
                self.personal_model.actualizar_clave(personal_id, hash_password(clave_nueva), db)
            db.commit()
            return {"mensaje": "Usuario actualizado correctamente"}
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def crear_usuario(
        self,
        nombre: str,
        ape_paterno: str,
        ape_materno: str,
        sexo: str,
        fecha_nacimiento: str,
        tipo_documento_id: int,
        num_documento: str,
        telefono: str | None,
        correo: str | None,
        ubigeo: str | None,
        tipo_personal_id: int,
        clave: str,
    ) -> dict[str, Any]:
        validar_documento_por_tipo(tipo_documento_id, num_documento)

        usuario = self.generar_nombre_usuario(nombre, ape_paterno, ape_materno)

        is_valid, validation_msg = password_validate(clave)
        if not is_valid:
            raise ValueError(validation_msg)

        clave_hash = hash_password(clave)

        db = Connection()
        try:
            fecha_nac = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
            persona_id = self.persona_model.registrar(
                nombre=nombre,
                ape_paterno=ape_paterno,
                ape_materno=ape_materno,
                sexo=sexo,
                fecha_nacimiento=fecha_nac,
                tipo_documento_id=tipo_documento_id,
                num_documento=num_documento,
                telefono=telefono,
                correo=correo,
                ubigeo=ubigeo,
                db=db,
            )

            personal_id = self.personal_model.crear_usuario(
                persona_id=persona_id,
                usuario=usuario,
                clave_hash=clave_hash,
                tipo_personal_id=tipo_personal_id,
                db=db,
            )
            db.commit()
            return {"mensaje": "Usuario creado correctamente", "personal_id": personal_id, "usuario": usuario}
        except psycopg2.errors.UniqueViolation as exc:
            db.rollback()
            raise ValueError(
                "Ya existe una persona registrada con ese número de documento, "
                "o el nombre de usuario generado ya está en uso."
            ) from exc
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
