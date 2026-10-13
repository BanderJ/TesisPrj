from datetime import date
from decimal import Decimal, ROUND_DOWN
from typing import Any

from src.database.bd import Connection
from src.models.caficultor import Caficultor
from src.models.evaluacion import Evaluacion
from src.models.evento_monitoreo import EventoMonitoreo
from src.models.tipo_grano import TipoGrano
from src.models.valor_cafe import ValorCafe
from src.services.bono_socio_service import BonoSocioService
from src.services.tipo_caficultor_service import TipoCaficultorService
from src.schemas.evaluacion import (
    CompletarEvaluacionRequest,
    CompletarEvaluacionResponse,
    EvaluacionData,
    FinalizarEvaluacionResponse,
    RegistrarEvaluacionRequest,
    RegistrarEvaluacionResponse,
    ResumenEvaluacionResponse,
)
from src.utilities.eventos_monitoreo import registro_eventos


class EvaluacionService:
    def __init__(self) -> None:
        self.evaluacion_model = Evaluacion()
        self.evento_model = EventoMonitoreo()
        self.caficultor_model = Caficultor()
        self.tipo_grano_model = TipoGrano()
        self.valor_cafe_model = ValorCafe()
        self.bono_socio_service = BonoSocioService()

    def registrar_evaluacion(
        self,
        personal_id: str,
        payload: RegistrarEvaluacionRequest,
    ) -> RegistrarEvaluacionResponse:
        db = Connection()
        try:
            caficultor = self.caficultor_model.obtener_estado_y_tipo_por_num_documento(
                payload.num_documento, db=db
            )
            if not caficultor:
                raise ValueError(
                    "No existe un caficultor registrado con ese numero de documento."
                )
            if str(caficultor.get("estado")) != "A":
                raise ValueError("El caficultor no se encuentra activo.")

            caficultor_id = str(caficultor["persona_id"])
            tipo_caficultor_id = int(caficultor["tipo_caficultor_id"])

            tipo_grano = self.tipo_grano_model.obtener_por_id(payload.tipo_grano_id, db=db)
            if not tipo_grano:
                raise ValueError("El tipo de grano seleccionado no existe.")

            # El pago se calcula con los precios del día: sin precios de hoy el
            # factor de rendimiento no tendría precio al finalizar el monitoreo.
            # Se bloquea aquí, antes de crear la evaluación.
            if not self.valor_cafe_model.obtener_resumen_rangos(date.today(), db):
                raise ValueError(
                    "No hay precios de café registrados hoy. Sin ellos no se puede registrar "
                    "la muestra ni iniciar el monitoreo. Comunique al administrador o gerente "
                    "que registre los precios del día para continuar."
                )

            nombre_completo = " ".join(
                p for p in [
                    caficultor.get("nombre"),
                    caficultor.get("ape_paterno"),
                    caficultor.get("ape_materno"),
                ] if p
            ) or payload.num_documento

            tipo_caficultor_nombre = str(caficultor.get("tipo_caficultor", ""))

            fila = self.evaluacion_model.registrar(
                personal_id=personal_id,
                caficultor_id=caficultor_id,
                tipo_caficultor_id=tipo_caficultor_id,
                num_sacos=payload.num_sacos,
                peso_bruto=payload.peso_bruto,
                humedad=payload.humedad,
                peso_muestra=payload.peso_muestra,
                peso_trillado=payload.peso_trillado,
                num_tamiz=payload.num_tamiz,
                peso_tamizado=payload.peso_tamizado,
                tipo_grano_id=payload.tipo_grano_id,
                db=db,
            )
            db.commit()

            return RegistrarEvaluacionResponse(
                registrado=True,
                mensaje="Evaluacion registrada correctamente.",
                data=EvaluacionData(
                    evaluacion_id=fila["id"],
                    codigo="",
                    num_documento=payload.num_documento,
                    caficultor_nombre=nombre_completo,
                    tipo_caficultor=tipo_caficultor_nombre,
                    num_sacos=payload.num_sacos,
                    peso_bruto=payload.peso_bruto,
                    humedad=payload.humedad,
                    peso_muestra=payload.peso_muestra,
                    peso_trillado=payload.peso_trillado,
                    num_tamiz=payload.num_tamiz,
                    peso_tamizado=payload.peso_tamizado,
                    tipo_grano_nombre=str(tipo_grano["nombre"]),
                ),
            )
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def _armar_resumen(self, fila: dict[str, Any]) -> ResumenEvaluacionResponse:
        fila["eventos"] = self.evento_model.listar_por_evaluacion(fila["evaluacion_id"])
        if fila.get("pago") is not None and fila.get("bono_socio") is not None:
            fila["pago_base"] = Decimal(str(fila["pago"])) - Decimal(str(fila["bono_socio"]))
        return ResumenEvaluacionResponse(**fila)

    def obtener_resumen_evaluacion(self, evaluacion_id: str) -> ResumenEvaluacionResponse:
        fila = self.evaluacion_model.obtener_resumen(evaluacion_id=evaluacion_id)
        if not fila:
            raise ValueError("No se encontró la evaluación.")
        return self._armar_resumen(fila)

    def completar_evaluacion(
        self,
        evaluacion_id: str,
        payload: CompletarEvaluacionRequest,
    ) -> CompletarEvaluacionResponse:
        db = Connection()
        try:
            eva = self.evaluacion_model.obtener_para_completar(evaluacion_id, db)
            if not eva:
                raise ValueError("No se encontró la evaluación.")
            # Una evaluación ya completada no se recalcula: su pago y su beneficio de
            # socio quedan fijos aunque cambien los precios o el monto del beneficio.
            if eva.get("factor_rendimiento") is not None:
                raise ValueError("La evaluación ya fue completada; su pago no se puede recalcular.")

            grano = self.tipo_grano_model.obtener_por_id(int(eva["tipo_grano_id"]), db)
            if not grano:
                raise ValueError("No se encontró el tipo de grano.")

            peso_muestra   = Decimal(str(eva["peso_muestra"]))
            peso_trillado  = Decimal(str(eva["peso_trillado"]))
            peso_bruto     = Decimal(str(eva["peso_bruto"]))
            num_sacos      = int(eva["num_sacos"])
            peso_qq_ref    = Decimal(str(grano["peso_qq"]))
            tara_saco      = Decimal("0.25")
            humedad        = Decimal(str(eva["humedad"]))

            divisor = peso_muestra / 100

            peso_bueno = Decimal(payload.peso_bueno).quantize(Decimal("0.01"))
            if peso_bueno > peso_trillado:
                raise ValueError(
                    f"El peso de grano bueno ({payload.peso_bueno} g) no puede superar el peso trillado ({peso_trillado} g)."
                )

            peso_cascara       = (peso_muestra - peso_trillado).quantize(Decimal("0.01"))
            peso_cascara_total = (peso_cascara / divisor).quantize(Decimal("0.01"))
            factor_rendimiento = (peso_bueno / divisor).quantize(Decimal("0.01"))
            peso_malo          = (peso_trillado - peso_bueno).quantize(Decimal("0.01"))

            # El precio se elige entre los de hoy, según el rango que contiene el
            # factor de rendimiento.
            valor_cafe = self.valor_cafe_model.obtener_por_factor(factor_rendimiento, date.today(), db)
            if not valor_cafe:
                raise ValueError(
                    f"No hay precio de café registrado hoy para el rango del factor de rendimiento "
                    f"({factor_rendimiento}). Registra ese rango en 'Valor de café'."
                )
            precio = Decimal(str(valor_cafe["precio"]))
            tara_total         = int(round(num_sacos * float(tara_saco)))
            peso_neto          = (peso_bruto - Decimal(tara_total)).quantize(Decimal("0.01"))

            if humedad > Decimal("12.00"):
                humedad_exceso    = humedad - Decimal("12.00")
                peso_neto_humedad = (peso_neto * humedad_exceso / (Decimal("100.00") - humedad)).quantize(Decimal("0.01"))
            else:
                peso_neto_humedad = Decimal("0.00")

            ### peso por quintal se redondea hacia abajo a 2 decimales para evitar pagar de más al caficultor
            peso_por_qq = ((peso_neto - peso_neto_humedad) / peso_qq_ref).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
            pago_base   = (peso_por_qq * precio).quantize(Decimal("0.01"))

            # Beneficio de socio: monto fijo por entrega, vigente al completar. Se usa
            # el tipo de caficultor que la evaluación registró al crearse y el monto
            # queda guardado en la fila, así un cambio posterior no altera el historial.
            es_socio   = int(eva["tipo_caficultor_id"]) == TipoCaficultorService.TIPO_SOCIO_ID
            bono_socio = self.bono_socio_service.monto_vigente(db) if es_socio else Decimal("0.00")
            pago       = pago_base + bono_socio

            fila = self.evaluacion_model.completar(
                evaluacion_id=evaluacion_id,
                codigo=str(eva["codigo"]),
                valor_cafe_id=str(valor_cafe["id"]),
                peso_cascara=peso_cascara,
                peso_cascara_total=peso_cascara_total,
                peso_bueno=peso_bueno,
                peso_malo=peso_malo,
                factor_rendimiento=factor_rendimiento,
                tara_saco=tara_saco,
                tara_total=tara_total,
                peso_neto=peso_neto,
                peso_por_qq=peso_por_qq,
                pago=pago,
                bono_socio=bono_socio,
                total_defectos=payload.total_defectos,
                db=db,
            )
            db.commit()

            return CompletarEvaluacionResponse(
                completado=True,
                mensaje="Evaluación completada correctamente.",
                evaluacion_id=evaluacion_id,
                codigo=str(fila["codigo"]).strip(),
                factor_rendimiento=Decimal(str(fila["factor_rendimiento"])),
                peso_por_qq=Decimal(str(fila["peso_por_qq"])),
                pago=Decimal(str(fila["pago"])),
                pago_base=pago_base,
                bono_socio=bono_socio,
                precio=precio,
                rango=str(valor_cafe["rango"]),
            )
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def buscar_evaluacion_por_codigo(self, codigo: str) -> ResumenEvaluacionResponse | None:
        fila = self.evaluacion_model.obtener_resumen(codigo=codigo)
        if not fila:
            return None
        return self._armar_resumen(fila)

    def verificar_estado(self, evaluacion_id: str) -> str | None:
        """Retorna 'activa' si aún no tiene codigo, 'finalizada' si ya fue completada, None si no existe."""
        fila = self.evaluacion_model.obtener_codigo(evaluacion_id)
        if fila is None:
            return None
        return "finalizada" if fila.get("codigo") else "activa"

    def obtener_kpis(self) -> dict[str, int | float | None]:
        fila = self.evaluacion_model.obtener_kpis()
        rendimiento = fila.get("rendimiento_promedio") if fila else None
        return {
            "total_lotes": int(fila["total_lotes"]) if fila else 0,
            "total_defectos": int(fila["total_defectos"]) if fila else 0,
            "rendimiento_promedio": float(rendimiento) if rendimiento is not None else None,
        }

    def finalizar_evaluacion(
        self,
        evaluacion_id: str,
        total_defectos: int | None = None,
        total_buenos: int | None = None,
        incidencias: list | None = None,
    ) -> FinalizarEvaluacionResponse:
        """Genera y asigna el codigo EVA y persiste la traza del monitoreo.

        Codigo y eventos se escriben en una sola transaccion: una evaluacion
        finalizada sin su traza, o una traza sin evaluacion cerrada, dejarian el
        historial incoherente.
        """
        db = Connection()
        try:
            fila = self.evaluacion_model.asignar_codigo(
                evaluacion_id, total_defectos, total_buenos, incidencias, db=db
            )
            # Solo la traza de ESTE lote: si el tracker ya arrancó otra evaluación
            # sus eventos no pertenecen a esta.
            if registro_eventos.evaluacion_id == evaluacion_id:
                self.evento_model.registrar_lote(
                    evaluacion_id, registro_eventos.todos(), db=db
                )
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

        return FinalizarEvaluacionResponse(
            finalizado=True,
            mensaje="Evaluacion finalizada correctamente.",
            evaluacion_id=fila["id"],
            codigo=fila["codigo"].strip(),
        )
