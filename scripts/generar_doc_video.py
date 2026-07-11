"""Genera el documento Word: Flujo de Captura de Video y Comunicacion Arduino."""
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

# Margenes
section = doc.sections[0]
section.top_margin    = Cm(2.5)
section.bottom_margin = Cm(2.5)
section.left_margin   = Cm(3.0)
section.right_margin  = Cm(2.5)

# Paleta
CAFE_OSCURO = RGBColor(0x3B, 0x1F, 0x0A)
CAFE_MEDIO  = RGBColor(0x6B, 0x3A, 0x1F)
VERDE_TEAL  = RGBColor(0x00, 0x7A, 0x6E)
GRIS_SUAVE  = RGBColor(0x55, 0x55, 0x55)
NEGRO       = RGBColor(0x1A, 0x1A, 0x1A)

# ── Helpers ────────────────────────────────────────────────────────────────────

def add_heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    run = p.runs[0] if p.runs else p.add_run(text)
    if level == 1:
        run.font.size = Pt(18); run.font.color.rgb = CAFE_OSCURO; run.font.bold = True
    elif level == 2:
        run.font.size = Pt(14); run.font.color.rgb = CAFE_MEDIO; run.font.bold = True
    elif level == 3:
        run.font.size = Pt(12); run.font.color.rgb = VERDE_TEAL; run.font.bold = True
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after  = Pt(4)
    return p

def add_para(doc, text, bold=False, italic=False, color=None, size=11):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color if color else NEGRO
    p.paragraph_format.space_after = Pt(6)
    return p

def add_code(doc, text):
    p = doc.add_paragraph()
    p.style = doc.styles['No Spacing']
    run = p.add_run(text)
    run.font.name = 'Courier New'
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)
    p.paragraph_format.left_indent  = Cm(1)
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(2)
    pPr  = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    left = OxmlElement('w:left')
    left.set(qn('w:val'), 'single')
    left.set(qn('w:sz'), '6')
    left.set(qn('w:space'), '12')
    left.set(qn('w:color'), '007A6E')
    pBdr.append(left)
    pPr.append(pBdr)
    return p

def add_bullet(doc, text, level=0):
    p = doc.add_paragraph(style='List Bullet')
    run = p.add_run(text)
    run.font.size = Pt(11)
    run.font.color.rgb = NEGRO
    p.paragraph_format.left_indent = Cm(0.5 + level * 0.5)
    p.paragraph_format.space_after = Pt(3)
    return p

def add_divider(doc):
    p = doc.add_paragraph()
    run = p.add_run(chr(0x2500) * 70)
    run.font.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)
    run.font.size = Pt(8)
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(2)
    return p

def add_label(doc, label, value):
    p = doc.add_paragraph()
    r1 = p.add_run(f"{label}: ")
    r1.font.bold = True; r1.font.size = Pt(11); r1.font.color.rgb = CAFE_MEDIO
    r2 = p.add_run(value)
    r2.font.size = Pt(11); r2.font.color.rgb = NEGRO
    p.paragraph_format.space_after = Pt(3)
    return p

def add_file_ref(doc, path, description=""):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.space_after = Pt(3)
    r1 = p.add_run(">> ")
    r1.font.size = Pt(11); r1.font.color.rgb = VERDE_TEAL
    r2 = p.add_run(path)
    r2.font.name = 'Courier New'; r2.font.size = Pt(10); r2.font.bold = True
    r2.font.color.rgb = VERDE_TEAL
    if description:
        r3 = p.add_run(f"  --  {description}")
        r3.font.size = Pt(10); r3.font.color.rgb = GRIS_SUAVE
    return p

# ══════════════════════════════════════════════════════════════════════════════
# PORTADA
# ══════════════════════════════════════════════════════════════════════════════
titulo = doc.add_paragraph()
titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
titulo.paragraph_format.space_before = Pt(40)
titulo.paragraph_format.space_after  = Pt(6)
r = titulo.add_run("CoffeeRen")
r.font.size = Pt(32); r.font.bold = True; r.font.color.rgb = CAFE_OSCURO

