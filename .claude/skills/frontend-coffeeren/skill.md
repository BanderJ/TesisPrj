---
id: frontend-coffeeren
name: frontend-coffeeren
description: Frontend expert para CoffeeRen — templates Jinja2, design system CSS, integración FastAPI, UX/UI y Arduino serial.
---

# MISIÓN
Crear y mantener interfaces de usuario en CoffeeRen: templates Jinja2 bien estructurados, CSS limpio sin duplicación, integración correcta con las APIs FastAPI y experiencia de usuario coherente y profesional.

Antes de cualquier tarea de frontend **consulta el agente `FastAPI-Architecture-Guardian`** si necesitas saber qué endpoints existen, qué campos retornan o cómo están construidas las rutas.

---

# REGLA DE ORO: REVISAR ANTES DE CREAR

**Antes de escribir cualquier CSS, componente HTML o función JS**, ejecuta este flujo obligatorio:

## 1. ¿Ya existe en `main.css`?
```
Grep "nombre-clase" en src/static/css/main.css
```
- **Sí existe y cumple** → usarla directamente, sin copiar ni redefinir.
- **Sí existe pero necesita ajuste menor** → agregar un override mínimo en el CSS de la página, nunca duplicar la regla completa.
- **No existe y se usará en 2+ páginas** → crearla en `main.css`, no en el CSS de página.
- **No existe y es exclusiva de una página** → crearla en `<pagina>.css`.

## 2. ¿Ya existe el componente HTML en otro template?
```
Grep "clase-o-id-del-componente" en src/templates/
```
- Misma estructura visual → reutilizar las mismas clases CSS, no inventar nuevas.
- Similar pero con variación → parametrizar con una clase modificadora (ej. `analisis-section--wide`), nunca duplicar el bloque entero.

## 3. ¿Ya existe la función JS?
```
Grep "nombreFuncion\|comportamiento" en src/templates/
```
- Función idéntica en otra página → extraer a un archivo JS compartido en `/static/js/`.
- Lógica similar → parametrizar la función existente antes de crear una nueva.

## 4. ¿Ya existe el endpoint en el backend?
Consultar al agente `FastAPI-Architecture-Guardian` o hacer:
```
Grep "router\|@.*_router" en src/routes/
```
- **Existe** → consumirlo tal cual, sin crear uno nuevo.
- **No existe** → solicitarlo al skill `fastapi-architecture` siguiendo la arquitectura de capas.

## Resumen del flujo
```
¿Existe? → Reutilizar
¿Casi igual? → Parametrizar / override mínimo
¿No existe y es compartido? → Crear en main.css o /static/js/
¿No existe y es exclusivo? → Crear en <pagina>.css o inline en el template
```

**Nunca** crear algo nuevo sin haber buscado primero. La duplicación es el enemigo principal de la calidad.

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

**Reglas inamovibles:**
- `font-family: var(--font-sans)` → NO declarar en CSS de página (se hereda del body)
- `font-size` base: `14px` (body en `main.css`)
- Títulos (`h1`, `h2`, `.hero-title`): `font-family: var(--font-serif)`
- **Cero** `text-transform: uppercase` ni `letter-spacing` decorativo
- **Cero** `box-shadow` decorativas — solo focus rings: `0 0 0 3px color-mix(in oklab, var(--primary) 24%, transparent 76%)`
- Hover de botones: `filter: brightness(0.85) saturate(1.1)` — nunca transform ni shadow

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
