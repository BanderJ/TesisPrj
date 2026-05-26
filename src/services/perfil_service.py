from typing import Any

from src.models.persona import Persona
from src.models.personal import Personal
from src.database.bd import Connection
from src.utilities.security import hash_password, verify_password, password_validate


class PerfilService:
    """Servicio que centraliza la lógica de perfil de usuario."""

    def __init__(self) -> None:
        self.personal_model = Personal()
        self.persona_model = Persona()

    def obtener_datos_usuario(self, personal_id: str) -> dict[str, Any] | None:
        """Obtiene los datos del usuario actual para pre-llenar el formulario."""
        db = Connection()
        try:
            sql = """
                SELECT pe.nombre, pe.ape_paterno, pe.ape_materno, pe.telefono,
                       COALESCE(pe.correo, '') as correo,
                       pe.num_documento, pe.sexo, pe.fecha_nacimiento,
                       p.usuario, p.estado, p.fecha_registro, p.tipo_personal_id,
                       tp.nombre as rol
                FROM persona pe
                INNER JOIN personal p ON pe.id = p.personal_id
                INNER JOIN tipo_personal tp ON p.tipo_personal_id = tp.id
                WHERE pe.id = %s
            """
            return db.obtener_uno(sql, (personal_id,))
        except Exception:
            # If correo column doesn't exist, try without it
            sql = """
                SELECT pe.nombre, pe.ape_paterno, pe.ape_materno, pe.telefono,
                       '' as correo,
                       pe.num_documento, pe.sexo, pe.fecha_nacimiento,
                       p.usuario, p.estado, p.fecha_registro, p.tipo_personal_id,
                       tp.nombre as rol
                FROM persona pe
                INNER JOIN personal p ON pe.id = p.personal_id
                INNER JOIN tipo_personal tp ON p.tipo_personal_id = tp.id
                WHERE pe.id = %s
            """
            return db.obtener_uno(sql, (personal_id,))
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
            raise ValueError("No se pudo actualizar los datos del usuario")

        return {"mensaje": "Datos personales actualizados correctamente"}

    def cambiar_contrasena(
        self,
        personal_id: str,
        clave_actual: str,
        clave_nueva: str,
    ) -> dict[str, Any]:
        """Verifica la contraseña actual y actualiza a la nueva."""
        try:
            resultado = self.personal_model.obtener_clave_por_id(personal_id)
            if not resultado or not resultado.get("clave"):
                raise ValueError("No se encontró la contraseña del usuario")

            clave_hash_actual = resultado["clave"]

            if not verify_password(clave_hash_actual, clave_actual):
                raise ValueError("La contraseña actual es incorrecta")

            is_valid, validation_msg = password_validate(clave_nueva)
            if not is_valid:
                raise ValueError(validation_msg)

            nueva_clave_hash = hash_password(clave_nueva)
            actualizado = self.personal_model.actualizar_clave(personal_id, nueva_clave_hash)

            if not actualizado:
                raise ValueError("No se pudo actualizar la contraseña")

            return {"mensaje": "Contraseña actualizada correctamente"}
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Error al cambiar contraseña: {str(e)}")

    def listar_usuarios(self) -> list[dict[str, Any]]:
        """Obtiene lista de todos los usuarios en el sistema."""
        usuarios = self.personal_model.obtener_todos_usuarios()
        return usuarios

    def obtener_usuario(self, personal_id: str) -> dict[str, Any] | None:
        """Obtiene los datos de un usuario específico."""
        return self.personal_model.obtener_usuario_por_id(personal_id)

    def cambiar_estado_usuario(self, personal_id: str, nuevo_estado: str) -> dict[str, Any]:
        """Cambia el estado de un usuario (A=Activo, I=Inactivo)."""
        if nuevo_estado not in ["A", "I"]:
            raise ValueError("Estado inválido. Debe ser 'A' (Activo) o 'I' (Inactivo)")

        actualizado = self.personal_model.cambiar_estado(personal_id, nuevo_estado)

        if not actualizado:
            raise ValueError("No se pudo cambiar el estado del usuario")

        return {"mensaje": f"Usuario marcado como {'activo' if nuevo_estado == 'A' else 'inactivo'}"}

    def cambiar_contrasena_usuario(
        self,
        personal_id: str,
        clave_nueva: str,
    ) -> dict[str, Any]:
        """Cambia la contraseña de un usuario (sin verificar contraseña actual)."""
        is_valid, validation_msg = password_validate(clave_nueva)
        if not is_valid:
            raise ValueError(validation_msg)

        nueva_clave_hash = hash_password(clave_nueva)
        actualizado = self.personal_model.actualizar_clave(personal_id, nueva_clave_hash)

        if not actualizado:
            raise ValueError("No se pudo actualizar la contraseña")

        return {"mensaje": "Contraseña actualizada correctamente"}

    @staticmethod
    def generar_nombre_usuario(nombre: str, ape_paterno: str, ape_materno: str) -> str:
        """Genera nombre de usuario: primera letra nombre + apellido paterno + 2 caracteres apellido materno."""
        primer_letra = nombre[0].lower() if nombre else ""
        apellido_paterno = ape_paterno.lower() if ape_paterno else ""
        dos_caracteres = ape_materno[:2].lower() if ape_materno else ""
        return f"{primer_letra}{apellido_paterno}{dos_caracteres}"

    def obtener_personas_sin_usuario(self) -> list[dict[str, Any]]:
        """Obtiene lista de personas que no tienen usuario asignado."""
        personas = self.persona_model.obtener_personas_sin_usuario()
        return personas

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
        tipo_personal_id: int,
        clave: str,
    ) -> dict[str, Any]:
        """Crea un nuevo usuario: primero registra la persona, luego crea su acceso personal."""
        from datetime import datetime

        usuario = self.generar_nombre_usuario(nombre, ape_paterno, ape_materno)

        is_valid, validation_msg = password_validate(clave)
        if not is_valid:
            raise ValueError(validation_msg)

        clave_hash = hash_password(clave)

        try:
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
                    db=db,
                )

                if correo:
                    self.persona_model.actualizar_datos_personales(
                        persona_id=persona_id,
                        nombre=nombre,
                        ape_paterno=ape_paterno,
                        ape_materno=ape_materno,
                        telefono=telefono,
                        correo=correo,
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
                return {
                    "mensaje": "Usuario creado correctamente",
                    "personal_id": personal_id,
                    "usuario": usuario,
                }
            except Exception as e:
                db.rollback()
                raise
            finally:
                db.close()
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Error al crear usuario: {str(e)}")
