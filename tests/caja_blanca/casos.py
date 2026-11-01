"""Datos de ejecución de cada caso PCB-XX que no están en el Excel: archivo y
función reales, módulo cuya cobertura se mide, fragmento de código que va a la
ficha (con las marcas # C1/# C2/# C3, solo en el documento) y lo que verificó cada
camino.

Fragmento: lista de segmentos (desde, hasta, lineas_extra) en el orden del archivo.
`desde` y `hasta` son textos de la primera y la última línea del segmento; la
búsqueda empieza después del segmento anterior y se omiten los docstrings. Entre
segmentos se inserta "...".
Marcas: (texto de la línea, comentario, n-ésima aparición dentro del fragmento).
sangria_por_segmento: alinea cada segmento por separado cuando vienen de funciones distintas.

El resto de los datos (caminos, datos de entrada, resultado esperado) se lee del
Excel con leer_casos().
"""
import os
from pathlib import Path
from typing import Any

import openpyxl

CARPETA = Path(os.environ.get(
    "CAJA_BLANCA_DIR", r"D:\Ciclo 10\Tesis1\Documentacion\Pruebas\CajaBlanca"
))
EVIDENCIAS = CARPETA / "evidencias"


def leer_casos() -> dict[str, dict[str, Any]]:
    """Filas de la hoja Casos de Casos_Prueba_Caja_Blanca.xlsx, por código."""
    ws = openpyxl.load_workbook(CARPETA / "Casos_Prueba_Caja_Blanca.xlsx")["Casos"]
    columnas = [c.value for c in ws[1]]
    filas = (dict(zip(columnas, (c.value for c in fila))) for fila in ws.iter_rows(min_row=2) if fila[0].value)
    return {f["Código"]: f for f in filas}


PASOS_COMUNES = (
    "2. Ejecutar python -m pytest {prueba} -v --cov-branch.\n"
    "3. Revisar el resultado (PASSED o FAILED) de cada camino.\n"
    "4. Revisar la cobertura de ramas de la función evaluada."
)

