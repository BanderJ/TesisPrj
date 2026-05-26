# API Video Streaming & Análisis ML — Referencia

## Endpoints Disponibles

### Streaming MJPEG (Sin autenticación)

#### `GET /video/stream`
Retorna stream MJPEG en tiempo real con frames anotados.

**Características:**
- ✅ Defectos detectados en **ROJO** (bounding box rojo)
- ✅ Nombre del defecto + confianza en etiqueta
- ✅ ID único por grano (para tracking sin duplicados)
- ✅ Contador total en esquina superior izquierda
- ✅ FPS actual

**Respuesta:**
```
Content-Type: multipart/x-mixed-replace; boundary=frame
[JPEG frames continuos a 60 FPS]
```

**Ejemplo HTML:**
```html
<img src="/video/stream" style="width: 100%;" />
```

**Ejemplo JavaScript:**
```javascript
const stream = document.getElementById('stream');
stream.src = '/video/stream';
```

---

### Control de Captura (Con JWT)

#### `POST /video/iniciar`
Inicia la captura de video y procesamiento con YOLO.

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Response:** `200 OK`
```json
{
  "mensaje": "Monitoreo iniciado exitosamente",
  "activo": true
}
```

**Errores:**
- `500` — No se pudo abrir la cámara (USB desconectada)

---

#### `POST /video/detener`
Detiene la captura y streaming.

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Response:** `200 OK`
```json
{
  "mensaje": "Monitoreo detenido",
  "activo": false
}
```

---

### Análisis de Lotes (Con JWT)

#### `GET /lote/conteo`
Retorna el conteo actual de granos detectados (sin generar reporte final).

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Response:** `200 OK`
```json
{
  "conteo": {
    "negro": 5,
    "partido_maquina": 3,
    "averanado": 2,
    "broca_severo": 1
  },
  "total_granos": 11,
  "clases_detectadas": 4
}
```

---

#### `POST /lote/generar-reporte`
Genera el reporte final del lote (clasificación SCA).

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Response:** `200 OK`
```json
{
  "total_granos_analizados": 11,
  "total_defectos": 8.4,
  "grado": "Grado 1 (Specialty)",
  "apto_specialty": true,
  "detalle_por_clase": {
    "negro": {
      "granos": 5,
      "peso_por_grano": 1.0,
      "defectos_equivalentes": 5.0
    },
    "partido_maquina": {
      "granos": 3,
      "peso_por_grano": 0.2,
      "defectos_equivalentes": 0.6
    },
    "averanado": {
      "granos": 2,
      "peso_por_grano": 0.2,
      "defectos_equivalentes": 0.4
    },
    "broca_severo": {
      "granos": 1,
      "peso_por_grano": 1.0,
      "defectos_equivalentes": 1.0
    }
  },
  "resumen": "Lote analizado: 11 granos — 8.4 defectos equivalentes — Grado 1 (Specialty) — APTO para Specialty"
}
```

**Interpretación:**
- `total_defectos <= 15`: Grado 1 (Specialty) ✅
- `total_defectos 16-23`: Grado 2 ❌
- `total_defectos 24-30`: Grado 3 ❌
- `total_defectos > 30`: No clasificable ❌

---

#### `POST /lote/resetear`
Resetea el conteo para iniciar análisis de un nuevo lote.

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Response:** `200 OK`
```json
{
  "mensaje": "Lote reseteado. Listo para nuevo análisis.",
  "conteo": {}
}
```

---

#### `GET /video/status`
Verifica el estado actual del sistema (sin autenticación para debugging).

**Response:** `200 OK`
```json
{
  "activo": true,
  "modelo": "yolov8n",
  "conteo_actual": {
    "negro": 5,
    "partido_maquina": 3
  }
}
```

---

## Flujo de Uso Típico

### 1. Inicio de Sesión
```bash
POST /auth/login
{
  "usuario": "evaluador1",
  "contraseña": "tu-password"
}
→ Recibe JWT en cookie `access_token`
```

### 2. Iniciar Monitoreo
```bash
POST /video/iniciar
Authorization: Bearer <JWT>
→ Abre cámara, inicia tracker YOLO + ByteTrack
→ /video/stream comienza a retornar frames anotados
```

