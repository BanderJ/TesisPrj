---
name: frontend-coffeeren
description: Frontend de CoffeeRen — plantillas Jinja2, sistema de diseño CSS (tokens, estados, movimiento), integración con FastAPI, criterio visual para una herramienta de trabajo (sin estética de IA) y consumo de los endpoints de video y Arduino. Usar siempre al crear o modificar archivos en src/templates/, src/static/css/ o src/static/js/, al diseñar o revisar una pantalla o componente, o al auditar, pulir o animar la interfaz.
---

# Frontend de CoffeeRen

Crear y mantener las interfaces de CoffeeRen: plantillas Jinja2 bien estructuradas, CSS sin
duplicación, integración correcta con FastAPI y una experiencia **sobria, precisa y confiable**.

Si necesitas saber qué endpoints existen o qué campos devuelven, revisa `src/routes/` o consulta
al agente `fastapi-architecture-guardian`.

## Referencias de esta skill (leer según la tarea)

| Tarea | Leer |
|---|---|
| Cualquier cambio visual, pulido o auditoría de una pantalla | `referencias/calidad-visual.md` |
| Transiciones, animaciones, hover, foco, modales, menús | `referencias/movimiento.md` |

Ambas adaptan al proyecto tres colecciones externas (ver "Fuentes" al final).

---

# 1. Criterio de diseño

CoffeeRen es una **herramienta de trabajo**, no una página de marketing. El usuario entra a
completar una tarea; la interfaz debe desaparecer en ella.

- **Cada cambio visual resuelve un problema concreto.** Nada decorativo.
- **Familiaridad ganada:** controles estándar, navegación estándar, el mismo componente en todas
  las pantallas.
- **Jerarquía clara:** el usuario sabe qué mirar primero y qué hacer después.
- **Color con significado:** el verde marca acción y selección; rojo y ámbar solo cuando hay un
  defecto, un error o una alerta.
- **Movimiento que informa:** confirma una acción o un cambio de estado. Rápido (≤ 300 ms), sin
  rebote, con salida más rápida que la entrada.
- **Refinar preserva:** "mejorar" una pantalla conserva su identidad, comportamiento y textos. Si
  el concepto está mal, se propone un rediseño; no se cuela dentro de un pulido.
- **No inventar textos factuales ni reglas de negocio.** Preguntar antes.

Rechazos frecuentes (detalle en `referencias/calidad-visual.md`): degradados decorativos, texto
con degradado, vidrio como adorno, tarjetas dentro de tarjetas, emojis como iconos, colores de
estado en hex suelto, sombras duras desplazadas, monospace como disfraz, modales para lo que
puede resolverse en línea, signos de exclamación en mensajes.

---

# 2. Regla de oro: revisar antes de crear

Antes de escribir CSS, HTML o JS:

1. **Clasificar:** ¿es presentación (CSS), estructura (HTML) o lógica (JS)?
2. **Buscar en `main.css`:** `Grep "nombre-clase" src/static/css/main.css`.
   - Existe y cumple → usarla. Nunca duplicar.
   - Existe pero necesita un ajuste menor → override mínimo en `<pagina>.css`
     (`.pagina .clase { ... }`).
   - No existe → paso 3.
3. **¿Se usa en 2 o más páginas?** Sí → `main.css`. No → `<pagina>.css`.
4. **Buscar el componente HTML** en `src/templates/`. Estructura idéntica → mismas clases.
   Similar → clase base + modificador (`.card` + `.card--wide`).
5. **Buscar la función JS** en `src/static/js/`. Idéntica → extraer a un archivo compartido.
   Similar → parametrizar la existente.
6. **Buscar el endpoint** en `src/routes/`. Existe → consumirlo tal cual. No existe → pedirlo con
   la skill `fastapi-architecture`.

