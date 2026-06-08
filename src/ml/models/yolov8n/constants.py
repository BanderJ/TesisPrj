"""
Constantes del modelo YOLOv8n — 17 clases
"""

# Filtro de tamaño de bounding box (píxeles) — calibrar según distancia real de la cámara
GRANO_MIN_PX = 8
GRANO_MAX_PX = 200

# Agrupaciones para mostrar en barras del frontend (backend computa, frontend solo pinta)
GRUPOS_DISPLAY = {
    "negro":   ["negro"],
    "brocado": ["broca_severo", "broca_ligero"],
    "partido": ["partido_maquina", "partido_mitad"],
}

CLASES = [
    "agrio_ligero", "agrio_severo", "averanado", "blanco",
    "broca_ligero", "broca_severo", "cascarilla_cereza_seca",
    "cascarilla_pergamino", "cereza_seca", "concha", "deforme",
    "inmaduro", "negro", "partido_maquina", "partido_mitad",
    "pergamino", "verde"
]

COLORES = {
    "agrio_ligero":           (0, 255, 255),
    "agrio_severo":           (0, 200, 255),
    "averanado":              (0, 165, 255),
    "blanco":                 (255, 255, 255),
    "broca_ligero":           (0, 255, 0),
    "broca_severo":           (0, 180, 0),
    "cascarilla_cereza_seca": (255, 0, 255),
    "cascarilla_pergamino":   (200, 0, 200),
    "cereza_seca":            (0, 0, 255),
    "concha":                 (255, 128, 0),
    "deforme":                (128, 0, 255),
    "inmaduro":               (0, 255, 128),
    "negro":                  (50, 50, 50),
    "partido_maquina":        (255, 0, 0),
    "partido_mitad":          (200, 0, 0),
    "pergamino":              (200, 200, 0),
    "verde":                  (0, 200, 0),
}

# Tabla de equivalencias SCA (350g)
EQUIVALENCIAS_DEFECTO = {
    "negro":                    1.0,
    "agrio_severo":             1.0,
    "cereza_seca":              1.0,
    "broca_severo":             1.0,

    "negro_parcial":            1/3,  # Legacy
    "agrio_ligero":             1/3,

    "pergamino":                1/5,
    "flotador":                 1/5,  # Legacy
    "inmaduro":                 1/5,
    "averanado":                1/5,
    "concha":                   1/5,
    "partido_maquina":          1/5,
    "partido_mitad":            1/5,
    "cascarilla_cereza_seca":   1/5,
    "cascarilla_pergamino":     1/5,

    "broca_ligero":             1/10,
}
