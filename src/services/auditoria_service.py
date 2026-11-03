from datetime import date

from src.models.auditoria import Auditoria


class AuditoriaService:
    def __init__(self) -> None:
        self.model = Auditoria()

    def registrar(
        self,
        accion: str,
        personal_id: str | None = None,
        usuario: str | None = None,
        tipo_personal_id: int | None = None,
        rol: str | None = None,
        tabla_afectada: str | None = None,
        registro_id: str | None = None,
        descripcion: str | None = None,
        datos_anteriores: dict | None = None,
        datos_nuevos: dict | None = None,
        ip_cliente: str | None = None,
    ) -> None:
        try:
            self.model.registrar(
                accion=accion,
                personal_id=personal_id,
                usuario=usuario,
                tipo_personal_id=tipo_personal_id,
                rol=rol,
                tabla_afectada=tabla_afectada,
                registro_id=registro_id,
                descripcion=descripcion,
                datos_anteriores=datos_anteriores,
                datos_nuevos=datos_nuevos,
                ip_cliente=ip_cliente,
            )
        except Exception:
            pass  # la auditoría nunca debe interrumpir el flujo principal

    def obtener(
        self,
        personal_id: str | None = None,
        tipo_personal_id: int | None = None,
        accion: str | None = None,
        usuario: str | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        pagina: int = 1,
        limite: int = 50,
    ) -> tuple[list[dict], int]:
        return self.model.obtener_filtrado(
            personal_id=personal_id,
            tipo_personal_id=tipo_personal_id,
            accion=accion,
            usuario=usuario,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            pagina=pagina,
            limite=limite,
        )

    def obtener_usuarios_auditados(self) -> list[dict]:
        return self.model.obtener_usuarios_auditados()

    def obtener_acciones_disponibles(self) -> list[str]:
        return self.model.obtener_acciones_disponibles()


auditoria_service = AuditoriaService()
