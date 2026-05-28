"""
Constantes del modelo YOLO26n_2cls — 2 clases (versión simplificada)
Clasificación binaria: defecto vs. verde
"""

CLASES = [
    "defecto", "verde"
]

COLORES = {
    "defecto": (0, 0, 255),      # Rojo para defectos
    "verde":   (0, 200, 0),      # Verde para granos sanos
}

# Tabla de equivalencias SCA (350g) — adaptada para yolo26n_2cls (2 clases)
EQUIVALENCIAS_DEFECTO = {
    # Defecto genérico — promedio ponderado de todos los defectos SCA
    # Basado en: (agrio_severo=1.0 + cereza_seca=1.0 + broca_severo=1.0 + agrio_ligero=0.333) / 4 ≈ 0.83
    "defecto": 0.83,

    # Verde: no es defecto en SCA (grano inmaduro detectado)
    # Se cuenta pero NO añade defectos equivalentes
    "verde": 0.0,
}