subtitulo = doc.add_paragraph()
subtitulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
subtitulo.paragraph_format.space_after = Pt(4)
r2 = subtitulo.add_run("Sistema de Clasificacion de Granos de Cafe")
r2.font.size = Pt(16); r2.font.color.rgb = CAFE_MEDIO

doc_titulo = doc.add_paragraph()
doc_titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
doc_titulo.paragraph_format.space_after = Pt(40)
r3 = doc_titulo.add_run("Flujo de Captura de Video y Comunicacion Arduino")
r3.font.size = Pt(13); r3.font.bold = True; r3.font.color.rgb = VERDE_TEAL

meta = doc.add_paragraph()
meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
r4 = meta.add_run("Documentacion Tecnica Interna  -  Junio 2026")
r4.font.size = Pt(10); r4.font.color.rgb = GRIS_SUAVE

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 1. VISION GENERAL
# ══════════════════════════════════════════════════════════════════════════════
add_heading(doc, "1. Vision General del Subsistema", 1)
add_para(doc, (
    "Este documento describe como CoffeeRen captura video de la camara ELP, "
    "lo procesa con YOLO + ByteTrack en tiempo real, transmite el resultado al "
    "navegador del operador, y comunica al Arduino para controlar fisicamente el "
    "servo que separa granos buenos de defectuosos."
))
add_para(doc, (
    "El sistema corre con 4 hilos en paralelo ademas del hilo principal de FastAPI. "
    "Ninguna ruta HTTP espera a la camara ni al servo: todo corre en segundo plano y "
    "las rutas solo leen estado cacheado, por eso el servidor responde rapido."
), italic=True, color=GRIS_SUAVE)
add_divider(doc)

add_heading(doc, "Archivos involucrados", 2)
add_file_ref(doc, "src/services/camara_service.py",    "Hilo de captura de camara")
add_file_ref(doc, "src/ml/tracker.py",                 "YOLO + ByteTrack + anotacion de frames")
add_file_ref(doc, "src/services/tracker_service.py",   "Coordina camara + tracker + streaming")
add_file_ref(doc, "src/utilities/servo_controller.py", "Cola de separacion con delay temporal")
add_file_ref(doc, "src/utilities/arduino_serial.py",   "Comunicacion serial con Arduino")
add_file_ref(doc, "src/routes/video.py",               "Endpoints HTTP del streaming y control")
add_file_ref(doc, "src/routes/arduino.py",             "Endpoints HTTP del Arduino")
add_file_ref(doc, "src/templates/monitoreo.html",      "Frontend: polling de frames y conteos")
doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 2. LOS 4 HILOS
# ══════════════════════════════════════════════════════════════════════════════
add_heading(doc, "2. Los 4 Hilos del Sistema", 1)
add_para(doc, (
    "Cuando el operador inicia el monitoreo, se levantan cuatro hilos de Python "
    "que corren de forma independiente y se comunican mediante variables compartidas "
    "protegidas por locks (threading.Lock / threading.Event)."
))

hilos = [
    ("camara-capture",
     "CamaraService._capture_loop()",
     "Lee frames crudos de la camara (cap.read) y guarda el ultimo JPEG comprimido. "
     "No procesa nada: solo captura al maximo FPS posible del sensor."),
    ("tracker-processing",
     "TrackerService._loop_procesamiento()",
     "Consume frames de camara-capture, los pasa a YOLO+ByteTrack, y guarda "
     "el resultado anotado listo para streaming."),
    ("servo-controller",
     "ServoController._worker()",
     "Monitorea una cola de granos pendientes de clasificacion. Cuando vence "
     "el delay de cada grano, envia el comando SERVO:BUENO o SERVO:DEFECTO al Arduino."),
    ("arduino-reader",
     "ArduinoSerial._reader_loop()",
     "Lee continuamente del puerto serial (9600 baud). Actualiza un estado cacheado "
     "con distancia, peso y estado del sensor de tapa."),
]
for nombre, funcion, desc in hilos:
    add_heading(doc, f"Hilo: {nombre}", 3)
    add_label(doc, "Funcion", funcion)
    add_para(doc, desc)
    doc.add_paragraph()