CASOS: dict[str, dict[str, Any]] = {
    "PCB-01": {
        "archivo": "src/services/auth_service.py",
        "funcion": "AuthService.autenticar()",
        "modulo_cov": "src.services.auth_service",
        "funciones_cov": ["AuthService.autenticar"],
        "preparar": "Simular el model Personal con pcn_operario activo y su contraseña en Argon2.",
        "fragmento": [
            ("def autenticar", "except (VerifyMismatchError", 1),
            ("token = generar_token(payload)", "token = generar_token(payload)", 0),
        ],
        "marcas": [
            ("if not usuario_db:", "# C2"),
            ("self.password_hasher.verify", "# C3: Argon2 no coincide"),
            ("token = generar_token(payload)", "# C1"),
        ],
        "obtenido": {
            "C1": "devuelve LoginResponse con token JWT; el token contiene personal_id, usuario (pcn_operario) y rol (Evaluador)",
            "C2": "devuelve None: credenciales rechazadas, sin token",
            "C3": "devuelve None: Argon2 no coincide, sin token",
        },
        "observaciones": "",
    },
    "PCB-02": {
        "archivo": "src/utilities/jwt_required.py",
        "funcion": "obtener_usuario_actual()",
        "modulo_cov": "src.utilities.jwt_required",
        "funciones_cov": ["obtener_usuario_actual"],
        "preparar": "Generar tokens de prueba y simular Personal.esta_activo (pcn_operario activo, pcn_desactivado inactivo).",
        "fragmento": [("def obtener_usuario_actual", "return payload", 0)],
        "marcas": [
            ("if not token_cookie:", "# C2: sin cookie"),
            ("if not payload:", "# C2: token alterado o expirado"),
            ("if not auth_service.cuenta_habilitada", "# C3: cuenta desactivada"),
            ("return payload", "# C1"),
        ],
        "obtenido": {
            "C1": "HTTP 200: la dependencia devuelve el payload del usuario y la petición continúa",
            "C2": "sin cookie, token alterado y token expirado: HTTP 303 a /auth/login en los tres casos",
            "C3": "HTTP 303 a /auth/login: la sesión de la cuenta desactivada se rechaza",
        },
        "observaciones": (
            "C3: la sesión deja de ser válida porque cada petición consulta el estado de la cuenta; "
            "la cookie no se borra, pero toda petición con ella se redirige al login. "
            "La redirección se probó con el mismo manejador de RequerirLoginException que tiene src/main.py."
        ),
    },
    "PCB-03": {
        "archivo": "src/schemas/evaluacion.py",
        "funcion": "RegistrarEvaluacionRequest.validar_pesos()",
        "modulo_cov": "src.schemas.evaluacion",
        "funciones_cov": ["RegistrarEvaluacionRequest.validar_pesos"],
        "preparar": "Armar los datos de una muestra válida (300 g de muestra, 240 g trillado) y sus variantes.",
        "fragmento": [
            ("peso_bruto: Decimal = Field", "peso_tamizado: Decimal = Field", 0),
            ("@model_validator", "def validar_pesos", 0),
            ("if self.peso_trillado > Decimal(\"0.83\")", "return self", 0),
        ],
        "marcas": [
            ("peso_bruto: Decimal = Field", "# C2: peso <= 0"),
            ("humedad: int = Field", "# C5: humedad <= 30"),
            ("if self.peso_trillado > Decimal(\"0.83\")", "# C3"),
            ("if self.peso_tamizado > self.peso_trillado:", "# C4"),
            ("return self", "# C1"),
        ],
        "obtenido": {
            "C1": "datos válidos: el schema se crea sin errores",
            "C2": "ValidationError en peso_bruto (greater_than): el dato se rechaza; la API lo muestra como \"peso_bruto: debe ser mayor que 0.\"",
            "C3": "ValidationError: \"El peso trillado no puede superar el 83% del peso de muestra\" (83 % de 300 g = 249 g)",
            "C4": "ValidationError: \"El peso tamizado no puede ser mayor al peso trillado\"",
            "C5": "humedad = 30 aceptada; 31 rechazada (less_than_equal, le = 30); 0 rechazada (greater_than_equal, ge = 1); 12.5 rechazada por no ser entera (int_from_float)",
        },
        "observaciones": "El mensaje de C3 no indica el máximo en gramos. C5: el límite de humedad se valida en Field, antes de validar_pesos(), igual que el peso positivo de C2.",
    },
    "PCB-04": {
        "archivo": "src/services/evaluacion_service.py",
        "funcion": "EvaluacionService.registrar_evaluacion()",
        "modulo_cov": "src.services.evaluacion_service",
        "funciones_cov": ["EvaluacionService.registrar_evaluacion"],
        "preparar": "Simular la conexión y los models Caficultor, TipoGrano, ValorCafe y Evaluacion.",
        "fragmento": [
            ("def registrar_evaluacion", "raise ValueError(\"El caficultor no se encuentra activo.\")", 0),
            ("if not self.valor_cafe_model.obtener_resumen_rangos", "\"que registre los precios del día", 1),
            ("fila = self.evaluacion_model.registrar(", "fila = self.evaluacion_model.registrar(", 0),
            ("db.commit()", "db.commit()", 0),
        ],
        "marcas": [
            ("if not caficultor:", "# C2: inexistente"),
            ("if str(caficultor.get(\"estado\")) != \"A\":", "# C2: inactivo"),
            ("if not self.valor_cafe_model.obtener_resumen_rangos", "# C3"),
            ("fila = self.evaluacion_model.registrar(", "# C1"),
        ],
        "obtenido": {
            "C1": "evaluación creada (registrado = True) con código vacío, es decir activa; se hizo commit",
            "C2": "ValueError para documento no registrado y para caficultor inactivo; no se llamó a registrar ni a commit",
            "C3": "ValueError \"No hay precios de café registrados hoy...\"; no se creó la evaluación",
        },
        "observaciones": (
            "C3: el código exige precios con fecha de hoy, no solo que VALOR_CAFE tenga filas; "
            "se simuló sin precios de hoy."
        ),
    },
    "PCB-05": {
        "archivo": "src/services/evaluacion_service.py",
        "funcion": "EvaluacionService.completar_evaluacion()",
        "modulo_cov": "src.services.evaluacion_service",
        "funciones_cov": ["EvaluacionService.completar_evaluacion"],
        "preparar": "Simular una evaluación con muestra de 300 g, trillado de 240 g y tamizado de 230 g; usar el rango 40-100 y, en C4, 60-65 y 66-70.",
        "fragmento": [
            ("divisor = peso_muestra / 100", "factor_rendimiento = (peso_bueno / divisor)", 0),
            ("valor_cafe = self.valor_cafe_model.obtener_por_factor", "precio = Decimal(str(valor_cafe", 0),
        ],
        "marcas": [
            ("if peso_bueno > peso_tamizado:", "# C2"),
            ("if not valor_cafe:", "# C3"),
            ("valor_cafe = self.valor_cafe_model.obtener_por_factor", "# C4: precio por parte entera"),
            ("precio = Decimal(str(valor_cafe", "# C1"),
        ],
        "obtenido": {
            "C1": "FR = 66.67; se asigna el rango 40-100 con precio S/ 2000",
            "C2": "se rechaza el peso final: ValueError \"El peso de grano bueno (235 g) no puede superar el peso tamizado (230 g).\"",
            "C3": "ValueError \"No hay precio de café registrado hoy para el rango del factor de rendimiento (39.67)...\"",
            "C4": "197 g / (300 g / 100) = FR 65.67; se guarda 65.67 y se usa el rango 60-65 a S/ 1900 (no 66-70 a S/ 2000)",
        },
        "observaciones": (
            "C4 usa un doble de obtener_por_factor (tests/caja_blanca/conftest.py) y verifica la lógica "
            "del service, no la consulta SQL. La consulta con FLOOR de src/models/valor_cafe.py se "
            "verificó aparte en PostgreSQL: 65.67 y 65.99 → 60-65; 66.00 → 66-70; "
            "71.50 → rango simple 71; 39.67 → sin rango."
        ),
    },
    "PCB-06": {
        "archivo": "src/services/evaluacion_service.py",
        "funcion": "EvaluacionService.completar_evaluacion()",
        "modulo_cov": "src.services.evaluacion_service",
        "funciones_cov": ["EvaluacionService.completar_evaluacion"],
        "preparar": "Simular una evaluación de 4 sacos y 200.00 kg, Pergamino (55.20 kg/qq), caficultor Externo y precio S/ 2000.",
        "fragmento": [
            ("tara_total         = int(round", "pago_base   = (peso_por_qq * precio)", 0),
        ],
        "marcas": [
            ("if humedad > Decimal(\"12.00\"):", "# C2"),
            ("peso_neto_humedad = Decimal(\"0.00\")", "# C1"),
            ("peso_por_qq = ((peso_neto", "# C3: ROUND_DOWN a 2 decimales"),
        ],
        "obtenido": {
            "C1": "tara = 1, peso neto = 199.00, sin castigo: peso por quintal = 3.60",
            "C2": "castigo 7.02 aplicado: peso por quintal = 3.47 y pago = S/ 6940.00",
            "C3": "peso por quintal = 3.60 (redondeo hacia abajo, no 3.61) y pago = S/ 7200.00",
        },
        "observaciones": (
            "Celda amarilla confirmada en el código: el peso por quintal se redondea hacia abajo a 2 "
            "decimales (ROUND_DOWN a 0.01). Se usó un caficultor Externo: a un socio se le suma el "
            "beneficio de socio al pago."
        ),
    },
    "PCB-07": {
        "archivo": "src/ml/classifier.py",
        "funcion": "calcular_defectos()",
        "modulo_cov": "src.ml.classifier",
        "funciones_cov": ["calcular_defectos"],
        "preparar": "Armar los conteos por clase y usar EQUIVALENCIAS_DEFECTO del modelo yolov26n_2cls.",
        "fragmento": [
            ("def calcular_defectos", "\"total_defectos\":  round(total_defectos, 2),", 1),
        ],
        "marcas": [
            ("if cantidad == 0:", "# C3: cantidad 0"),
            ("if peso is None:", "# C3: sin equivalencia"),
            ("defectos_equivalentes = round(cantidad * peso, 2)", "# C1: peso 0 / C2: peso > 0"),
        ],
        "obtenido": {
            "C1": "{verde: 20}: total_defectos = 0",
            "C2": "{defecto: 15, verde: 5}: total_defectos = 15",
            "C3": "{defecto: 0, piedra: 3}: total_defectos = 0 y detalle vacío",
        },
        "observaciones": (
            "Caso reemplazado con autorización del responsable: la asignación de grado 1/2/3 no existe "
            "(el grado SCA se retiró del sistema). Se prueba calcular_defectos(), que suma los defectos "
            "equivalentes del lote."
        ),
    },
    "PCB-08": {
        "sangria_por_segmento": True,
        "archivo": "src/services/valor_cafe_service.py",
        "funcion": "ValorCafeService.crear_precios_bloque()",
        "modulo_cov": "src.services.valor_cafe_service",
        "funciones_cov": [
            "ValorCafeService.crear_precios_bloque",
            "ValorCafeService._validar_sin_solapamiento",
            "ValorCafeService._validar_precios_no_decrecientes",
            "_se_superponen",
        ],
        "preparar": "Simular el model ValorCafe sin precios registrados hoy.",
        "fragmento": [
            ("def _se_superponen", "return a[0] <= b[1]", 0),
            ("if _se_superponen(parsed, parsed_previo):", "raise ValueError(", 0),
            ("if precio_actual < precio_prev:", "raise ValueError(", 0),
            ("def crear_precios_bloque", "filas = self.model.crear_bloque", 0),
        ],
        "marcas": [
            ("if _se_superponen(parsed, parsed_previo):", "# C2"),
            ("if precio_actual < precio_prev:", "# C3"),
            ("filas = self.model.crear_bloque", "# C1"),
        ],
        "obtenido": {
            "C1": "bloque aceptado: se registran 2 rangos",
            "C2": "ValueError \"El rango '65-70' se solapa con el rango '60-65'.\"; no se registra nada",
            "C3": "ValueError \"El precio del rango '60-100' (S/ 1800.00) no puede ser menor al del rango '40-59' (S/ 2000.00).\"",
        },
        "observaciones": (
            "Límites en el formato del sistema (enteros X-Y): 40-59 en lugar de 40-59.99, como permite la nota del Excel."
        ),
    },
    "PCB-09": {
        "archivo": "src/models/evaluacion.py",
        "funcion": "Evaluacion.asignar_codigo(), llamada por EvaluacionService.finalizar_evaluacion()",
        "modulo_cov": "src.models.evaluacion",
        "funciones_cov": ["Evaluacion.asignar_codigo", "Evaluacion._generar_codigo"],
        "preparar": "Simular la conexión: evaluación sin código y último correlativo EVA0000041.",
        "fragmento": [
            ("return f\"EVA{int(row['siguiente']):07d}\"", "return f\"EVA{int(row['siguiente']):07d}\"", 0),
            ("existente = db.obtener_uno(", "incidencias_json = json.dumps", 0),
        ],
        "marcas": [
            ("return f\"EVA{int(row['siguiente']):07d}\"", "# C1: siguiente correlativo"),
            ("codigo = existente.get(\"codigo\") or self._generar_codigo(db)", "# C1: sin código / C2: lo reutiliza"),
        ],
        "obtenido": {
            "C1": "genera EVA0000042 y guarda total_defectos = 12, total_buenos = 88 e incidencias",
            "C2": "el segundo llamado devuelve EVA0000042 sin consultar un nuevo correlativo",
        },
        "observaciones": (
            "La idempotencia está en el model (Evaluacion.asignar_codigo), no en el service. "
            "Se probó llamando a EvaluacionService.finalizar_evaluacion()."
        ),
    },
    "PCB-10": {
        "archivo": "src/ml/tracker.py",
        "funcion": "CoffeeRenTracker._resolver_clase()",
        "modulo_cov": "src.ml.tracker",
        "funciones_cov": ["CoffeeRenTracker._resolver_clase"],
        "preparar": "Crear el tracker con el modelo YOLO simulado y armar historiales de detecciones.",
        "fragmento": [
            ("def _resolver_clase(self", "return max(sanas", 1),
        ],
        "marcas": [
            ("if clase_top in sanas:", "# C1"),
            ("if peso_sana > 0.0 and peso[clase_top] < peso_sana * self.MARGEN_DEFECTO:", "# C3"),
            ("return clase_top", "# C2", 2),
        ],
        "obtenido": {
            "C1": "2 × defecto (0.60) y 4 × verde (0.90): verde",
            "C2": "4 × defecto (0.60) y 2 × verde (0.90): defecto (2.40 >= 2.34)",
            "C3": "2 × defecto (0.50) y 1 × verde (0.90): verde (1.00 < 1.17)",
        },
        "observaciones": (
            "Caso ajustado a la regla real con autorización del responsable: el código no usa 5 "
            "detecciones ni promedio 0.45; suma la confianza por clase con MARGEN_DEFECTO = 1.3. "
            "Con los datos originales del Excel, C3 daba defecto."
        ),
    },
    "PCB-11": {
        "archivo": "src/ml/tracker.py",
        "funcion": "CoffeeRenTracker.procesar_frame() (filtro de tamaño)",
        "modulo_cov": "src.ml.tracker",
        "funciones_cov": ["CoffeeRenTracker.procesar_frame"],
        "preparar": "Crear el tracker con el modelo YOLO, ByteTrack y el servo simulados; armar cajas de 49, 50, 640 y 641 px.",
        "fragmento": [
            ("for pista in tracks:", "for pista in tracks:", 0),
            ("# Filtro de tamaño: descarta", "and self.GRANO_MIN_PX <= h <= self.GRANO_MAX_PX):", 0),
            ("continue", "continue", 0),
            ("self.conteo_ids_confianza[track_id].append", "self.conteo_ids_confianza[track_id].append", 0),
        ],
        "marcas": [
            ("if not (self.GRANO_MIN_PX <= w <= self.GRANO_MAX_PX", "# C2: < 50 / C3: > 640"),
            ("self.conteo_ids_confianza[track_id].append", "# C1"),
        ],
        "obtenido": {
            "C1": "cajas de 50 px y de 640 px: se cuentan (1 grano cada una)",
            "C2": "caja de 49 px: se descarta (0 granos)",
            "C3": "caja de 641 px: se descarta (0 granos)",
        },
        "observaciones": (
            "Celda amarilla confirmada: los límites son inclusivos. Con autorización del responsable se "
            "usó GRANO_MAX_PX = 640, valor vigente en constants.py (el Excel decía 300). La cobertura "
            "es parcial porque procesar_frame() también contiene el dibujo, la latencia y el streaming, "
            "que este caso no prueba."
        ),
    },
    "PCB-12": {
        "sangria_por_segmento": True,
        "archivo": "src/ml/tracker.py",
        "funcion": "CoffeeRenTracker._evidencia_suficiente()",
        "modulo_cov": "src.ml.tracker",
        "funciones_cov": ["CoffeeRenTracker._evidencia_suficiente"],
        "preparar": "Crear el tracker con el modelo YOLO simulado; usar servo_controller sin cambios y simular arduino_serial.",
        "fragmento": [
            ("if track_id not in self._ids_servados and self._evidencia_suficiente(track_id):",
             "servo_controller.solicitar(", 0),
            ("def _evidencia_suficiente", "return max(c for _, c in dets) >= self.SERVO_CONF_MIN", 0),
        ],
        "marcas": [
            ("if len(dets) >= self.SERVO_MIN_FRAMES:", "# C2: 2 o más detecciones"),
            ("return max(c for _, c in dets) >= self.SERVO_CONF_MIN", "# C1: < 0.45 / C3: >= 0.45"),
        ],
        "obtenido": {
            "C1": "1 × defecto (0.30): no se llama a solicitar() y no sale SERVO:DEFECTO",
            "C2": "2 × defecto (0.30): una solicitud; el Arduino simulado recibe SERVO:DEFECTO",
            "C3": "1 × defecto (0.50): una solicitud; el Arduino simulado recibe SERVO:DEFECTO",
        },
        "observaciones": (
            "servo_controller.py y arduino_serial.py no se modificaron; solo se simuló el puerto serie. "
            "SERVO_DELAY_S y SERVO_HOLD_S se usaron con sus valores calibrados."
        ),
    },
}
