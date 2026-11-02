"""
Reporte Service - Registro de reportes disponibles.

Para agregar un nuevo reporte:
1. Crear la consulta en src/models/reporte.py
2. Escribir un builder `_reporte_<nombre>()` que devuelva columnas/filas/grafico
3. Registrarlo en `self._reportes` con su código, título y descripción

La ruta y el frontend (coffee-report.js) no requieren cambios.
"""
from decimal import Decimal
from typing import Any, Callable

from src.models.reporte import Reporte
from src.schemas.reporte import FiltrosReporte


class ReporteService:
    def __init__(self) -> None:
        self.reporte_model = Reporte()
        self._reportes: dict[str, dict[str, Any]] = {
            "resumen_periodo": {
                "titulo": "Resumen por período",
                "descripcion": "Evaluaciones con rendimiento calculado. Kilos recibidos: peso bruto. Los pagos incluyen el beneficio de socio histórico.",
                "admite_filtros": True,
                "builder": self._reporte_evaluaciones,
            },
            "entregas_caficultor": {
                "titulo": "Entregas por caficultor",
                "descripcion": "Muestras con código EVA. Busque por nombre o documento y abra el detalle de cada entrega. El tipo Socio/Externo corresponde al registrado en la evaluación.",
                "admite_filtros": True,
                "builder": self._reporte_evaluaciones,
            },
            "usuarios": {
                "titulo": "Usuarios del sistema",
                "descripcion": "Distribución de usuarios activos por rol y caficultores registrados",
                "builder": self._reporte_usuarios,
            },
            "caficultores_tipo": {
                "titulo": "Caficultores por tipo",
                "descripcion": "Distribución de caficultores activos entre socios y no socios",
                "builder": self._reporte_caficultores_tipo,
            }
        }

    def listar_catalogo(self) -> list[dict[str, Any]]:
        """Lista los reportes disponibles (sin ejecutar sus consultas)."""
        return [
            {"codigo": codigo, "titulo": meta["titulo"], "descripcion": meta["descripcion"],
             "admite_filtros": meta.get("admite_filtros", False)}
            for codigo, meta in self._reportes.items()
        ]

    def generar(self, codigo: str, filtros: FiltrosReporte | None = None) -> dict[str, Any] | None:
        """Ejecuta el builder del reporte y devuelve la estructura genérica completa."""
        meta = self._reportes.get(codigo)
        if not meta:
            return None
        builder: Callable[..., dict[str, Any]] = meta["builder"]
        contenido = builder(codigo, filtros or FiltrosReporte()) if meta.get("admite_filtros") else builder()
        return {
            "codigo": codigo,
            "titulo": meta["titulo"],
            "descripcion": meta["descripcion"],
            "admite_filtros": meta.get("admite_filtros", False),
            **contenido,
        }

    def _reporte_evaluaciones(self, codigo: str, filtros: FiltrosReporte) -> dict[str, Any]:
        resumen = codigo == "resumen_periodo"
        resultado = self.reporte_model.evaluaciones(filtros, resumen=resumen)
        filas = resultado["filas"]
        if resumen:
            campos = [
                ("evaluaciones", "Evaluaciones completadas", ""),
                ("kilos_recibidos", "Kilos recibidos (bruto)", "kg"),
                ("pagos", "Pagos totales", "S/"),
                ("beneficios", "Beneficios de socio aplicados", "S/"),
            ]
            return {
                "columnas": [
                    {"campo": "fecha", "titulo": "Fecha"},
                    {"campo": "evaluaciones", "titulo": "Evaluaciones", "formato": "numero"},
                    {"campo": "kilos_recibidos", "titulo": "Peso bruto (kg)", "formato": "decimal"},
                    {"campo": "pagos", "titulo": "Pagos (S/)", "formato": "moneda"},
                    {"campo": "beneficios", "titulo": "Beneficios de socio (S/)", "formato": "moneda"},
                ],
                "filas": filas,
                "indicadores": [
                    {"titulo": titulo, "valor": sum((Decimal(str(f.get(campo) or 0)) for f in filas), Decimal(0)), "unidad": unidad}
                    for campo, titulo, unidad in campos
                ],
            }
        for fila in filas:
            fila["estado"] = "Completada" if fila["factor_rendimiento"] is not None else "Rendimiento pendiente"
        return {
            "columnas": [
                {"campo": "codigo", "titulo": "Código EVA"},
                {"campo": "fecha", "titulo": "Fecha"},
                {"campo": "caficultor", "titulo": "Caficultor"},
                {"campo": "documento", "titulo": "Documento"},
                {"campo": "tipo_caficultor", "titulo": "Tipo en la entrega"},
                {"campo": "peso_bruto", "titulo": "Peso bruto (kg)", "formato": "decimal"},
                {"campo": "peso_neto", "titulo": "Peso neto (kg)", "formato": "decimal"},
                {"campo": "factor_rendimiento", "titulo": "Factor de rendimiento", "formato": "decimal"},
                {"campo": "pago", "titulo": "Pago (S/)", "formato": "moneda"},
                {"campo": "bono_socio", "titulo": "Beneficio de socio (S/)", "formato": "moneda"},
                {"campo": "estado", "titulo": "Estado"},
            ],
            "filas": filas,
            "detalle_evaluacion": True,
            "total_filas": resultado["total"],
            "pagina": filtros.pagina,
            "por_pagina": filtros.por_pagina,
        }

    def _reporte_usuarios(self) -> dict[str, Any]:
        filas = self.reporte_model.conteo_personal_por_rol()
        filas.append({"categoria": "Caficultores", "cantidad": self.reporte_model.conteo_caficultores()})
        return {
            "columnas": [
                {"campo": "categoria", "titulo": "Tipo de usuario"},
                {"campo": "cantidad", "titulo": "Cantidad"},
            ],
            "filas": filas,
            "grafico": {"tipo": "pie", "campo_etiqueta": "categoria", "campo_valor": "cantidad"},
        }

    def _reporte_caficultores_tipo(self) -> dict[str, Any]:
        return {
            "columnas": [
                {"campo": "categoria", "titulo": "Tipo de caficultor"},
                {"campo": "cantidad", "titulo": "Cantidad"},
            ],
            "filas": self.reporte_model.conteo_caficultores_por_tipo(),
            "grafico": {"tipo": "bar", "campo_etiqueta": "categoria", "campo_valor": "cantidad"},
        }


reporte_service = ReporteService()
