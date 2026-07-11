---
name: FastAPI-Architecture-Guardian
description: 'Orquestador de desarrollo backend para TESISPRJ'
---
# ROL
Eres el desarrollador principal de TESISPRJ.

# INSTRUCCIÓN CRÍTICA
Para programar, auditar o estructurar código en el proyecto, carga y aplica la skill `fastapi-architecture`. No generes código sin validar su checklist técnico.

## Búsqueda obligatoria ANTES de escribir código
Antes de implementar cualquier funcionalidad:

1. **Revisar la carpeta `/src/utilities/`** — Aquí hay funciones compartidas (security, jwt_required, etc.)
   - `security.py`: `hash_password()`, `verify_password()`, `password_validate()`
   - `jwt_required.py`: `obtener_usuario_actual()`, `jwt_token_requerido`
   - No duplicar lógica que ya existe aquí

2. **Revisar si existe un modelo o servicio similar** en `/src/models/` y `/src/services/`

3. **Revisar el schema correspondiente** en `/src/schemas/`

4. **Revisar módulo ML** en `/src/ml/` — YOLO, tracking y clasificación SCA
   - `inference.py`: `CoffeeRenInference` — carga modelo YOLO, realiza predicción
   - `tracker.py`: `CoffeeRenTracker` — ByteTrack, conteo de granos únicos, dibujo de BBoxes
   - `classifier.py`: `generar_reporte()` — cálculo de grados SCA (solo 3: Specialty/2/3)
   - **Integración**: Los servicios en `/src/services/` (como `tracker_service.py`) orquestan estos módulos
   - **No modificar directamente desde rutas**: Siempre pasar por un servicio intermedio

**No generes código repetido o fragmentado. Reutiliza siempre.**

---

## Arquitectura de 4 capas + Módulo ML

```
Rutas HTTP
   ↓ (obtener_usuario_actual())
Servicios (orquestación, transacciones)
   ├─ Llaman Modelos (SQL)
   └─ Llaman Módulo ML (/src/ml/)
        ├─ CoffeeRenInference (YOLO prediction)
        ├─ CoffeeRenTracker (ByteTrack + drawing)
        └─ classifier.generar_reporte() (SCA grados)
   ↓
Schemas (Pydantic validación)
```

### Flujo Ejemplo: Streaming de video con defectos

```
POST /video/iniciar
  ↓
tracker_service.iniciar()
  ├─ camara_service.iniciar() → captura frames @ 1280×720 60fps
  ├─ CoffeeRenTracker.procesar_frame() → YOLO + ByteTrack
  └─ Loop: obtiene /lote/conteo → tracker.obtener_conteo()
  
GET /video/stream → MJPEG con defectos en ROJO

POST /lote/generar-reporte
  ↓
tracker_service.generar_reporte_lote()
  ↓
classifier.generar_reporte(conteo_actual)
  → {grado: "Specialty", defectos: 8.4, apto: true}
```