| Clase | Ubicación | Razón |
|---|---|---|
| `.btn`, `.btn-primary`, `.card`, `.page-hero` | `main.css` | Todas las páginas |
| `.feed-card`, `.live-indicator` | `main.css` | `/monitoreo` y `/test` |
| `.cm-*` (CoffeeModal) | `main.css` | Modal global |
| `.monitoreo-feed-stats`, `.defect-track` | `monitoreo.css` | Solo `/monitoreo` |
| `.analisis-toolbar` | `analisis.css` | `/analisis` y `/reporte` (en reporte, el buscador va junto al título: `reporte.css`) |

---

# 3. Estructura de páginas

```html
{% extends "main.html" %}

{% block style %}
<link rel="stylesheet" href="/static/css/<pagina>.css">
{% endblock %}

{% block content %}
<!-- solo HTML -->
{% endblock %}

{% block script %}
<script>const EVALUACION_ID = '{{ evaluacion_id }}';</script>  <!-- solo si hay variables Jinja2 -->
<script src="/static/js/<pagina>.js"></script>
{% endblock %}
```

- Nunca repetir header, nav, footer, modales ni scripts de `main.html`.
- Sin `?v=N`: `main.py` sirve los estáticos con `Cache-Control: no-cache`.
- Sin estilos en línea salvo valores calculados por JS. Los estilos van al CSS.
- Orden de carga: `http.js` y `validators.js` en `<head>`; `main.js` al final del `<body>`; luego
  `{% block script %}`.
- **Excepción `login.html`:** no extiende `main.html`; carga `login.css` y `login.js` directo.
- Al agregar una página al menú, añadir el enlace en el `<nav>` de `main.html`
  (`<a href="/ruta" class="nav-link">Nombre</a>`); `main.js` marca el activo. Si la página es
  solo para Gerente o Administrador, el enlace va dentro de
  `{% if user and user.tipo_personal_id in [2, 3] %}` **y** la ruta usa
  `Depends(require_admin_o_gerente)`: ocultar el enlace no es control de acceso.

---

# 4. Sistema de diseño

## 4.1 Tokens (`src/static/css/input.css`, compilado a `tailwind.css`)

Tras editar `input.css`, recompilar:
`./tailwindcss-windows-x64.exe -i src/static/css/input.css -o src/static/css/tailwind.css`.
Tailwind solo escanea `src/templates` y `src/static/js` (`@source` en `input.css`).

| Grupo | Tokens |
|---|---|
| Base | `--background`, `--foreground`, `--card`, `--border`, `--input`, `--ring`, `--muted`, `--muted-foreground` |
| Estructura | `--canvas` (lienzo cálido de todas las pantallas), `--shell` / `--shell-foreground` / `--shell-muted` (cabecera verde bosque) |
| Marca | `--primary` (verde bosque), `--primary-foreground`, `--secondary` (marrón café), `--accent` (miel) |
| Estado | `--success`, `--success-strong`, `--danger`, `--danger-strong`, `--warning`, `--info`, `--info-strong`, `--destructive` |
| Movimiento | `--ease-out`, `--ease-in-out`, `--dur-press` (140 ms), `--dur-fast` (180 ms), `--dur-base` (240 ms) |

- Los tokens de estado tienen variantes más luminosas en `.dark`. Las `-strong` sirven para texto
  sobre un fondo teñido del mismo tono.
- Fondos teñidos: `color-mix(in oklab, var(--success) 12%, transparent 88%)`.
- **Nunca** escribir `#16a34a`, `#dc2626`, `#d97706` o `#2563eb` en un CSS de página.

## 4.2 Tipografía

- Toda la interfaz usa `var(--font-sans)` (hoy `system-ui`), heredada del `body`. No declararla en
  CSS de página.
- **Nada de serif en elementos de interfaz** (inputs, botones, encabezados de tarjeta): el usuario
  lo pidió expresamente. `--font-serif` existe para títulos de página y marca, y hoy también
  resuelve a `system-ui`.