add_divider(doc)
add_heading(doc, "Diagrama de flujo entre hilos", 2)
lineas = [
    "HTML (polling 33 ms)",
    "  |  GET /video/frame",
    "  v",
    "video.py --------- tracker_service._frame_anotado  (bytes JPEG)",
    "                            ^",
    "                            |  hilo 'tracker-processing'",
    "                            |  esperar_frame() -> procesar_frame()",
    "                            |",
    "                  tracker.procesar_frame(frame)",
    "                            |  YOLO model.track() + ByteTrack",
    "                            |",
    "                       nuevo track_id detectado?",
    "                            |  si",
    "                            v",
    "                  servo_controller.solicitar()",
    "                            |  encola con delay = ahora + SERVO_DELAY_S",
    "                            v",
    "                  hilo 'servo-controller' (cada 10 ms)",
    "                            |  vence el delay -> consulta clase del grano",
    "                            |",
    "                     es defecto?  --si--> SERVO:DEFECTO -> arduino_serial",
    "                            |  no                               |",
    "                     SERVO:BUENO --------------------------------> Arduino",
    "                                                                  |",
    "                                              mueve servo (canal bueno / defecto)",
    "",
    "Paralelo -- hilo 'arduino-reader':",
    "  readline() <- LISTO/PESO/etc. <- Arduino -> actualiza cache de estado",
]
for linea in lineas:
    add_code(doc, linea)
doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 3. DESDE EL HTML
# ══════════════════════════════════════════════════════════════════════════════
add_heading(doc, "3. Paso a Paso: Desde el HTML", 1)

add_heading(doc, "3.1 Carga de la pagina /monitoreo", 2)
add_para(doc, (
    "Al abrir la pagina, el JavaScript ejecuta automaticamente GET /video/status. "
    "Si el backend responde activo: true, arranca directamente el streaming. "
    "Si no, hace POST /video/iniciar para arrancar la captura."
))
add_file_ref(doc, "src/templates/monitoreo.html", "lineas 305-320 (arranque automatico)")
for linea in [
    "(async () => {",
    "  const res = await fetch('/video/status');",
    "  const { activo } = await res.json();",
    "  if (activo) {",
    "    iniciarStream();  // arranca el polling de frames",
    "  } else {",
    "    await fetch('/video/iniciar', { method: 'POST' });",
    "    iniciarStream();",
    "  }",
    "})();",
]:
    add_code(doc, linea)

add_heading(doc, "3.2 iniciarStream() -- polling de frames", 2)
add_para(doc, (
    "En lugar de un <video> nativo con MJPEG, el HTML hace polling de /video/frame "
    "cada 33 ms (~30 fps en el navegador). Cada respuesta es un JPEG individual que "
    "reemplaza el src del elemento <img id='cameraStream'>."
))
add_file_ref(doc, "src/templates/monitoreo.html", "funcion iniciarStream(), lineas 262-294")
for linea in [
    "const refrescarFrame = async () => {",
    "  const res = await fetch('/video/frame');",
    "  if (res.status === 503) {",
    "    frameTimeout = setTimeout(refrescarFrame, 33); // sin frame aun",
    "    return;",
    "  }",
    "  const url = URL.createObjectURL(await res.blob());",
    "  cameraStreamEl.src = url;  // reemplaza la imagen",
    "  frameTimeout = setTimeout(refrescarFrame, 33);  // siguiente frame",
    "};",
]:
    add_code(doc, linea)
add_para(doc, (
    "Por que polling y no MJPEG nativo: el polling por fetch permite detectar errores "
    "HTTP (503, timeouts) y mostrar mensajes de error al operador. Con un <img src> nativo "
    "de MJPEG no hay forma de capturar esos errores en JavaScript."
), italic=True, color=GRIS_SUAVE)

add_heading(doc, "3.3 Polling de conteo -- GET /video/lote/conteo", 2)
add_para(doc, (
    "Cada 2 segundos el HTML consulta el conteo de granos para actualizar "
    "los indicadores de la pantalla (total granos, total defectos, barras de defecto)."
))
for linea in [
    "setInterval(async () => {",
    "  const data = await fetch('/video/lote/conteo').then(r => r.json());",
    "  totalGrainsEl.textContent  = data.total_granos;",
    "  totalDefectsEl.textContent = data.total_defectos;",
    "  // actualiza barras de progreso por clase...",
    "}, 2000);",
]:
    add_code(doc, linea)
doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 4. CAMARA SERVICE
# ══════════════════════════════════════════════════════════════════════════════
add_heading(doc, "4. Capa de Captura: CamaraService", 1)
add_file_ref(doc, "src/services/camara_service.py")
add_para(doc, (
    "CamaraService tiene un unico trabajo: capturar frames de la camara fisica "
    "lo mas rapido posible y guardar solo el ultimo. No hace procesamiento."
))

add_heading(doc, "4.1 Inicializacion de la camara", 2)
add_para(doc, "Al llamar iniciar(), prueba los indices 0 y 1. Por cada indice:")
add_bullet(doc, "Abre con cv2.VideoCapture(idx)")
add_bullet(doc, "Configura buffer minimo: CAP_PROP_BUFFERSIZE = 1 (evita frames viejos acumulados)")
add_bullet(doc, "Solicita codec MJPEG: CAP_PROP_FOURCC = 'MJPG' (menos CPU que YUY2)")
add_bullet(doc, "Lee un frame de prueba para confirmar que la camara responde")
add_bullet(doc, "Detecta si la camara entrega MJPEG nativo (passthrough) para ahorrar una re-compresion")

add_heading(doc, "4.2 El bucle de captura _capture_loop()", 2)
for linea in [
    "while self._running:",
    "  ret, frame = cap.read()               # bloquea hasta nuevo frame del sensor",
    "  if not ret:",
    "    errores_consecutivos += 1",
    "    if errores_consecutivos >= 10:",
    "      self._running = False; break       # camara desconectada",
    "    continue",
    "  # Comprimir a JPEG calidad 95",
    "  _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 95])",
    "  self._latest_jpeg = buf.tobytes()      # sobreescribe el ultimo",
    "  self._new_frame.set()                  # senial al hilo tracker",
]:
    add_code(doc, linea)
add_para(doc, (
    "threading.Event.set() despierta al hilo tracker-processing que estaba esperando "
    "en esperar_frame(timeout=1.0). Asi evita busy-waiting: el hilo tracker no consume "
    "CPU mientras no hay frame nuevo."
), italic=True, color=GRIS_SUAVE)

add_heading(doc, "4.3 esperar_frame(timeout)", 2)
for linea in [
    "def esperar_frame(self, timeout: float = 1.0) -> bytes | None:",
    "  self._new_frame.wait(timeout)    # duerme hasta que haya frame nuevo",
    "  self._new_frame.clear()          # resetea la senial",
    "  return self._latest_jpeg         # retorna el ultimo JPEG",
]:
    add_code(doc, linea)
doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 5. TRACKER / YOLO
# ══════════════════════════════════════════════════════════════════════════════
add_heading(doc, "5. Procesamiento YOLO: CoffeeRenTracker", 1)
add_file_ref(doc, "src/ml/tracker.py")
add_para(doc, (
    "CoffeeRenTracker recibe frames en BGR (formato OpenCV) y retorna JPEG anotado "
    "con bounding boxes de cada grano detectado, su ID unico de ByteTrack, "
    "la clase de defecto y la confianza."
))

add_heading(doc, "5.1 Carga del modelo", 2)
add_para(doc, (
    "En el constructor, carga el archivo best.pt usando YOLO(model_path). "
    "Si el modelo solicitado no existe en disco, hace fallback automatico a yolov8n. "
    "El modelo se carga una sola vez al arrancar el servidor, nunca por peticion."
))
add_label(doc, "Ruta del modelo", "src/ml/models/{model_name}/best.pt")
add_label(doc, "Modelo activo",   "yolov26n_2cls  (instancia global en tracker_service.py)")
add_label(doc, "Umbral de conf.", "CONF_THRESHOLD = 0.50  (definido en tracker_service.py)")
add_para(doc, (
    "Las constantes de cada modelo (CLASES, COLORES, EQUIVALENCIAS_DEFECTO) se cargan "
    "dinamicamente desde src/ml/models/{model_name}/constants.py usando importlib."
), italic=True, color=GRIS_SUAVE)

add_heading(doc, "5.2 procesar_frame() -- el nucleo", 2)
add_para(doc, "Cada frame pasa por estos pasos en orden:")

