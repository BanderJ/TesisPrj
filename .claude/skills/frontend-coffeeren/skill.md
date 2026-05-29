---
id: frontend-coffeeren
name: frontend-coffeeren
description: Frontend expert para CoffeeRen — templates Jinja2, design system CSS, integración FastAPI, UX/UI y Arduino serial.
---

# MISIÓN
Crear y mantener interfaces de usuario en CoffeeRen: templates Jinja2 bien estructurados, CSS limpio sin duplicación, integración correcta con las APIs FastAPI y experiencia de usuario **profesional, austera, experta** (sin "AI aesthetics").

Antes de cualquier tarea de frontend **consulta el agente `FastAPI-Architecture-Guardian`** si necesitas saber qué endpoints existen, qué campos retornan o cómo están construidas las rutas.

---

# ENFOQUE PROFESIONAL (Sin IA Slop)

**Cada cambio visual debe resolver un PROBLEMA específico.** Nunca agregar algo decorativo.

## Principios de Experto UX/UI
- **Jerarquía clara**: El usuario sabe qué ver primero
- **Tipografía funcional**: Legible, clara, sin "personalidad innecesaria"
- **Color con propósito**: Cada color comunica estado, no decora
- **Motion solo donde ayuda**: Transiciones `0.2-0.3s` para entender cambios, nada más
- **Espaciado deliberado**: Grid de `8px`, respira pero no sofoca
- **Consistencia extrema**: Las reglas son claras y se cumplen

## Antipatrones IA
❌ Fuentes "bonitas"  
❌ Gradientes coloridos  
❌ Animaciones en todo  
❌ Efectos shadow dramáticos  
❌ Hover effects chocantes  

✅ Fuentes legibles  
✅ Color plano con propósito  
✅ Motion funcional donde ayuda  
✅ Sombras sutiles, consistentes  
✅ Transiciones imperceptibles

---

# REGLA DE ORO: REVISAR ANTES DE CREAR

**PROTOCOLO OBLIGATORIO antes de escribir cualquier CSS, componente HTML o función JS:**

## 🔍 PASO 1: ¿Qué es lo que voy a agregar? (Clasificar)
- ¿Es CSS de presentación (estilos visuales)?
- ¿Es componente HTML (estructura)?
- ¿Es lógica JavaScript?

## 🔍 PASO 2: ¿Ya existe en main.css?
```bash
Grep "nombre-clase" en src/static/css/main.css
```
**Decisión:**
- **Existe y cumple** → Usar directamente. **Nunca** duplicar.
- **Existe pero necesita ajuste menor** → Override mínimo en `<pagina>.css` (especificidad aumentada: `.page-name .clase { ... }`)
- **No existe** → Decide si va en main.css o <pagina>.css (ver PASO 3)

## 🔍 PASO 3: ¿Se usa en 2+ páginas o es único?
**SI se usa en 2+ páginas:**
```
✅ → Crear en main.css (compartido)
```
**SI es único para UNA página:**
```
✅ → Crear en <pagina>.css (específico)
```

### Ejemplos reales:
| Clase | Ubicación | Razón |
|-------|-----------|-------|
| `.btn`, `.btn-primary` | main.css | Usado en TODAS las páginas |
| `.card`, `.page-hero` | main.css | Componente compartido |
| `.monitoreo-feed-stats` | monitoreo.css | Solo en /monitoreo |
| `.analisis-toolbar` | analisis.css | Solo en /analisis |
| `.defect-track` | monitoreo.css | Solo usada en defect list de monitoreo |

## 🔍 PASO 4: ¿Ya existe el componente HTML?
```bash
Grep "clase-o-id-del-componente" en src/templates/
```
- Estructura idéntica → Reutilizar exactamente, mismas clases, sin variantes.
- Estructura similar → Usar clase base + modificador: `.card` + `.card--wide`
- Estructura única → Crear nueva, con clases específicas de esa página.

