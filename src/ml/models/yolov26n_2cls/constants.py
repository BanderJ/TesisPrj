"""
Constantes del modelo YOLO26n_2cls — 2 clases (versión simplificada)
Clasificación binaria: defecto vs. verde
"""

# Filtro de tamaño de bounding box (píxeles, ya en coordenadas del frame completo).
# Con la cámara montada sobre la faja JGY370 (oct 2026) un grano grande mide
# ~455 px de lado en un frame 1920x1080. El techo deja ~40 % de margen para el
# estiramiento por desenfoque de movimiento y para la caja envolvente que arma
# _fusionar_cajas al unir recortes de tiles vecinos. Con 480 px un grano quieto
# pasaba el filtro y el mismo grano en movimiento se descartaba.
# Si se cambia la altura de la cámara, recalibrar con el rótulo gris "WxHpx".
GRANO_MIN_PX = 50
GRANO_MAX_PX = 640

# Detección por tiles. El modelo se entrenó con 1 grano por imagen ocupando
# ~40-77% de un frame de 640px. Sobre un frame de cámara de 1920x1080 con varios
# granos, cada grano queda demasiado chico al reescalar a 640 y el modelo no lo
# detecta (o lo detecta partido en el borde entre tiles). Partir el frame en una
# grilla y correr cada tile a imgsz=640 acerca cada grano a la escala de
# entrenamiento. 1x1 = frame completo (sin tiling).
#   - TILE_SOLAPE_PX debe ser >= (lado máximo de un grano) / 2 para que ningún
#     grano quede partido: cae entero en al menos un tile y _fusionar_cajas
#     descarta el recorte parcial del tile vecino.
#   - Subir TILES_X/TILES_Y agranda cada grano en la inferencia (mejor
#     separación de granos que se tocan) a costa de más inferencias por frame.
#     Con GPU los tiles se infieren en un solo batch, así que 3x3 es barato;
#     en CPU conviene 2x2 o 1x1.
TILES_X = 3
TILES_Y = 3
TILE_SOLAPE_PX = 320   # = GRANO_MAX_PX / 2

# Confianza mínima acumulada (máx. sobre el track) para aceptar que un objeto
# es un grano de café. Un track que nunca supera este umbral en toda su vida se
# marca "objeto desconocido" (azul) = materia extraña (piedra, pajilla, palito).
# ⚠️ Con EQUIVALENCIAS_DEFECTO["desconocido"] = 1.0, cada desconocido se desvía a
# DEFECTO por el servo Y suma 1.0 al total de defectos equivalentes. Subir este
# umbral marca más objetos como desconocidos: si captura granos reales de baja
# confianza (granos que se tocan, mala luz) infla el conteo con falsos defectos.
# Bajarlo deja pasar más ruido como grano. Calibrar con granos reales, no a ciegas.
UMBRAL_CONF_CONOCIDO = 0.35
# Frames mínimos observados antes de poder marcar un track como desconocido:
# evita rotular un grano recién aparecido que aún no acumuló una detección buena.
DESCONOCIDO_MIN_FRAMES = 3

# Sin GRUPOS_DISPLAY: con 2 clases (defecto/verde) no hay subtipos que agrupar.
# El frontend pinta las barras con total_defectos / total_sanos directamente.

CLASES = [
    "defecto", "verde"
]

# Clase sintética (no la emite el modelo, la deriva el tracker por baja confianza).
CLASE_DESCONOCIDO = "desconocido"

COLORES = {
    "defecto":     (0, 0, 255),      # Rojo para defectos
    "verde":       (0, 200, 0),      # Verde para granos sanos
    "desconocido": (255, 0, 0),      # Azul (BGR) para objeto no identificado
}

# Tabla de equivalencias SCA (350g) — adaptada para yolo26n_2cls (2 clases)
# ⚠️ VERIFICAR contra la tabla oficial de Line Coffee Marañón / INCAL antes de desplegar.
EQUIVALENCIAS_DEFECTO = {
    # Defecto genérico — promedio ponderado de todos los defectos SCA
    # Basado en: (agrio_severo=1.0 + cereza_seca=1.0 + broca_severo=1.0 + agrio_ligero=0.333) / 4 ≈ 0.83
    "defecto": 1,

    # Verde: no es defecto en SCA
    # Se cuenta pero NO añade defectos equivalentes
    "verde": 0.0,

    # Objeto no identificado por el modelo (baja confianza sostenida). INCAL y
    # otras entidades advierten materia extraña en el lote: piedras pequeñas,
    # pajilla, terrones, palitos. En SCA la materia extraña es defecto primario
    # (equivalencia 1.0 por unidad). Se desvía al canal DEFECTO por el servo y
    # suma al total igual que un grano defectuoso. Riesgo: un grano real de
    # confianza baja (p. ej. granos que se tocan) mal rotulado infla el defecto
    # — calibrar UMBRAL_CONF_CONOCIDO y vigilar total_desconocidos.
    "desconocido": 1.0,
}