pasos = [
    ("model.track()",
     "Llama a YOLO con tracker='bytetrack.yaml' y persist=True. ByteTrack asigna "
     "un track_id unico a cada grano que persiste entre frames mientras sea visible. "
     "persist=True es critico: sin el, el ID cambiaria cada frame y se contaria el "
     "mismo grano multiples veces."),
    ("Filtro de tamano",
     "Cada deteccion se filtra por ancho y alto del bbox: "
     "GRANO_MIN_PX <= w <= GRANO_MAX_PX. Esto descarta ruido de fondo, reflejos "
     "o particulas que YOLO detecte pero sean demasiado pequenias o grandes."),
    ("Registro del track_id",
     "Para cada bbox valido, se guarda (clase, confianza) en un dict: "
     "conteo_ids_confianza[track_id]. Un mismo grano puede aparecer en 20 frames "
     "con distintas clases si el modelo vacila; al final gana la clase de "
     "mayor confianza acumulada."),
    ("Solicitar servo (solo IDs nuevos)",
     "Si el track_id no esta en _ids_servados, se llama servo_controller.solicitar(). "
     "Esto programa la activacion del servo con el delay de la faja. Solo se programa "
     "una vez por grano, aunque aparezca en 50 frames."),
    ("Anotacion del frame",
     "Dibuja el bounding box con el color de la clase (definido en constants.py), "
     "y la etiqueta '#ID clase XX%' sobre fondo solido del mismo color. "
     "Agrega estadisticas globales en la esquina superior izquierda."),
    ("Codificacion JPEG",
     "cv2.imencode('.jpg', frame_anotado, quality=85) comprime el frame anotado. "
     "Calidad 85 es un balance entre tamano y legibilidad de las anotaciones."),
]
for titulo_paso, descripcion in pasos:
    add_heading(doc, titulo_paso, 3)
    add_para(doc, descripcion)

add_heading(doc, "5.3 Conteo sin duplicados: _calcular_conteo_final()", 2)
for linea in [
    "for track_id, detecciones in conteo_ids_confianza.items():",
    "  clase_final = max(detecciones, key=lambda x: x[1])[0]",
    "  # x[1] = confianza, x[0] = clase",
    "  conteo_por_clase[clase_final].add(track_id)",
    "",
    "return {clase: len(ids) for clase, ids in conteo_por_clase.items()}",
]:
    add_code(doc, linea)
add_para(doc, (
    "Resultado: si el grano #47 fue detectado 15 veces como 'negro' (conf 0.72) "
    "y 3 veces como 'verde' (conf 0.41), se cuenta como un unico grano negro. "
    "El conteo retorna {'negro': 1, ...}, nunca 2 por el mismo grano."
), italic=True, color=GRIS_SUAVE)
doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 6. TRACKER SERVICE
# ══════════════════════════════════════════════════════════════════════════════
add_heading(doc, "6. Coordinacion: TrackerService", 1)
add_file_ref(doc, "src/services/tracker_service.py")
add_para(doc, (
    "TrackerService es el pegamento entre CamaraService y CoffeeRenTracker. "
    "Es el unico punto de entrada que usan las rutas HTTP. "
    "Existe como instancia global: tracker_service = TrackerService(model_name='yolov26n_2cls')."
))

add_heading(doc, "6.1 iniciar()", 2)
add_bullet(doc, "Llama camara_service.iniciar() --> levanta el hilo camara-capture")
add_bullet(doc, "Espera 1 segundo y verifica que la camara este disponible")
add_bullet(doc, "Lanza el hilo tracker-processing (_loop_procesamiento)")

add_heading(doc, "6.2 _loop_procesamiento()", 2)
for linea in [
    "while self.activo:",
    "  if not camara_service.esta_disponible():",
    "    self._on_camara_desconectada(); break  # emergencia",
    "",
    "  jpeg_bytes = camara_service.esperar_frame(timeout=1.0)",
    "  frame      = self._jpeg_a_frame(jpeg_bytes)   # JPEG -> BGR ndarray",
    "  frame_anotado_jpeg = self.tracker.procesar_frame(frame)",
    "",
    "  with self._lock:",
    "    self._frame_anotado = frame_anotado_jpeg  # disponible para streaming",
]:
    add_code(doc, linea)

