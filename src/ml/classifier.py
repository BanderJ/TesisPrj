"""
CoffeeRen - Módulo de Clasificación por Grado
Calcula el total de defectos y el grado del lote según la norma
de clasificación de café verde (verificar con NTP 209.027 o tabla
interna de la Cooperativa Line Coffee Marañón).
"""

# ============================================================
# TABLA DE EQUIVALENCIAS DE DEFECTOS (Norma SCA)
# Fuente: SCA Green Coffee Defect Guide (Arabica Washed)
# Muestra: 350g — basado en tabla oficial
# VERIFICAR con tabla oficial de Line Coffee Marañón antes de deploy
# ============================================================
EQUIVALENCIAS_DEFECTO = {
    # Categoría 1 — Defectos Graves (1 grano = 1 defecto)
    "negro":                    1.0,
    "agrio_severo":             1.0,
    "cereza_seca":              1.0,
    "broca_severo":             1.0,
    # Materia extraña (piedras, palos, etc.) no se cuenta por granos
    # sino por objeto: 1 objeto = 1 defecto

    # Categoría 2 — Defectos Leves
    # 3 granos = 1 defecto
    "negro_parcial":            1/3,
    "agrio_ligero":             1/3,

    # 5 granos = 1 defecto
    "pergamino":                1/5,
    "flotador":                 1/5,
    "inmaduro":                 1/5,
    "averanado":                1/5,
    "concha":                   1/5,
    "partido_maquina":          1/5,
    "partido_mitad":            1/5,
    "cascarilla_cereza_seca":   1/5,
    "cascarilla_pergamino":     1/5,

    # 10 granos = 1 defecto
    "broca_ligero":             1/10,

    # Verde/Blanco/Deforme: no son defectos en SCA (son malformaciones)
    # Incluir solo si se detectan como defectos en el modelo
}

# ============================================================
# TABLA DE GRADOS (Norma SCA — 3 grados solamente)
# Basado en: SCA Green Coffee Defect Guide / NTP 209.027
# ============================================================
TABLA_GRADOS = [
    {"grado": "Grado 1 (Specialty)",  "min": 0,   "max": 15},
    {"grado": "Grado 2",              "min": 16,  "max": 23},
    {"grado": "Grado 3",              "min": 24,  "max": 30},
]


def calcular_defectos(conteo_granos: dict) -> dict:
    """
    Calcula el total de defectos equivalentes a partir del conteo de granos.

    Args:
        conteo_granos: {clase: cantidad_granos} — output del tracker

    Returns:
        dict con:
            - detalle: {clase: {granos, defectos_equivalentes}}
            - total_defectos: float
            - grado: str
            - apto_specialty: bool

    ⚠️ Limitación: La norma SCA requiere máx 1 defecto cat1 + máx 5 cat2 para Specialty.
    Esta implementación usa solo el total (<=15) porque el tracker no diferencia categorías.
    VERIFICAR equivalencias con Line Coffee Marañón antes de deploy.
    """
    detalle = {}
    total_defectos = 0.0

    for clase, cantidad in conteo_granos.items():
        if cantidad == 0:
            continue

        peso = EQUIVALENCIAS_DEFECTO.get(clase, None)
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
    return "Grado 3 — No clasificable"


def generar_reporte(conteo_granos: dict) -> dict:
    """
    Genera el reporte completo del lote para mostrar en la interfaz.

    Args:
        conteo_granos: {clase: cantidad_granos} — output del tracker

    Returns:
        dict con resultado completo del análisis del lote
    """
    resultado = calcular_defectos(conteo_granos)
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