## 🔍 PASO 5: ¿Ya existe la función JS?
```bash
Grep "nombreFuncion" en src/templates/
```
- Función idéntica → Extraer a `/static/js/shared.js` o `/static/js/<modulo>.js`
- Lógica similar → Parametrizar la existente antes de crear nueva
- Única → Inline en el template o archivo JS específico de la página

## 🔍 PASO 6: ¿Ya existe el endpoint en el backend?
Consultar `FastAPI-Architecture-Guardian` o:
```bash
Grep "router\|@.*_router" en src/routes/
```
- **Existe** → Consumirlo tal cual, sin crear uno nuevo.
- **No existe** → Solicitarlo al skill `fastapi-architecture`

## Flujo de decisión (RESUMEN)
```
┌─ ¿Ya existe en main.css?
│  ├─ SÍ, cumple ─→ Usar directamente
│  ├─ SÍ, ajuste menor ─→ Override en <pagina>.css
│  └─ NO ─→ Paso siguiente
│
├─ ¿Se usa en 2+ páginas?
│  ├─ SÍ ─→ Crear en main.css
│  └─ NO ─→ Crear en <pagina>.css
│
└─ Escribir el código
```

**❌ NUNCA:** Crear CSS duplicado. Crear componentes sin buscar primero. Crear funciones que ya existen.  
**✅ SIEMPRE:** Reutilizar. Parametrizar. Combinar con lo existente.

---

# ESTRUCTURA DE PÁGINAS

## Template base (`main.html`)
Toda página usa `{% extends "main.html" %}` y dos bloques:

```html
{% extends "main.html" %}

{% block style %}
<link rel="stylesheet" href="/static/css/<pagina>.css?v=1">
{% endblock %}

{% block content %}
<!-- contenido -->
{% endblock %}
```

**Nunca** repetir nav, header, footer, modales ni scripts de main.html.  
**Siempre** incrementar `?v=N` en el link CSS al modificar el archivo CSS.

## Excepción: login.html
Es la única página sin `{% extends %}` — tiene su propio `<html>` completo y carga `login.css` directamente.

---

# SISTEMA DE DISEÑO (CSS VARIABLES)

```css
--primary              /* verde principal */
--primary-foreground   /* texto sobre primary */
--secondary
--background
--foreground
--card                 /* fondo de tarjetas */
--border
--muted-foreground     /* texto secundario/gris */
--input
--ring
--destructive
--font-sans            /* fuente base (heredada por body) */
--font-serif           /* fuente para títulos */
```

**Reglas inamovibles (Profesionalismo):**
- `font-family: var(--font-sans)` → NO declarar en CSS de página (se hereda del body)
- `font-size` base: `14px` (body en `main.css`)
- Títulos (`h1`, `h2`, `.hero-title`): `font-family: var(--font-serif)`
- Números/métricas: `font-family: 'JetBrains Mono'` — legible a distancia, sin ambigüedad
- **Cero** `text-transform: uppercase` — es decorativo, no funcional
- **Cero** `letter-spacing` decorativo
- **Cero** `box-shadow` decorativas — solo focus rings funcionales: `0 0 0 3px color-mix(in oklab, var(--primary) 24%, transparent 76%)`
- Transiciones: **`0.2s` a `0.3s` máximo** — solo donde cambia el estado, nunca decorativas
- Hover de botones: `filter: brightness(0.85) saturate(1.1)` — nunca transform ni shadow
- **Cero** animaciones de "entrada" o "salida" — son distracción, no función
- **Cero** gradientes decorativos — color plano con propósito

---

# TIPOGRAFÍA FUNCIONAL (No decorativa)

## Fuentes Base
- **Display / Títulos**: `Fraunces` (serif elegante, humanista) — establece autoridad, profesional
- **Body / Texto**: `Instrument Sans` (geometric pero cálida, diferente a Manrope) — legible, con carácter
- **Números / Métricas**: `JetBrains Mono` (monospace técnico) — sin ambigüedad `0/O`, `1/l`, legible a distancia

