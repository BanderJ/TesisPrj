"""
Constantes del modelo YOLO26n_2cls — 2 clases (versión simplificada)
Clasificación binaria: defecto vs. verde
"""

# Filtro de tamaño de bounding box (píxeles) — calibrar según distancia real de la cámara
GRANO_MIN_PX = 8
GRANO_MAX_PX = 500

# Agrupaciones para mostrar en barras del frontend
# Con 2 clases todos los defectos van a "negro" (barra principal)
GRUPOS_DISPLAY = {
    "negro":   ["defecto"],
    "brocado": [],
    "partido": [],
}

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

    # Verde: no es defecto en SCA
    # Se cuenta pero NO añade defectos equivalentes
    "verde": 0.0,
}