add_heading(doc, "6.3 obtener_frame_streaming()", 2)
add_para(doc, (
    "Esta funcion es la que llaman las rutas HTTP GET /video/frame y GET /video/stream. "
    "Solo hace 'return self._frame_anotado' bajo lock. Sin procesamiento. Sin bloqueos. "
    "El hilo tracker-processing ya actualizo ese valor antes."
))

add_heading(doc, "6.4 Manejo de desconexion de camara", 2)
for linea in [
    "def _on_camara_desconectada(self) -> None:",
    "  self.activo = False",
    "  self._camara_desconectada = True",
    "  servo_controller.bloquear()               # vacia la cola",
    "  arduino_serial.enviar_comando('SERVO:DEFECTO')  # posicion de seguridad",
]:
    add_code(doc, linea)
add_para(doc, (
    "Principio de seguridad: ante cualquier falla del sistema, el servo queda "
    "fijo en el canal de defectos. Es preferible desechar granos buenos que "
    "aprobar granos defectuosos sin clasificar."
), bold=True, color=CAFE_MEDIO)
doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 7. SERVO CONTROLLER
# ══════════════════════════════════════════════════════════════════════════════
add_heading(doc, "7. ServoController -- Separacion Fisica con Delay", 1)
add_file_ref(doc, "src/utilities/servo_controller.py")
add_para(doc, (
    "El ServoController resuelve un problema fisico: la camara ve el grano "
    "antes de que llegue al servo. Si se activa el servo en el momento de la "
    "deteccion, el servo se mueve cuando el grano aun esta lejos. "
    "El delay compensa el tiempo de viaje del grano en la faja."
))

add_heading(doc, "7.1 solicitar() -- programar la separacion", 2)
for linea in [
    "def solicitar(self, obtener_clase, equivalencias):",
    "  ejecutar_en = time.monotonic() + Config.SERVO_DELAY_S",
    "  # encola una _Solicitud con:",
    "  #   - obtener_clase: lambda que consulta la mejor clase del grano",
    "  #   - equivalencias: tabla defecto -> peso (de constants.py)",
    "  #   - ejecutar_en: timestamp futuro cuando el grano llegara al servo",
]:
    add_code(doc, linea)
add_para(doc, (
    "El lambda obtener_clase no captura la clase al llamar solicitar(), sino que "
    "consulta al tracker en el momento de ejecutar. Esto es intencional: al activar "
    "el servo el grano habra sido detectado en mas frames y la clase sera mas precisa."
), italic=True, color=GRIS_SUAVE)

add_heading(doc, "7.2 _worker() -- el hilo que ejecuta", 2)
for linea in [
    "while self._activo:  # cada 10 ms",
    "  if not self._bloqueado and cola[0].ejecutar_en <= ahora:",
    "    solicitud = cola.pop(0)",
    "    clase = solicitud.obtener_clase()   # consulta tracker ahora",
    "    es_defecto = equivalencias.get(clase, 0.0) > 0.0",
    "",
    "    if es_defecto:",
    "      arduino_serial.enviar_comando('SERVO:DEFECTO')",
    "      time.sleep(Config.SERVO_HOLD_S)  # mantiene mientras pasa el grano",
    "      arduino_serial.enviar_comando('SERVO:BUENO')",
    "    else:",
    "      arduino_serial.enviar_comando('SERVO:BUENO')",
]:
    add_code(doc, linea)
add_label(doc, "SERVO_DELAY_S", "segundos desde deteccion hasta que el grano llega al servo")
add_label(doc, "SERVO_HOLD_S",  "segundos que el servo mantiene la posicion de defecto")
add_para(doc, "Ambos valores se configuran en src/config.py segun la velocidad de la faja.", italic=True, color=GRIS_SUAVE)
doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 8. ARDUINO SERIAL
# ══════════════════════════════════════════════════════════════════════════════
add_heading(doc, "8. ArduinoSerial -- Comunicacion Serial", 1)
add_file_ref(doc, "src/utilities/arduino_serial.py")
add_para(doc, (
    "ArduinoSerial maneja la comunicacion bidireccional con el microcontrolador. "
    "Usa pyserial a 9600 baud con dos locks separados: uno para escritura al puerto "
    "(evitar colisiones entre hilos) y otro para el estado cacheado (lectura segura)."
))

