"""
CoffeeRen - Módulo de Clasificación por Grado
Calcula el total de defectos y el grado del lote según la norma SCA.
Las equivalencias de defecto se cargan dinámicamente del modelo YOLO usado.
"""

# ============================================================
# TABLA DE GRADOS (Norma SCA — 3 grados solamente)
# Basado en: SCA Green Coffee Defect Guide / NTP 209.027
# ============================================================
TABLA_GRADOS = [
    {"grado": "Grado 1 (Specialty)",  "min": 0,   "max": 15},
    {"grado": "Grado 2",              "min": 16,  "max": 23},
    {"grado": "Grado 3",              "min": 24,  "max": float("inf")},
]


def calcular_defectos(conteo_granos: dict, equivalencias: dict) -> dict:
    """
    Calcula el total de defectos equivalentes a partir del conteo de granos.

    Args:
        conteo_granos: {clase: cantidad_granos} — output del tracker
        equivalencias: {clase: peso} — tabla de equivalencias SCA del modelo

    Returns:
        dict con:
            - detalle: {clase: {granos, defectos_equivalentes}}
            - total_defectos: float
            - grado: str
            - apto_specialty: bool
    """
    detalle = {}
    total_defectos = 0.0

    for clase, cantidad in conteo_granos.items():
        if cantidad == 0:
            continue

        peso = equivalencias.get(clase, None)
        if peso is None:
            continue

        defectos_equivalentes = round(cantidad * peso, 2)
        total_defectos += defectos_equivalentes

        detalle[clase] = {
            "granos":                cantidad,
            "peso_por_grano":        peso,
            "defectos_equivalentes": defectos_equivalentes
        }

    total_defectos = round(total_defectos, 2)
    grado = _determinar_grado(total_defectos)
    apto_specialty = total_defectos <= 15

    return {
        "detalle":         detalle,
        "total_defectos":  total_defectos,
        "grado":           grado,
        "apto_specialty":  apto_specialty
    }


def _determinar_grado(total_defectos: float) -> str:
    """Determina el grado del lote según el total de defectos."""
    for nivel in TABLA_GRADOS:
        if nivel["min"] <= total_defectos <= nivel["max"]:
            return nivel["grado"]
    return "Grado 3"


def generar_reporte(conteo_granos: dict, equivalencias: dict) -> dict:
    """
    Genera el reporte completo del lote para mostrar en la interfaz.

    Args:
        conteo_granos: {clase: cantidad_granos} — output del tracker
        equivalencias: {clase: peso} — tabla de equivalencias SCA del modelo

    Returns:
        dict con resultado completo del análisis del lote
    """
    resultado = calcular_defectos(conteo_granos, equivalencias)
    total_granos = sum(conteo_granos.values())

    reporte = {
        "total_granos_analizados": total_granos,
        "total_defectos":          resultado["total_defectos"],
        "grado":                   resultado["grado"],
        "apto_specialty":          resultado["apto_specialty"],
        "detalle_por_clase":       resultado["detalle"],
        "resumen": _generar_resumen(resultado, total_granos)
    }

    return reporte


def _generar_resumen(resultado: dict, total_granos: int) -> str:
    """Genera un resumen textual del análisis."""
    grado = resultado["grado"]
    defectos = resultado["total_defectos"]
    apto = "APTO" if resultado["apto_specialty"] else "NO APTO"

    return (
        f"Lote analizado: {total_granos} granos — "
        f"{defectos} defectos equivalentes — "
        f"{grado} — {apto} para Specialty"
    )
