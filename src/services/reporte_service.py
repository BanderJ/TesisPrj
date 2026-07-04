"""
Reporte Service - Registro de reportes disponibles.

Para agregar un nuevo reporte:
1. Crear la consulta en src/models/reporte.py
2. Escribir un builder `_reporte_<nombre>()` que devuelva columnas/filas/grafico
3. Registrarlo en `self._reportes` con su código, título y descripción

La ruta y el frontend (coffee-report.js) no requieren cambios.
"""
from typing import Any, Callable

from src.models.reporte import Reporte


class ReporteService:
    def __init__(self) -> None:
        self.reporte_model = Reporte()
        self._reportes: dict[str, dict[str, Any]] = {
            "usuarios": {
                "titulo": "Usuarios del sistema",
                "descripcion": "Distribución de usuarios activos por rol y caficultores registrados",
                "builder": self._reporte_usuarios,
            },
        }

    def listar_catalogo(self) -> list[dict[str, str]]:
        """Lista los reportes disponibles (sin ejecutar sus consultas)."""
        return [
            {"codigo": codigo, "titulo": meta["titulo"], "descripcion": meta["descripcion"]}
            for codigo, meta in self._reportes.items()
        ]

    def generar(self, codigo: str) -> dict[str, Any] | None:
        """Ejecuta el builder del reporte y devuelve la estructura genérica completa."""
        meta = self._reportes.get(codigo)
        if not meta:
            return None
        builder: Callable[[], dict[str, Any]] = meta["builder"]
        return {
            "codigo": codigo,
            "titulo": meta["titulo"],
            "descripcion": meta["descripcion"],
            **builder(),
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


reporte_service = ReporteService()
