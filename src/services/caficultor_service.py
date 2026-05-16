from typing import Any
import re
import unicodedata

from src.database.bd import Connection
from src.models.caficultor import Caficultor
from src.models.persona import Persona
from src.models.tipo_caficultor import TipoCaficultor
from src.models.tipo_documento import TipoDocumento
from src.schemas.caficultor import (
    CaficultorData,
    ConvertirSocioResponse,
    RegistrarCaficultorRequest,
    RegistrarCaficultorResponse,
)


class CaficultorService:
    """Servicio para casos de uso relacionados con caficultores."""

    TIPO_SOCIO_ID = 1

    def __init__(self) -> None:
        self.caficultor_model: Caficultor = Caficultor()
        self.persona_model: Persona = Persona()
        self.tipo_caficultor_model: TipoCaficultor = TipoCaficultor()
        self.tipo_documento_model: TipoDocumento = TipoDocumento()

    def _normalizar_nombre_tipo_documento(self, nombre: str) -> str:
        """Normaliza texto para comparar nombres de tipos de documento."""
        texto = unicodedata.normalize("NFD", nombre)
        texto = "".join(ch for ch in texto if unicodedata.category(ch) != "Mn")
        return texto.strip().lower()

    def _validar_documento_por_tipo(self, tipo_documento_id: int, num_documento: str) -> None:
        """Valida num_documento en función del tipo de documento registrado."""
        tipo_documento = self.tipo_documento_model.obtener_por_id(tipo_documento_id)
        if not tipo_documento:
            raise ValueError("El tipo de documento seleccionado no existe")

        nombre_tipo = self._normalizar_nombre_tipo_documento(str(tipo_documento.get("nombre", "")))

        if nombre_tipo == "dni":
            if not num_documento.isdigit() or len(num_documento) != 8:
                raise ValueError("Si el tipo de documento es DNI, debe tener exactamente 8 digitos numericos")
            return

        if nombre_tipo in {"pasaporte", "carnet de extranjeria"}:
            if not re.fullmatch(r"[A-Za-z0-9]{8,12}", num_documento):
                raise ValueError(
                    "Si el tipo de documento es Pasaporte o Carnet de Extranjeria, debe tener entre 8 y 12 caracteres alfanumericos"
                )
            return

        if not re.fullmatch(r"[A-Za-z0-9]{8,12}", num_documento):
            raise ValueError("El documento debe tener entre 8 y 12 caracteres alfanumericos")

    def obtener_caficultor_por_documento(self, num_documento: str) -> CaficultorData | None:
        """Retorna datos de caficultor por documento o None si no existe."""
        resultado: dict[str, Any] | None = self.caficultor_model.obtener_por_num_documento(num_documento)

        if not resultado:
            return None

        nombre_completo = " ".join(
            parte
            for parte in [
                resultado.get("nombre"),
                resultado.get("ape_paterno"),
                resultado.get("ape_materno"),
            ]
            if parte
        )

        return CaficultorData(
            persona_id=str(resultado["persona_id"]),
            num_documento=resultado["num_documento"],
            nombre_completo=nombre_completo,
            tipo_caficultor=resultado["tipo_caficultor"],
        )

    def _validar_tipo_caficultor(self, tipo_caficultor_id: int) -> None:
        """Valida existencia de tipo de caficultor."""
        if not self.tipo_caficultor_model.obtener_por_id(tipo_caficultor_id):
            raise ValueError("El tipo de caficultor seleccionado no existe")

    def _obtener_estado_caficultor(self, num_documento: str, db: Connection) -> dict[str, Any] | None:
        """Obtiene estado/tipo del caficultor por documento para conversion a socio."""
        return self.caficultor_model.obtener_estado_y_tipo_por_num_documento(num_documento, db=db)

    def _validar_caficultor_existe(self, registro: dict[str, Any] | None) -> dict[str, Any]:
        """Valida existencia de caficultor."""
        if not registro:
            raise ValueError("El caficultor no existe. Se recomienda realizar el registro primero")
        return registro

    def _validar_caficultor_activo(self, registro: dict[str, Any]) -> None:
        """Valida que la persona asociada al caficultor esté activa."""
        if str(registro.get("estado")) != "A":
            raise ValueError("El caficultor existe pero no se encuentra activo")

    def _validar_no_es_socio(self, registro: dict[str, Any]) -> None:
        """Valida que el caficultor no sea socio actualmente."""
        if int(registro.get("tipo_caficultor_id", 0)) == self.TIPO_SOCIO_ID:
            raise ValueError("El caficultor ya es socio")

    def registrar_caficultor(self, payload: RegistrarCaficultorRequest) -> RegistrarCaficultorResponse:
        """Registra persona y caficultor en una sola transaccion."""
        self._validar_documento_por_tipo(payload.tipo_documento_id, payload.num_documento)
        self._validar_tipo_caficultor(payload.tipo_caficultor_id)

        db = Connection()
        try:
            caficultor_existente = self.caficultor_model.obtener_por_num_documento(
                payload.num_documento,
                db=db,
            )
            if caficultor_existente:
                raise ValueError("Ya existe un caficultor registrado con ese numero de documento")

            persona_existente = self.persona_model.obtener_por_num_documento(
                payload.num_documento,
                db=db,
            )
            if persona_existente:
                persona_id = str(persona_existente["id"])
                if payload.ubigeo:
                    self.persona_model.actualizar_ubigeo(persona_id, payload.ubigeo, db=db)
            else:
                persona_id = self.persona_model.registrar(
                    nombre=payload.nombre,
                    ape_paterno=payload.ape_paterno,
                    ape_materno=payload.ape_materno,
                    sexo=payload.sexo,
                    fecha_nacimiento=payload.fecha_nacimiento,
                    tipo_documento_id=payload.tipo_documento_id,
                    num_documento=payload.num_documento,
                    telefono=payload.telefono,
                    ubigeo=payload.ubigeo,
                    db=db,
                )

            if self.caficultor_model.obtener_por_persona_id(persona_id, db=db):
                raise ValueError("La persona ya se encuentra registrada como caficultor")

            self.caficultor_model.registrar_caficultor(
                persona_id=persona_id,
                tipo_caficultor_id=payload.tipo_caficultor_id,
                db=db,
            )
            db.commit()

            return RegistrarCaficultorResponse(
                registrado=True,
                mensaje="Caficultor registrado correctamente.",
                persona_id=persona_id,
                caficultor_id=persona_id,
                tipo_caficultor_id=payload.tipo_caficultor_id,
            )
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def convertir_caficultor_a_socio(self, num_documento: str) -> ConvertirSocioResponse:
        """Convierte un caficultor existente y activo al tipo socio """
        db = Connection()
        try:
            registro = self._obtener_estado_caficultor(num_documento, db)
            registro = self._validar_caficultor_existe(registro)
            self._validar_caficultor_activo(registro)
            self._validar_no_es_socio(registro)

            actualizado = self.caficultor_model.actualizar_tipo_caficultor_por_num_documento(
                num_documento=num_documento,
                nuevo_tipo_caficultor_id=self.TIPO_SOCIO_ID,
                db=db,
            )

            if not actualizado:
                raise ValueError("No se pudo actualizar el tipo de caficultor")

            db.commit()
            return ConvertirSocioResponse(
                actualizado=True,
                mensaje="Caficultor convertido a socio correctamente.",
                num_documento=num_documento
            )
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()