- Cuerpo `14px`, mínimo `12px`. Títulos de página `clamp(1.15rem, 1.4vw, 1.45rem)`.
- Pesos: 400 texto, 500 navegación y etiquetas secundarias, 600 etiquetas y botones, 700 títulos.
- Cifras: `font-variant-numeric: tabular-nums` (global en `table`, `input`, `output`; agregarlo en
  contadores y métricas).
- Monospace solo para códigos e identificadores (ej. códigos EVA). `JetBrains Mono` **no se carga**;
  cae al monospace del sistema.
- Mayúsculas sostenidas: evitarlas. Se toleran solo en etiquetas cortas de datos (≤ 12 px) con
  `letter-spacing` leve, como las que ya existen en análisis y monitoreo.
- Títulos con `text-wrap: balance`; mensajes con `text-wrap: pretty`.

## 4.3 Superficies, foco y profundidad

- **Estructura de pantalla:** cabecera fija en `--shell` con texto crema; el enlace activo es una
  pastilla crema con texto verde. Debajo, el lienzo `--canvas` liso (sin fotos de fondo). El
  título de página va directo sobre el lienzo (`.page-hero` no es tarjeta); el trabajo va en
  tarjetas blancas.
- Tarjetas: borde de 1 px (`.card`), radio 12 px, sin sombra. **Nunca tarjetas dentro de
  tarjetas:** dentro de una tarjeta, separar con divisores (`border-top`/`border-right`) o con una
  sola superficie dividida (ver los indicadores de inicio y monitoreo).
- Sombra solo en capas elevadas (modal, menú), con desplazamiento y desenfoque.
- Foco: anillo global con `:focus-visible` (`outline: 2px solid var(--ring)`). En `.btn`, anillo
  `0 0 0 3px color-mix(in oklab, var(--primary) 24%, transparent 76%)`. Inputs mantienen su
  anillo en `:focus` (al hacer clic también es útil).
- Selección de texto, scrollbar y `accent-color` ya toman la paleta (`main.css`).

## 4.4 Interacción y movimiento (detalle en `referencias/movimiento.md`)

- Hover de botones: `filter: brightness(0.85) saturate(1.1)` (primario) o tinte del primario
  (secundario).
- Presión: `transform: scale(0.97)` en `:active` (ya en `.btn`).
- Transiciones con propiedades explícitas y tokens. Nunca `transition: all`.
- Entradas con `--ease-out`; nunca `ease-in`; sin curvas con rebote.
- `prefers-reduced-motion` ya reduce todas las transiciones en `main.css`; las animaciones de
  entrada de una página se desactivan en su propio CSS.
- Spinners: `animation: spin … linear infinite` (keyframes `spin` en `main.css`).

---

# 5. Clases compartidas (`main.css`)

## Cabecera de página
```html
<header class="page-hero">
  <h1 class="hero-title">Título principal</h1>
  <p class="hero-description">Descripción breve.</p>
</header>
```
Sin tarjeta: el título (1.6rem) va sobre el lienzo. Todas las páginas usan esta misma cabecera.

## Botones
```html
<button class="btn btn-primary">Guardar evaluación</button>
<button class="btn btn-secondary">Cancelar</button>
<!-- Botón a todo el ancho al pie de una tarjeta: .flow-btn (caficultor.css), solo ancho y margen -->
```
- `.btn-export.pdf` (rojo) y `.btn-export.excel` (verde), con `img` de 18 px.
- El texto del botón nombra la acción, no "Aceptar".

## Formularios
```html
<div class="form-row form-row--2">
  <div class="field-group">
    <label for="numSacos">Número de sacos</label>
    <input id="numSacos" type="number">
    <p class="helper-text" id="numSacosHint" aria-live="polite"></p>
  </div>
  <div class="field-group">...</div>
</div>
<div class="form-actions">...</div>
```
- **Dos campos por fila** (`form-row--2`); pasa a una columna bajo 768 px.
- Validación en vivo (`input`/`blur`) con `CoffeeValidators` (`validators.js`) y el patrón
  `validarInline(...)` de `registro.js`; el modal al enviar es la última defensa.
