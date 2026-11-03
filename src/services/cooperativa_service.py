import io
import os

from PIL import Image

from src.config import Config
from src.database.bd import Connection
from src.models.cooperativa import Cooperativa
from src.schemas.cooperativa import CooperativaUpdate
from src.utilities.uuid_utils import uuid7

MAX_TAMANO_IMAGEN_BYTES = 5 * 1024 * 1024
_DIR_IMAGENES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "cooperativa")
_URL_IMAGENES = "/resources/cooperativa/"
# Formato que detecta Pillow leyendo el archivo -> extensión con que se guarda.
_FORMATOS_IMAGEN = {"JPEG": "jpg", "PNG": "png", "WEBP": "webp", "GIF": "gif"}


class CooperativaService:
    def __init__(self) -> None:
        self.model = Cooperativa()

    def obtener_por_id(self, cooperativa_id: str) -> dict | None:
        return self.model.obtener_por_id(cooperativa_id)

    def actualizar(self, cooperativa_id: str, data: CooperativaUpdate) -> dict | None:
        db = Connection()
        try:
            actual = self.model.obtener_por_id(cooperativa_id, db)
            if not actual:
                return None
            if data.codigo and data.codigo != actual.get("codigo"):
                if self.model.obtener_por_codigo(data.codigo, db):
                    raise ValueError(f"El código '{data.codigo}' ya está en uso.")
            result = self.model.actualizar(
                cooperativa_id=cooperativa_id,
                nombre=data.nombre,
                codigo=data.codigo,
                ubicacion=data.ubicacion,
                telefono=data.telefono,
                correo=data.correo,
                descripcion=data.descripcion,
                imagen_url=data.imagen_url,
                db=db,
            )
            db.commit()
            if data.imagen_url and data.imagen_url != actual.get("imagen_url"):
                self._borrar_imagen(actual.get("imagen_url"))
            return result
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def obtener_por_usuario(self, personal_id: str) -> dict | None:
        db = Connection()
        try:
            cooperativa = self.model.obtener_cooperativa_de_usuario(personal_id, db)
            if cooperativa:
                return cooperativa

            default_id = self.model.obtener_id_por_codigo(Config.COOPERATIVA_DEFAULT_CODIGO, db)
            if not default_id:
                return None

            self.model.asignar_cooperativa_a_persona(personal_id, default_id, db)
            db.commit()
            return self.model.obtener_por_id(default_id, db)
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def guardar_imagen(self, contenido: bytes) -> str:
        """Guarda el logo subido y devuelve su URL. El formato se decide leyendo el
        archivo con Pillow, no por la extensión ni el content-type que envía el
        cliente; el nombre en disco es un uuid7 con la extensión del formato real."""
        if len(contenido) > MAX_TAMANO_IMAGEN_BYTES:
            raise ValueError("La imagen no puede superar 5 MB.")
        try:
            with Image.open(io.BytesIO(contenido)) as imagen:
                formato = imagen.format
                imagen.verify()
        except Exception as exc:
            raise ValueError("El archivo no es una imagen válida.") from exc
        ext = _FORMATOS_IMAGEN.get(formato or "")
        if not ext:
            raise ValueError("Formato de imagen no permitido. Use JPG, PNG, WEBP o GIF.")
        os.makedirs(_DIR_IMAGENES, exist_ok=True)
        nombre = f"{uuid7()}.{ext}"
        with open(os.path.join(_DIR_IMAGENES, nombre), "wb") as f:
            f.write(contenido)
        return f"{_URL_IMAGENES}{nombre}"

    @staticmethod
    def _borrar_imagen(url: str | None) -> None:
        """Borra el logo reemplazado. Solo archivos de la carpeta de logos: se usa
        el nombre base, nunca una ruta que venga de la base de datos."""
        if not url or not url.startswith(_URL_IMAGENES):
            return
        ruta = os.path.join(_DIR_IMAGENES, os.path.basename(url))
        try:
            if os.path.isfile(ruta):
                os.remove(ruta)
        except OSError as exc:
            print(f"[cooperativa] No se pudo borrar la imagen anterior {ruta}: {exc}")


cooperativa_service = CooperativaService()
