"""
Constantes del modelo YOLO26n — 14 clases
Clases fusionadas respecto a yolov8n:
  - agrio_ligero + agrio_severo → agrio
  - partido_maquina + partido_mitad → partido
  - concha + deforme → defecto_forma
"""

# Filtro de tamaño de bounding box (píxeles) — calibrar según distancia real de la cámara
GRANO_MIN_PX = 8
GRANO_MAX_PX = 200

# Agrupaciones para mostrar en barras del frontend
GRUPOS_DISPLAY = {
    "negro":   ["negro"],
    "brocado": ["broca_severo", "broca_ligero"],
    "partido": ["partido"],
}

CLASES = [
    "agrio", "averanado", "blanco", "broca_ligero", "broca_severo",
    "cascarilla_cereza_seca", "cascarilla_pergamino", "cereza_seca",
    "defecto_forma", "inmaduro", "negro", "partido", "pergamino", "verde"
]

COLORES = {
    "agrio":                  (0, 220, 255),
    "averanado":              (0, 165, 255),
    "blanco":                 (255, 255, 255),
    "broca_ligero":           (0, 255, 0),
    "broca_severo":           (0, 180, 0),
    "cascarilla_cereza_seca": (255, 0, 255),
    "cascarilla_pergamino":   (200, 0, 200),
    "cereza_seca":            (0, 0, 255),
    "defecto_forma":          (128, 0, 128),
    "inmaduro":               (0, 255, 128),
    "negro":                  (50, 50, 50),
    "partido":                (200, 0, 0),
    "pergamino":              (200, 200, 0),
    "verde":                  (0, 200, 0),
}

# Tabla de equivalencias SCA (350g) — adaptada para yolo26n
EQUIVALENCIAS_DEFECTO = {
    "negro":                    1.0,
    "agrio":                    1/3,
    "cereza_seca":              1.0,
    "broca_severo":             1.0,

    "pergamino":                1/5,
    "inmaduro":                 1/5,
    "averanado":                1/5,
    "defecto_forma":            1/5,
    "partido":                  1/5,
    "cascarilla_cereza_seca":   1/5,
    "cascarilla_pergamino":     1/5,
    "broca_ligero":             1/10,
}
