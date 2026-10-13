"""
CoffeeRen - Conteo de defectos del lote
Calcula el total de defectos equivalentes del lote a partir del conteo del tracker.
Las equivalencias de defecto se cargan dinámicamente del modelo YOLO usado.

No asigna grado SCA ni aptitud Specialty: el grado depende del TIPO de defecto
(primario/secundario) y el modelo actual solo distingue defecto/verde.
"""


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

    return {
        "detalle":         detalle,
        "total_defectos":  round(total_defectos, 2),
    }


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
        "detalle_por_clase":       resultado["detalle"],
        "resumen": _generar_resumen(resultado, total_granos)
    }

    return reporte


def _generar_resumen(resultado: dict, total_granos: int) -> str:
    """Genera un resumen textual del análisis."""
    return (
        f"Lote analizado: {total_granos} granos — "
        f"{resultado['total_defectos']} defectos equivalentes"
    )