## Uso correcto
```css
/* Títulos de sección */
h1, h2, .hero-title, .section-title {
    font-family: var(--font-serif);  /* Fraunces */
}

/* Texto normal (heredado) */
body { font-family: var(--font-sans); }

/* Contadores / datos numéricos */
.metric-value, .defect-count, #totalGrains {
    font-family: 'JetBrains Mono';
    font-weight: 600;
}
```

## ¿Cuándo cambiar fuentes?
- **NUNCA** por "personalidad"
- **SÍ** por claridad (ej. números necesitan monospace para evitar ambigüedad)
- **SÍ** por jerarquía (títulos vs. body)

---

# CLASES COMPARTIDAS (main.css — NO duplicar en CSS de página)

## Hero / cabecera de página
```html
<header class="page-hero">
  <p class="kicker">Subtítulo en primary</p>
  <h1 class="hero-title">Título principal</h1>
  <p class="hero-description">Descripción breve.</p>
</header>
```
- `.page-hero` → tarjeta con borde, fondo `var(--card)`, border-radius 16px
- `.kicker` → 12px, `var(--primary)`, font-weight 700
- `.hero-title` → font-serif, clamp responsive
- `.hero-description` / `.info-text` → 14px, `var(--muted-foreground)`

## Botones
```html
<!-- Primario -->
<button class="btn btn-primary">Acción</button>

<!-- Secundario -->
<button class="btn btn-secondary">Cancelar</button>

<!-- Layout-only override (agregar al btn existente) -->
<button class="btn btn-primary flow-btn">...</button>
<a href="/ruta" class="btn btn-primary workflow-btn">Ir</a>
```
- `.flow-btn` y `.workflow-btn` son **solo** `width:100%; margin-top:auto;` — los estilos visuales vienen de `.btn .btn-primary/secondary`
- `.btn-export.pdf` → rojo, `.btn-export.excel` → verde, con `img` de 18px dentro

## Formularios
```html
<div class="field-group">
  <label>Campo</label>
  <input type="text" class="field-input" />
</div>
```

## Navegación activa
El script en `main.html` marca automáticamente `.nav-link.active` comparando `window.location.pathname`.  
Al agregar una nueva página, añadir el link en el `<nav>` de `main.html`:
```html
<a href="/nueva-ruta" class="nav-link">Nombre</a>
```

---

# PATRONES DE INTEGRACIÓN CON FASTAPI

## Fetch estándar (GET con query param)
```javascript
const res = await fetch(`/evaluacion/buscar?codigo=${encodeURIComponent(codigo)}`);
if (res.status === 404) { /* no encontrado */ return; }
if (!res.ok) throw new Error('Error de servidor');
const data = await res.json();
```

## Fetch POST/PATCH con JSON
```javascript
const res = await fetch(`/evaluacion/${id}/completar`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ total_defectos: 12, peso_bueno: 0.45 }),
});
if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Error');
}
const data = await res.json();
```

## Auth
JWT viaja en cookie httponly — el browser la adjunta automáticamente en cada `fetch()`. **No** gestionar tokens en JS.  
Si el backend devuelve 401/403, redirigir a `/auth/login`.

## Estados de carga en botones
```javascript
const btnOriginal = btn.innerHTML;
btn.disabled = true;
btn.innerHTML = '<span style="opacity:0.7">Cargando...</span>';
try {
    // await fetch(...)
} finally {
    btn.disabled = false;
    btn.innerHTML = btnOriginal;
}
```

## Manejo de errores con CoffeeModal
```javascript
// Disponible globalmente en todas las páginas (definido en main.html)
CoffeeModal.success('Operación exitosa.');
CoffeeModal.error('Descripción del error.', 'Título opcional');
CoffeeModal.warning('Atención...');
CoffeeModal.info('Información.');

// Confirmación async
const ok = await CoffeeModal.confirm({
    message: '¿Confirmar acción?',
    okText: 'Sí, continuar',
    cancelText: 'Cancelar',
});
if (!ok) return;
```
**Nunca** usar `alert()`, `confirm()` o `prompt()` del browser.

---