- Contraseña: envolver en `.password-wrapper` con `.password-toggle-btn`; `main.js` lo conecta.

## Menú de usuario
`.dropdown-item` para opciones normales; `.dropdown-item--danger` solo para la acción destructiva
(cerrar sesión).

## Layout con barra lateral (perfil, cooperativa)
`.perfil-container` > `.perfil-layout` > `.perfil-sidebar` + `.perfil-content` >
`.perfil-section`. Una sola sección visible a la vez; los enlaces llevan `data-section` igual al
`id` de la sección.

---

# 6. Integración con FastAPI

## Fetch y errores
```javascript
const res = await fetch(`/evaluacion/${id}/completar`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ total_defectos, peso_bueno }),
});
if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo completar la evaluación.'));
const data = await res.json();
```
- `CoffeeHttp.mensajeError()` (`http.js`) es el único extractor de errores: el texto lo decide el
  backend; el frontend solo da un respaldo.
- `encodeURIComponent()` en todo query param con entrada del usuario.
- 404 se maneja aparte del error genérico cuando significa "no encontrado".
- Auth: el JWT viaja en cookie httponly; no se manejan tokens en JS. Ante 401/403, ir a
  `/auth/login`.

## Estado de carga en botones
```javascript
const textoOriginal = btn.innerHTML;
btn.disabled = true;
btn.textContent = 'Guardando…';
try {
    // await fetch(...)
} finally {
    btn.disabled = false;
    btn.innerHTML = textoOriginal;
}
```

## CoffeeModal (global, definido en `main.js`, estilos `.cm-*` en `main.css`)
```javascript
CoffeeModal.success('La evaluación se registró correctamente.');
CoffeeModal.error(mensaje, 'Título opcional');
CoffeeModal.warning('...');
CoffeeModal.info('...');

const ok = await CoffeeModal.confirm({
    message: 'Se descartará el conteo actual del lote.',
    okText: 'Descartar',
    cancelText: 'Volver',
});
if (!ok) return;
```
- Nunca `alert()`, `confirm()` ni `prompt()`.
- El tipo se aplica con `data-type` en el overlay; no tocar estilos del modal desde JS.
- Si un cambio exige reiniciar sesión, primero un modal que explique qué pasó y qué hacer, luego
  el `logout`. Nunca un redirect silencioso.

## Estados de una sección asíncrona
```javascript
function mostrarEstado(estado) {
    emptyState.hidden    = estado !== 'empty';
    notFoundState.hidden = estado !== 'notfound';
    resultados.hidden    = estado !== 'results';
}
```
El estado vacío orienta ("Ingrese un código EVA para ver el reporte"), no solo dice "Sin datos".

---

# 7. El frontend no toma decisiones de negocio

El frontend presenta; el backend decide. Si el template necesita saber qué es un defecto, qué
clases existen, qué umbral aplica o cómo se calcula un total, **eso debe venir calculado en la
respuesta**.

```javascript
// Mal: el frontend conoce las clases del modelo o aplica umbrales
const CLASES_SANAS = new Set(['verde', 'sano']);
const conDescuento = humedad > 12;

// Bien: el backend ya lo calculó
const data = await fetch('/video/lote/conteo').then(r => r.json());
totalDefectosEl.textContent = data.total_defectos;
totalSanosEl.textContent    = data.total_sanos;
```

Prueba: **si cambiar el nombre de una clase del modelo obliga a tocar un template, hay lógica de
negocio en el frontend.** La corrección va en el service, no en el template.

---

# 8. Módulo de visión y monitoreo

Página `/monitoreo/{evaluacion_id}`:

| Endpoint | Uso |
|---|---|
| `GET /video/stream` / `GET /video/frame` | MJPEG / último JPEG anotado (defecto rojo, verde verde, desconocido azul; 1280 px de ancho) |
| `POST /video/iniciar` / `POST /video/detener` | Inicia o detiene YOLO + ByteTrack |
| `GET /video/lote/conteo` | `total_defectos`, `total_sanos`, `total_desconocidos`, `segundos_sin_deteccion`, … |
| `GET /video/eventos?desde=<seq>` | Bitácora del monitoreo (render compartido en `eventos-monitoreo.js`) |
| `GET /video/status` | Estado, `evaluacion_id` dueña del lote, cámara desconectada |
| `POST /video/lote/generar-reporte` | `{total_granos_analizados, total_defectos, detalle_por_clase, resumen}` |
| `POST /video/lote/resetear` | Prepara un lote nuevo |

El grado SCA no se muestra: depende del tipo de defecto y el modelo actual solo distingue
defecto/verde. No agregar grado, Specialty ni categoría en ninguna pantalla.

Detalle: `docs/API_VIDEO_STREAMING.md`.

---

# 9. Arduino

El puerto serie lo maneja **solo el backend** (`src/utilities/arduino_serial.py`, 9600 baud). El
frontend consume HTTP:

| Endpoint | Respuesta |
|---|---|
| `GET /arduino/estado` | `{ listo, distancia, conectado, mensaje }` |
| `GET /arduino/peso` | `{ peso, conectado, mensaje }` (`peso = null`: la báscula está retirada) |
| `POST /arduino/motor/iniciar` / `POST /arduino/motor/detener` | `{ activo, mensaje }` (faja) |

`peso_bueno` es **ingreso manual** en gramos enteros (balanza externa), en el modal de finalización
del monitoreo o en `/analisis` como respaldo. Validación compartida:
`CoffeeValidators.pesoBueno(valor, maxTrillado)`.

Flujo de finalización:
1. `PATCH /evaluacion/{id}/finalizar` → asigna el código EVA.
2. El evaluador ingresa el peso bueno.
3. `PATCH /evaluacion/{id}/completar` con `{ total_defectos, peso_bueno }` → `codigo`,
   `factor_rendimiento`, `pago`, `pago_base`, `bono_socio`, `peso_por_qq`, `precio`, `rango`.
4. Navegar a `/analisis/{evaluacion_id}`.

---

# 10. Layout a todo el ancho

Por defecto **todo layout ocupa el 100 % del ancho disponible**; solo se limita si el usuario lo
pide. Antes de dar un layout por bueno, revisar en el navegador que no quede fondo visible a los
lados y buscar `max-width` / `margin: 0 auto` en **todos** los CSS cargados (`main.css`,
`perfil.css` y el de la página). No usar la clase suelta `container`: Tailwind la genera con
`max-width` por breakpoint.

Responsive obligatorio: `@media (max-width: 768px)` (tablet) y `@media (max-width: 640px)` (móvil).

---

# 11. APIs de ubigeo y persona (campos exactos)

```javascript
// GET /ubigeo/departamentos            → [{ codigo: "15", nombre: "Lima" }, ...]
// GET /ubigeo/provincias?departamento=15 → [{ codigo: "1501", nombre: "Lima" }, ...]
// GET /ubigeo/distritos?provincia=1501   → [{ codigo: "150103", nombre: "Ate" }, ...]
opt.value = item.codigo;
opt.textContent = item.nombre;

// GET /persona/consultar/{doc} → estructura PLANA
// { encontrado, nombres, apellido_paterno, apellido_materno, sexo,
//   fecha_nacimiento, telefono, ubigeo_sunat, ubigeo, ... }
input.value = data.nombres;                    // no data.persona.nombre
const ubigeo = data.ubigeo_sunat || data.ubigeo;
```