### 3. Ver Streaming (en HTML/JS)
```html
<div class="video-container">
  <img id="stream" src="/video/stream" style="max-width: 100%;" />
  <button onclick="obtenerConteo()">Actualizar Conteo</button>
</div>

<script>
async function obtenerConteo() {
  const res = await fetch('/lote/conteo');
  const data = await res.json();
  console.log('Granos detectados:', data);
}
</script>
```

### 4. Al Finalizar el Lote
```bash
# Obtener reporte final
POST /lote/generar-reporte
Authorization: Bearer <JWT>
→ JSON con grado, defectos, apto_specialty, detalle

# Resetear para siguiente lote
POST /lote/resetear
Authorization: Bearer <JWT>
→ Limpia conteo
```

### 5. Detener
```bash
POST /video/detener
Authorization: Bearer <JWT>
→ Cierra cámara y tracker
```

---

## Configuración Recomendada

### En `monitoreo.html`

```html
<template>
  <section class="video-monitor">
    <!-- Stream MJPEG -->
    <div class="stream-container">
      <img id="mjpeg-stream" src="/video/stream" alt="Streaming" />
      <div class="overlay-stats">
        <div id="conteo-actual">Cargando...</div>
      </div>
    </div>

    <!-- Panel de Control -->
    <div class="control-panel">
      <button @click="iniciar">🎥 Iniciar Captura</button>
      <button @click="detener">⏹️  Detener</button>
      <button @click="obtenerConteo">📊 Actualizar Conteo</button>
      <button @click="generarReporte">📋 Generar Reporte</button>
    </div>

    <!-- Resultados -->
    <div v-if="reporte" class="reporte-panel">
      <h3>Reporte del Lote</h3>
      <p>Grado: <strong>{{ reporte.grado }}</strong></p>
      <p>Defectos: <strong>{{ reporte.total_defectos }}</strong></p>
      <p>¿Apto Specialty? <strong>{{ reporte.apto_specialty ? '✅ Sí' : '❌ No' }}</strong></p>
      <p>{{ reporte.resumen }}</p>
    </div>
  </section>
</template>

<script>
export default {
  data() {
    return {
      conteo: null,
      reporte: null
    };
  },
  methods: {
    async iniciar() {
      const res = await fetch('/video/iniciar', { method: 'POST' });
      const data = await res.json();
      console.log(data.mensaje);
    },
    async detener() {
      const res = await fetch('/video/detener', { method: 'POST' });
      const data = await res.json();
      console.log(data.mensaje);
    },
    async obtenerConteo() {
      const res = await fetch('/lote/conteo');
      this.conteo = await res.json();
      console.log('Conteo:', this.conteo);
    },
    async generarReporte() {
      const res = await fetch('/lote/generar-reporte', { method: 'POST' });
      this.reporte = await res.json();
      console.log('Reporte:', this.reporte);
    }
  }
};
</script>
```

---

## Solución de Problemas

### El stream muestra imagen estática
**Causa:** Captura no iniciada.
**Solución:** `POST /video/iniciar` antes de acceder a `/video/stream`

### Error 500 en iniciar
**Causa:** Cámara no detectada.
**Solución:** 
- Verificar USB (ELP AR0234 conectada)
- Revisar drivers de cámara
- Probar con otra aplicación de video

### No hay detecciones (conteo vacío)
**Causa:** Modelo YOLO no cargado o deficiencia de confianza.
**Solución:**
- Verificar que `best.pt` existe en `src/ml/models/yolov8n/`
- Bajar confianza (conf=0.3) en tracker_service.py
- Verificar luz/enfoque de la cámara

### Baja velocidad de FPS
**Causa:** GPU no disponible, procesamiento en CPU.
**Solución:**
- Verificar PyTorch con CUDA: `python -c "import torch; print(torch.cuda.is_available())"`
- Instalar CUDA si es disponible
- Reducir resolución modelo (usar yolov5n en lugar de yolov8)

---

## Especificaciones Técnicas

| Parámetro | Valor |
|-----------|-------|
| **Resolución** | 1280×720 |
| **FPS Captura** | 60 |
| **Codec Streaming** | MJPEG |
| **Calidad JPEG** | 85% |
| **Timeout Stream** | 1.0s |
| **Buffer Cámara** | 1 frame |
| **Modelo YOLO** | yolov8n (default) |
| **Tracker** | ByteTrack |
| **Confianza mínima** | 0.5 (configurable) |