# ESTADOS DE UI

Toda sección que carga datos async debe tener tres estados visibles:

```html
<!-- Estado vacío/inicial -->
<div id="emptyState" class="reporte-state">
  <svg .../>
  <p>Mensaje orientativo</p>
</div>

<!-- Estado no encontrado / error -->
<div id="notFoundState" class="reporte-state" hidden>...</div>

<!-- Resultados -->
<div id="resultados" hidden>...</div>
```

```javascript
function mostrarEstado(state) {
    emptyState.hidden    = state !== 'empty';
    notFoundState.hidden = state !== 'notfound';
    resultados.hidden    = state !== 'results';
}
```

---

# INTEGRACIÓN MÓDULO ML (YOLO + CLASIFICACIÓN SCA)

## Streaming MJPEG en tiempo real

Página: `/monitoreo/{evaluacion_id}` integra:
- **`GET /video/stream`** → MJPEG (defectos en **ROJO 🔴**, 1280×720 @ 60fps)
- **`POST /video/iniciar`** → Inicia captura YOLO + ByteTrack
- **`POST /video/detener`** → Detiene procesamiento
- **`GET /lote/conteo`** → Conteo actual `{clase: cantidad, ...}`
- **`POST /lote/generar-reporte`** → Reporte final {grado, defectos, apto_specialty}
- **`POST /lote/resetear`** → Prepara nuevo lote

### Patrón de integración en templates

```javascript
// 1. Iniciar captura
fetch('/video/iniciar', {method: 'POST'})
  .then(r => r.json())
  .then(data => console.log('✅ Captura iniciada'))

// 2. Stream (automático en <img src="/video/stream">)
<img src="/video/stream" alt="YOLO Live" />

// 3. Obtener conteo en tiempo real (cada 1.5s)
const res = await fetch('/lote/conteo');
const {conteo, total_granos} = await res.json();
// conteo = {negro: 5, partido_maquina: 3, ...}

// 4. Generar reporte final
const res = await fetch('/lote/generar-reporte', {method: 'POST'});
const {grado, total_defectos, apto_specialty} = await res.json();
// grado = "Grado 1 (Specialty)" | "Grado 2" | "Grado 3"
```

### Colores de defectos en el stream

- **🔴 ROJO (0, 0, 255 BGR)** → Todos los defectos detectados por YOLO
- **🟡 AMARILLO (0, 255, 255 BGR)** → Estadísticas (contador, FPS)

### Tabla de grados SCA (3 solamente)

| Grado | Defectos Máx | Specialty |
|-------|:------------:|:---------:|
| **1** | 0–15 | ✅ Apto |
| **2** | 16–23 | ❌ No apto |
| **3** | 24–30 | ❌ No apto |

Documentación completa: [`docs/API_VIDEO_STREAMING.md`](../../docs/API_VIDEO_STREAMING.md)

---

# INTEGRACIÓN ARDUINO / SERIAL

El Arduino (`arduino/coffe_ren/logica_hardware.ino`) comunica por serial a 9600 baud.

**Comando clave para capturar `peso_bueno`:**
- Enviar: `PF\n`
- Respuesta JSON: `{"tipo":"peso_final","g":142.50,"kg":0.143}`

**Patrón de lectura en el frontend** (vía Web Serial API o backend proxy):
```javascript
// Al finalizar evaluación — extraer kg del JSON de Arduino
const line = /* línea recibida del serial */;
if (line.includes('"tipo":"peso_final"')) {
    const parsed = JSON.parse(line);
    pesoBuenoKg = parsed.kg;  // → enviar a PATCH /evaluacion/{id}/completar
}
```

**Flujo completo de finalización:**
1. Enviar `PF` al Arduino → esperar `{"tipo":"peso_final",...}`
2. `PATCH /evaluacion/{id}/completar` con `{ total_defectos, peso_bueno: kg }`
3. Respuesta incluye `codigo`, `pago`, `peso_por_qq`, `categoria`
4. Navegar a `/analisis/{evaluacion_id}`