Búsqueda con respaldo RENIEC (patrón de `caficultor.js`): primero `/persona/consultar/{doc}` en la
BD local; si no se encuentra y es DNI, `/dni/consultar/{doc}`. Al replicar esta lógica en otra
página, **copiar las funciones tal cual** y cambiar solo los IDs del DOM.

---

# 12. Antipatrones

| Mal | Bien |
|---|---|
| `alert('Error')` | `CoffeeModal.error(...)` |
| Reescribir el texto de error del backend | `CoffeeHttp.mensajeError(res, respaldo)` |
| `#dc2626` en un CSS de página | `var(--danger)` |
| `transition: all 0.3s ease` | `transition: opacity var(--dur-fast) var(--ease-out), ...` |
| Curva con rebote, `ease-in`, entrada desde `scale(0)` | `var(--ease-out)`, `scale(0.96)` + `opacity: 0` |
| `outline: none` sin reemplazo | `:focus-visible` con anillo |
| Estilos en línea en el HTML | Clases en el CSS de la página o `main.css` |
| `font-family` declarado en CSS de página | Heredado del `body` |
| Serif en inputs, botones o tarjetas | `var(--font-sans)` |
| `font-size: 10px` | Mínimo `12px` |
| `/static/icons/` | `/static/icon/` |
| Lógica de negocio o nombres de clases del modelo en el template | Totales calculados por el backend |
| Redirect sin explicación | Modal informativo, luego la acción |
| Layout centrado con fondo visible a los lados | `width: 100%; max-width: none` |
| Adaptar nombres de campos al copiar JS | Copiar la función exacta |
| Emojis en interfaz, código o comentarios | Iconos SVG; texto sobrio |

---

# 13. Lista de control antes de entregar

### Antes de escribir
- [ ] Busqué la clase en `main.css`, el componente en `src/templates/` y la función en
      `src/static/js/`.
- [ ] Verifiqué que el endpoint existe en `src/routes/`.
- [ ] Leí `referencias/calidad-visual.md` (y `referencias/movimiento.md` si hay transiciones).

### HTML
- [ ] Extiende `main.html`; JS en `{% block script %}`; solo variables Jinja2 inline.
- [ ] Sin estilos en línea nuevos; iconos SVG con un solo grosor de trazo; `alt` útil.
- [ ] `label for` en cada campo; formularios de dos columnas.

### CSS
- [ ] Sin hex de estado, sin `transition: all`, sin `ease-in`, sin rebote.
- [ ] Nada repetido de `main.css`; sin `font-family` de página; fuentes ≥ 12 px.
- [ ] Hover, `:active`, `:focus-visible`, deshabilitado, cargando y error cubiertos.
- [ ] Revisado en 1280 px y ≤ 640 px, en claro y oscuro.

### JS e integración
- [ ] Errores con `CoffeeHttp.mensajeError` + `CoffeeModal.error`.
- [ ] Botón restaurado en `finally`; `encodeURIComponent` en query params.
- [ ] Ninguna regla de negocio en el frontend.

### Cierre
- [ ] Auditoría con `architecture-compliance-auditor` (cambios en `src/templates` o `src/static`).
- [ ] Línea en `docs/guia/05-historial-de-cambios.md` si el cambio es relevante.

---

# Fuentes

Las reglas de criterio visual, calidad y movimiento adaptan, traducen y recortan para CoffeeRen:

- **impeccable** — Paul Bakaus, Apache 2.0, https://github.com/pbakaus/impeccable. Modo *Operate*,
  "craft floor", flujo de `polish` y `audit`.
- **emilkowalski/skills** — Emil Kowalski, MIT, https://github.com/emilkowalski/skills.
  `emil-design-eng`, `review-animations`, `mobile-native`.
- **taste-skill** — Leonxlnx, MIT, https://github.com/Leonxlnx/taste-skill. Auditoría de
  `redesign-skill`. La skill principal (`design-taste-frontend`) no se usó: está pensada para
  landing pages y portafolios, y excluye paneles y tablas de datos.
