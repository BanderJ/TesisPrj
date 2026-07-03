from decimal import Decimal, ROUND_DOWN

from src.database.bd import Connection
from src.models.caficultor import Caficultor
from src.models.evaluacion import Evaluacion
from src.models.tipo_grano import TipoGrano
from src.models.valor_cafe import ValorCafe
from src.schemas.evaluacion import (
    CompletarEvaluacionRequest,
    CompletarEvaluacionResponse,
    EvaluacionData,
    FinalizarEvaluacionResponse,
    RegistrarEvaluacionRequest,
    RegistrarEvaluacionResponse,
    ResumenEvaluacionResponse,
)


class EvaluacionService:
    def __init__(self) -> None:
        self.evaluacion_model = Evaluacion()
        self.caficultor_model = Caficultor()
        self.tipo_grano_model = TipoGrano()
        self.valor_cafe_model = ValorCafe()

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

    def obtener_resumen_evaluacion(self, evaluacion_id: str) -> ResumenEvaluacionResponse:
        fila = self.evaluacion_model.obtener_resumen(evaluacion_id=evaluacion_id)
        if not fila:
            raise ValueError("Evaluacion no encontrada.")
        return ResumenEvaluacionResponse(**fila)

    def completar_evaluacion(
        self,
        evaluacion_id: str,
        payload: CompletarEvaluacionRequest,
    ) -> CompletarEvaluacionResponse:
        db = Connection()
        try:
            eva = self.evaluacion_model.obtener_para_completar(evaluacion_id, db)
            if not eva:
                raise ValueError("Evaluación no encontrada.")

            grano = self.tipo_grano_model.obtener_por_id(int(eva["tipo_grano_id"]), db)
            if not grano:
                raise ValueError("Tipo de grano no encontrado.")

            valor_cafe = self.valor_cafe_model.obtener_mas_reciente(db)
            if not valor_cafe:
                raise ValueError("No hay precios de café registrados.")

            peso_muestra   = Decimal(str(eva["peso_muestra"]))
            peso_trillado  = Decimal(str(eva["peso_trillado"]))
            peso_bruto     = Decimal(str(eva["peso_bruto"]))
            num_sacos      = int(eva["num_sacos"])
            peso_qq_ref    = Decimal(str(grano["peso_qq"]))
            precio         = Decimal(str(valor_cafe["precio"]))
            tara_saco      = Decimal("0.25")
            humedad        = Decimal(str(eva["humedad"]))

            divisor = peso_muestra / 100

            peso_cascara       = (peso_muestra - peso_trillado).quantize(Decimal("0.01"))
            peso_cascara_total = (peso_cascara / divisor).quantize(Decimal("0.01"))
            peso_bueno         = payload.peso_bueno.quantize(Decimal("0.01"))
            factor_rendimiento = (peso_bueno / divisor).quantize(Decimal("0.01"))
            peso_malo          = (peso_trillado - peso_bueno).quantize(Decimal("0.01"))
            tara_total         = int(round(num_sacos * float(tara_saco)))
            peso_neto          = (peso_bruto - Decimal(tara_total)).quantize(Decimal("0.01"))

            if humedad > Decimal("12.00"):
                humedad_exceso    = humedad - Decimal("12.00")
                peso_neto_humedad = (peso_neto * humedad_exceso / (Decimal("100.00") - humedad)).quantize(Decimal("0.01"))
            else:
                peso_neto_humedad = Decimal("0.00")

            ### peso por quintal se redondea hacia abajo a 2 decimales para evitar pagar de más al caficultor
            peso_por_qq = ((peso_neto - peso_neto_humedad) / peso_qq_ref).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
            pago        = (peso_por_qq * precio).quantize(Decimal("0.01"))

            categoria = self.evaluacion_model.obtener_categoria_por_defectos(
                payload.total_defectos, db
            )
            categoria_id = int(categoria["id"]) if categoria else None

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
                categoria_id=categoria_id,
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
                categoria=str(categoria["nombre"]) if categoria else None,
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
        return ResumenEvaluacionResponse(**fila)

    def verificar_estado(self, evaluacion_id: str) -> str | None:
        """Retorna 'activa' si aún no tiene codigo, 'finalizada' si ya fue completada, None si no existe."""
        fila = self.evaluacion_model.obtener_codigo(evaluacion_id)
        if fila is None:
            return None
        return "finalizada" if fila.get("codigo") else "activa"

    def obtener_kpis(self) -> dict[str, int]:
        fila = self.evaluacion_model.obtener_kpis()
        return {
            "total_lotes": int(fila["total_lotes"]) if fila else 0,
            "total_defectos": int(fila["total_defectos"]) if fila else 0,
        }

    def finalizar_evaluacion(
        self,
        evaluacion_id: str,
        total_defectos: int | None = None,
        total_buenos: int | None = None,
    ) -> FinalizarEvaluacionResponse:
        """Genera y asigna el codigo EVA a la evaluacion al finalizar el monitoreo."""
        fila = self.evaluacion_model.asignar_codigo(evaluacion_id, total_defectos, total_buenos)
        return FinalizarEvaluacionResponse(
            finalizado=True,
            mensaje="Evaluacion finalizada correctamente.",
            evaluacion_id=fila["id"],
            codigo=fila["codigo"].strip(),
        )