add_heading(doc, "8.1 Protocolo de mensajes", 2)
add_para(doc, "Arduino --> Backend (lecturas continuas):", bold=True)
protocolo_entrada = [
    ("LISTO:15.34",    "Tapa cerrada, muestra detectada. Distancia al sensor = 15.34 cm"),
    ("NO_LISTO:45.21", "Sin muestra o tapa abierta. Distancia = 45.21 cm"),
    ("PESO:1234.56",   "Lectura de la celda de carga en gramos (promedio deslizante)"),
    ("TARE:OK",        "Confirmacion: bascula tarada"),
    ("SISTEMA:LISTO",  "Arduino reiniciado y listo"),
]
for cmd, desc in protocolo_entrada:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1); p.paragraph_format.space_after = Pt(3)
    r1 = p.add_run(f"  {cmd:<22}")
    r1.font.name = 'Courier New'; r1.font.size = Pt(10); r1.font.bold = True
    r1.font.color.rgb = VERDE_TEAL
    r2 = p.add_run(f"->  {desc}")
    r2.font.size = Pt(10); r2.font.color.rgb = NEGRO

doc.add_paragraph()
add_para(doc, "Backend --> Arduino (comandos):", bold=True)
protocolo_salida = [
    ("ON",             "Iniciar faja transportadora"),
    ("OFF",            "Detener faja y resetear servo a canal BUENO"),
    ("SERVO:BUENO",    "Mover servo al canal de granos buenos"),
    ("SERVO:DEFECTO",  "Mover servo al canal de granos defectuosos"),
    ("TARE",           "Tarar la bascula (poner en cero)"),
    ("SCALE:<factor>", "Actualizar factor de calibracion de la bascula"),
]
for cmd, desc in protocolo_salida:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1); p.paragraph_format.space_after = Pt(3)
    r1 = p.add_run(f"  {cmd:<22}")
    r1.font.name = 'Courier New'; r1.font.size = Pt(10); r1.font.bold = True
    r1.font.color.rgb = CAFE_MEDIO
    r2 = p.add_run(f"->  {desc}")
    r2.font.size = Pt(10); r2.font.color.rgb = NEGRO

add_heading(doc, "8.2 El hilo _reader_loop()", 2)
for linea in [
    "while self._activo and self._puerto.is_open:",
    "  linea = self._puerto.readline().decode('utf-8').strip()",
    "  if linea:",
    "    self._procesar_linea(linea)  # actualiza self._estado o self._peso",
]:
    add_code(doc, linea)
add_para(doc, (
    "readline() con timeout=1.0 s: si no llega ninguna linea en 1 segundo, retorna vacio "
    "y el bucle continua. Nunca bloquea indefinidamente."
))

add_heading(doc, "8.3 enviar_comando()", 2)
for linea in [
    "def enviar_comando(self, cmd: str) -> bool:",
    "  self._asegurar_conexion()           # reconecta si es necesario",
    "  with self._write_lock:              # solo un hilo escribe a la vez",
    "    self._puerto.write(f'{cmd}\\n'.encode('utf-8'))",
    "    return True",
]:
    add_code(doc, linea)