---

# REGLAS CSS POR PÁGINA

## Qué va en `main.css` (compartido)
- Clases usadas en 2+ páginas: `.btn`, `.page-hero`, `.hero-title`, `.kicker`, `.info-text`, `.field-group`, `.nav-link`, `.glassmorphism`, etc.

## Qué va en `<pagina>.css` (específico)
- Layout único de esa página
- Componentes exclusivos (ej. `.analisis-toolbar`, `.reporte-search-card`)
- Overrides de tamaño/spacing para contexto específico

## Tamaños mínimos de fuente
- Mínimo: `12px` (nunca menos)
- Texto general: `14px`  
- Títulos: `clamp(1.1rem, 1.4vw, 1.45rem)` o mayor

## Responsive obligatorio
```css
@media (max-width: 768px) { /* tablet */ }
@media (max-width: 640px) { /* mobile */ }
```

---

# CHECKLIST ANTES DE ENTREGAR

### Revisión previa (obligatorio antes de escribir código)
- [ ] ¿Busqué la clase CSS en `main.css` antes de crearla?
- [ ] ¿Busqué el componente HTML en otros templates antes de inventar uno nuevo?
- [ ] ¿Busqué la función JS en otros templates antes de escribirla?
- [ ] ¿Verifiqué con `FastAPI-Architecture-Guardian` si el endpoint ya existe?

### HTML
- [ ] ¿Extiende `main.html` con `{% extends %}` y `{% block content %}`?
- [ ] ¿El `{% block style %}` tiene `?v=N` actualizado?
- [ ] ¿Rutas de imágenes usan `/static/icon/` (sin "s")?
- [ ] ¿Los `<img>` dentro de botones tienen `width`/`height` definidos en CSS?
- [ ] ¿Formularios usan `fetch()` + JSON, no submit tradicional?
- [ ] ¿Botones de carga muestran estado intermedio?
- [ ] ¿Errores van a `CoffeeModal.error()`, no a `alert()`?

### CSS
- [ ] ¿Hay `text-transform: uppercase`? → Eliminar
- [ ] ¿Hay `box-shadow` decorativa? → Eliminar
- [ ] ¿Se repite algo que ya está en `main.css`? → Eliminar duplicado
- [ ] ¿`font-family: var(--font-sans)` declarado? → Eliminar (hereda)
- [ ] ¿Fuentes < 12px? → Subir a 12px mínimo
- [ ] ¿Hover usa `transform` o `shadow`? → Cambiar a `filter: brightness()`

### Integración API
- [ ] ¿`encodeURIComponent()` en query params con input del usuario?
- [ ] ¿Se maneja el status 404 por separado del error genérico?
- [ ] ¿Se restaura el botón en `finally` aunque falle el fetch?
- [ ] ¿Las imágenes/iconos tienen ruta correcta `/static/icon/`?

---

---

# PATRONES DE NAVEGACIÓN CON FEEDBACK

## Cambios que requieren reinicio de sesión

Cuando un cambio se guarda exitosamente pero requiere que el usuario reinicie sesión para verlo reflejado (ej: cambio de datos personales, cambio de contraseña):

**❌ MAL:**
```javascript
// NO hacer redirect silencioso sin feedback
CoffeeModal.success('Datos actualizados.');
setTimeout(() => window.location.href = '/auth/logout', 2000);
```

**✅ BIEN:**
```javascript
// 1. Mostrar modal informativo
CoffeeModal.success('Datos actualizados correctamente.', 'Cambios guardados');

// 2. Luego de la lectura del usuario, hacer logout
setTimeout(() => {
    CoffeeModal.info(
        'Los cambios se reflejarán al reiniciar sesión. Se cerrará la sesión ahora.',
        'Por favor reinicie sesión'
    );
    
    // 3. Después del segundo modal, hacer logout
    setTimeout(() => {
        window.location.href = '/auth/logout';
    }, 2500);
}, 1500);
```

