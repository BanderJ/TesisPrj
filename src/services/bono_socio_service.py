from decimal import Decimal

from src.database.bd import Connection
from src.models.bono_socio import BonoSocio
from src.schemas.bono_socio import BonoSocioActualizarRequest, BonoSocioRegistro, BonoSocioResponse


class BonoSocioService:
    def __init__(self) -> None:
        self.bono_model = BonoSocio()

    def obtener(self) -> BonoSocioResponse:
        historial = [BonoSocioRegistro(**fila) for fila in self.bono_model.listar()]
        return BonoSocioResponse(vigente=historial[0] if historial else None, historial=historial)

    def monto_vigente(self, db: Connection | None = None) -> Decimal:
        """Monto que se aplica hoy a cada entrega de un socio (0 si nunca se configuró)."""
        filas = self.bono_model.listar(limite=1, db=db)
        return Decimal(str(filas[0]["monto"])) if filas else Decimal("0.00")

    def actualizar(self, payload: BonoSocioActualizarRequest, personal_id: str) -> tuple[Decimal, BonoSocioResponse]:
        """Registra el nuevo monto y devuelve (monto anterior, estado actualizado)."""
        # Nunca se edita una fila: cada cambio es un registro nuevo, así las
        # evaluaciones pasadas conservan el monto que tenían (EVALUACION.bono_socio).
        db = Connection()
        try:
            anterior = self.monto_vigente(db)
            self.bono_model.registrar(payload.monto, personal_id, db)
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
        return anterior, self.obtener()