add_heading(doc, "8.4 Reconexion automatica", 2)
add_para(doc, (
    "_asegurar_conexion() verifica si el puerto sigue abierto antes de cada operacion. "
    "Si se desconecto, intenta reconectar, pero no mas de una vez cada 10 segundos "
    "(throttle) para no bloquear peticiones HTTP mientras el Arduino esta desenchufado."
))
doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 9. RUTAS HTTP
# ══════════════════════════════════════════════════════════════════════════════
add_heading(doc, "9. Rutas HTTP del Sistema", 1)
rutas = [
    ("POST", "/video/iniciar",              "Levanta hilos camara-capture y tracker-processing."),
    ("POST", "/video/detener",              "Detiene ambos hilos y libera la camara."),
    ("GET",  "/video/stream",               "StreamingResponse MJPEG. Alternativa al polling."),
    ("GET",  "/video/frame",                "Retorna el ultimo JPEG procesado. Usado por el HTML a 30fps."),
    ("GET",  "/video/status",               "Estado: activo, modelo, conteo actual, errores de camara."),
    ("GET",  "/video/lote/conteo",          "Conteo enriquecido: granos, defectos, sanos, segundos sin deteccion."),
    ("POST", "/video/lote/generar-reporte", "Reporte SCA final: grado, defectos equivalentes, apto specialty."),
    ("POST", "/video/lote/resetear",        "Resetea conteo para nuevo lote."),
    ("GET",  "/arduino/estado",             "Estado de distancia y tapa (del cache, sin bloquear)."),
    ("GET",  "/arduino/peso",               "Ultimo peso leido de la celda de carga."),
    ("POST", "/arduino/tare",               "Envia comando TARE al Arduino."),
    ("POST", "/arduino/motor/iniciar",      "Envia comando ON al Arduino (arranca faja)."),
    ("POST", "/arduino/motor/detener",      "Envia comando OFF al Arduino (detiene faja)."),
]
for metodo, ruta, descripcion in rutas:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(5)
    color_metodo = VERDE_TEAL if metodo == "GET" else CAFE_MEDIO
    r1 = p.add_run(f"{metodo:<5}")
    r1.font.name = 'Courier New'; r1.font.size = Pt(10); r1.font.bold = True
    r1.font.color.rgb = color_metodo
    r2 = p.add_run(f"  {ruta:<40}")
    r2.font.name = 'Courier New'; r2.font.size = Pt(10); r2.font.color.rgb = NEGRO
    r3 = p.add_run(descripcion)
    r3.font.size = Pt(10); r3.font.color.rgb = GRIS_SUAVE
doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 10. CONCEPTOS CLAVE
# ══════════════════════════════════════════════════════════════════════════════
add_heading(doc, "10. Conceptos Clave para Explicar el Sistema", 1)
conceptos = [
    ("ByteTrack",
     "Algoritmo de tracking que asigna un ID unico (track_id) a cada objeto detectado "
     "y lo mantiene entre frames mientras sea visible. Sin ByteTrack, cada frame el mismo "
     "grano seria un objeto nuevo y se contaria 60 veces por segundo."),
    ("persist=True en model.track()",
     "Le indica a YOLO que mantenga el estado de ByteTrack entre llamadas sucesivas. "
     "Si se pone False, ByteTrack resetea sus IDs cada frame y el tracking no funciona."),
    ("threading.Event",
     "Mecanismo de sincronizacion entre hilos. camara-capture hace set() cada nuevo frame "
     "y tracker-processing hace wait() hasta que llegue. Evita que tracker consuma CPU "
     "cuando no hay frames nuevos."),
    ("Estado cacheado",
     "ArduinoSerial actualiza self._estado en su hilo lector. Las rutas HTTP solo leen "
     "ese estado con un lock. Asi /arduino/estado responde en microsegundos sin tocar "
     "el puerto serial."),
    ("SERVO_DELAY_S",
     "Parametro de calibracion fisica. Es el tiempo en segundos que tarda un grano en "
     "recorrer la distancia entre donde lo ve la camara y donde esta el servo en la faja. "
     "Hay que medirlo fisicamente y ajustarlo en src/config.py."),
    ("Clase de mayor confianza",
     "Un grano puede aparecer en multiples frames con distintas predicciones. "
     "CoffeeRen elige la clase que tuvo la confianza individual mas alta en cualquiera "
     "de los frames. Una deteccion muy segura (0.92) pesa mas que diez mediocres (0.51)."),
    ("Posicion de seguridad DEFECTO",
     "Ante cualquier falla (camara desconectada, error en YOLO, servo bloqueado), "
     "el sistema manda el grano al canal de defectos. Es preferible rechazar un grano "
     "bueno que aprobar uno defectuoso en un sistema de calidad certificada."),
]
for titulo_concepto, explicacion in conceptos:
    add_heading(doc, titulo_concepto, 3)
    add_para(doc, explicacion)

# ══════════════════════════════════════════════════════════════════════════════
# GUARDAR
# ══════════════════════════════════════════════════════════════════════════════
output_path = r"d:\TesisPrj\docs\documentacion\Flujo_CapVideo_Arduino_CoffeeRen.docx"
doc.save(output_path)
print(f"OK: {output_path}")