**Por qué:** El usuario necesita entender QUÉ pasó, POR QUÉ se está cerrando sesión, y QUÉ DEBE HACER DESPUÉS. No dejar cambios "invisibles" sin explicación.

---

# NAVEGACIÓN POR SECCIONES CON SIDEBAR

Patrón para páginas con navegación interna (ej. perfil, configuración):

```html
<!-- Sidebar con links -->
<aside class="perfil-sidebar">
  <nav class="perfil-nav">
    <a href="#account-control" class="perfil-nav-link active" data-section="account-control">
      <svg>...</svg>
      Control de cuenta
    </a>
    <a href="#personal-info" class="perfil-nav-link" data-section="personal-info">
      <!-- ... -->
    </a>
  </nav>
</aside>

<!-- Secciones con ids que coincidan con data-section -->
<main class="perfil-content">
  <section id="account-control" class="perfil-section">...</section>
  <section id="personal-info" class="perfil-section">...</section>
</main>
```

```javascript
// JavaScript para mostrar/ocultar secciones
document.querySelectorAll('.perfil-nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const section = link.getAttribute('data-section');

        // Remover active de todos
        document.querySelectorAll('.perfil-nav-link').forEach(l => l.classList.remove('active'));
        link.classList.add('active');

        // Ocultar todas las secciones
        document.querySelectorAll('.perfil-section').forEach(s => {
            s.style.display = 'none';
        });

        // Mostrar solo la seleccionada
        const selectedSection = document.getElementById(section);
        if (selectedSection) {
            selectedSection.style.display = 'flex';
        }
    });
});

// Inicializar mostrando solo la primera sección
document.querySelectorAll('.perfil-section').forEach((s, index) => {
    s.style.display = index === 0 ? 'flex' : 'none';
});
```

**CSS importante:**
```css
.perfil-section {
    display: none;  /* Ocultas por defecto */
    flex-direction: column;
}

.perfil-section:first-child {
    display: flex;  /* Primera visible al cargar */
}
```

**Ventajas:**
- Una única sección visible a la vez
- Transiciones limpias sin scroll excesivo
- Menos distracciones visuales
- UX profesional y moderna

---

# ANTIPATRONES A EVITAR

| ❌ Mal | ✅ Bien |
|---|---|
| `alert('Error')` | `CoffeeModal.error('...')` |
| `box-shadow: 0 4px 12px rgba(0,0,0,0.1)` | sin shadow decorativa |
| `text-transform: uppercase` | texto natural |
| `font-family: var(--font-sans)` en CSS de página | heredado, no declarar |
| `fetch('/ruta')` sin manejo de error | try/catch + CoffeeModal |
| `btn.textContent = 'Cargando'` sin restaurar | usar `btnOriginal` en finally |
| CSS idéntico en dos archivos | mover al `main.css` |
| `font-size: 10px` | mínimo `12px` |
| `/static/icons/` | `/static/icon/` (sin s) |
| Lógica de negocio en el template | solo presentación y fetch |
| Redirect sin feedback | Modal informativo → acción |
| Mostrar todas las secciones | Ocultar, mostrar solo seleccionada |
| Sidebars con gap grande | gap: 4px entre items |
| Validar contraseña en frontend solo | Usar `password_validate()` en backend |
| Layout centrado con espacio vacío en lados | Siempre `width: 100%; max-width: none !important` |
| Adaptar nombres de campos de API al copiar JS | Copiar EXACTAMENTE la función del template de referencia |

---

# REGLA CRÍTICA: LAYOUTS DEBEN OCUPAR TODA LA PANTALLA

**Por defecto, todo layout ocupa el 100% del ancho disponible.** Solo se limita el ancho si el usuario lo pide explícitamente.

## Problema conocido: `perfil.css` limita `.perfil-layout` a 1100px

`perfil.css` define:
```css
.perfil-layout { max-width: 1100px; margin: 0 auto; }
```

Cualquier página que extienda `perfil.css` **DEBE** sobrescribir esto en su propio CSS:

```css
/* ⚠️ OBLIGATORIO en páginas que usan perfil.css y necesitan full-width */
.perfil-container {
    width: 100%;
    max-width: none !important;
    margin: 0 !important;
}
.perfil-layout {
    max-width: none !important;
    margin: 0 !important;
    width: 100%;
}
.perfil-content {
    width: 100%;
    min-width: 0;
}
.perfil-section {
    width: 100%;
    box-sizing: border-box;
}
```

**Por qué `!important`:** `perfil.css` se carga primero. Sin `!important`, la especificidad CSS no garantiza que el override gane.

## Checklist de layout full-width

Antes de declarar un layout como "correcto", verificar en el navegador:
- [ ] ¿Hay background visible a los lados del contenido? → Hay un `max-width` o `margin: auto` sin sobrescribir
- [ ] ¿El contenido está centrado con espacio a los lados? → Buscar `margin: 0 auto` en el CSS padre
- [ ] ¿Busqué `max-width` en TODOS los CSS cargados, no solo el de la página?

---

# APIS DE UBIGEO Y PERSONA — ESTRUCTURA EXACTA

## Endpoints de ubigeo (campos reales)

```javascript
// GET /ubigeo/departamentos → [{ codigo: "15", nombre: "Lima" }, ...]
opt.value       = dep.codigo;   // "15"
opt.textContent = dep.nombre;   // "Lima"

// GET /ubigeo/provincias?departamento=15 → [{ codigo: "1501", nombre: "Lima" }, ...]
opt.value       = prov.codigo;  // "1501"
opt.textContent = prov.nombre;  // "Lima"

// GET /ubigeo/distritos?provincia=1501 → [{ codigo: "150103", nombre: "Ate" }, ...]
opt.value       = dist.codigo;  // "150103"
opt.textContent = dist.nombre;  // "Ate"
```

## Endpoint persona (campos reales)

```javascript
// GET /persona/consultar/{doc} → estructura PLANA, no anidada
// { encontrado, nombres, apellido_paterno, apellido_materno, sexo,
//   fecha_nacimiento, telefono, ubigeo_sunat, ubigeo, ... }

// ❌ MAL
input.value = data.persona.nombre;

// ✅ BIEN
input.value = data.nombres;
const ubigeo = data.ubigeo_sunat || data.ubigeo;
```

## Patrón de búsqueda con fallback RENIEC (copiar de nuevo_caficultor.html)

```javascript
async function consultarYAutollenar(documento) {
    // 1. BD local primero
    const respBD = await fetch(`/persona/consultar/${encodeURIComponent(documento)}`);
    if (respBD.ok) {
        const dataBD = await respBD.json();
        if (dataBD.encontrado) {
            await autollenarDesdeDni(dataBD);
            return;
        }
    }
    // 2. RENIEC solo si es DNI
    if (esTipoDNI()) {
        const respAPI = await fetch(`/dni/consultar/${encodeURIComponent(documento)}`);
        const dataAPI = await respAPI.json();
        if (dataAPI.encontrado) await autollenarDesdeDni(dataAPI);
    }
}

async function autollenarDesdeDni(data) {
    if (data.nombres)          nombreInput.value    = data.nombres;
    if (data.apellido_paterno) apePatInput.value    = data.apellido_paterno;
    if (data.apellido_materno) apeMatInput.value    = data.apellido_materno;
    if (data.sexo)             sexoInput.value      = data.sexo;
    if (data.fecha_nacimiento) fechaInput.value     = data.fecha_nacimiento;
    if (data.telefono)         telefonoInput.value  = data.telefono;

    const ubigeoCode = data.ubigeo_sunat || data.ubigeo;
    if (ubigeoCode && /^\d{6}$/.test(ubigeoCode)) {
        deptoInput.value = ubigeoCode.substring(0, 2);
        await cargarProvincias(ubigeoCode.substring(0, 2));
        provInput.value  = ubigeoCode.substring(0, 4);
        await cargarDistritos(ubigeoCode.substring(0, 4));
        distInput.value  = ubigeoCode;
    }
}
```
