# Movimiento e interacción en CoffeeRen

Referencia de la skill `frontend-coffeeren`. Adapta al proyecto las skills `emil-design-eng`,
`review-animations` y `mobile-native` de **Emil Kowalski** (MIT), más las reglas de movimiento
del modo *Operate* de **impeccable** (Apache 2.0). Se omitió lo específico de React, Framer Motion
y gestos de arrastre, que el proyecto no usa.

---

## 1. Tokens (definidos en `src/static/css/input.css`)

| Token | Valor | Uso |
|---|---|---|
| `--ease-out` | `cubic-bezier(0.23, 1, 0.32, 1)` | Entradas, salidas, respuesta a acciones |
| `--ease-in-out` | `cubic-bezier(0.77, 0, 0.175, 1)` | Algo que se desplaza dentro de la pantalla |
| `--dur-press` | `140ms` | `:active` de botones |
| `--dur-fast` | `180ms` | Hover, menús, cambios de color |
| `--dur-base` | `240ms` | Modales, paneles |

Usar siempre los tokens. No escribir curvas o duraciones sueltas.

---

## 2. Antes de animar algo, responder en orden

**1. ¿Debe animarse?** Según la frecuencia con que el usuario lo ve:

| Frecuencia | Decisión |
|---|---|
| Cientos de veces al día (atajos de teclado, cambio de pestaña interna) | Sin animación |
| Decenas de veces al día (hover, navegación de listas, inicio) | Mínima o ninguna |
| Ocasional (modales, menús, notificaciones) | Animación estándar |
| Rara (primera vez, confirmación de lote terminado) | Puede tener un detalle |

Nunca animar acciones iniciadas con el teclado.

**2. ¿Para qué?** Solo valen: indicar un cambio de estado, confirmar una acción (el botón se
hunde al presionarlo), mantener coherencia espacial (un menú sale de su disparador) o evitar un
salto brusco. "Se ve bonito" no es razón en una herramienta de trabajo.

**3. ¿Qué curva?**

- Entra o sale → `--ease-out`.
- Se mueve dentro de la pantalla → `--ease-in-out`.
- Hover o cambio de color → `ease`.
- Movimiento constante (spinner, barra de progreso) → `linear`.
- **Nunca `ease-in`** en interfaz: arranca lento justo cuando el usuario está mirando.
- **Sin rebote** (`cubic-bezier(0.34, 1.56, …)` y similares): un panel profesional es preciso.

**4. ¿Cuánto dura?**

| Elemento | Duración |
|---|---|
| Presión de botón | 100–160 ms |
| Tooltip, popover pequeño | 125–200 ms |
| Menú desplegable, select | 150–250 ms |
| Modal, panel lateral | 200–300 ms |

La interfaz se queda bajo 300 ms. **La salida es más rápida que la entrada** (CoffeeModal entra en
240 ms y sale en 150 ms).

---

## 3. Reglas de componentes

- **Botones que responden:** `transform: scale(0.97)` en `:active`. Ya está en `.btn`; cualquier
  elemento presionable nuevo hace lo mismo (entre 0.95 y 0.98).
- **Nunca desde `scale(0)`:** empezar en `scale(0.95)`–`scale(0.98)` con `opacity: 0`.
- **Menús desde su disparador:** `transform-origin` en la esquina del botón que los abre (el menú
  de usuario usa `top right`). Los modales son la excepción: se quedan centrados.
- **Transiciones antes que `@keyframes`** para todo lo que el usuario puede disparar rápido: una
  transición se puede interrumpir y retomar; un keyframe reinicia desde cero.
- **Propiedades explícitas:** `transition: opacity 180ms …, transform 180ms …`. Nunca
  `transition: all`.
- **Solo `transform` y `opacity`** para mover cosas. Animar `width`, `height`, `top`, `margin` o
  `padding` obliga a recalcular el layout. Excepción aceptada: barras de progreso con `scaleX`.
- **Visibilidad con retardo:** para ocultar con transición, `visibility` cambia al final
  (`visibility 0s linear var(--dur-fast)`) y vuelve a `0s` al abrir. Así el elemento no queda
  clicable mientras se desvanece.
- **Hover solo en dispositivos con puntero:** los efectos de hover que mueven o escalan van dentro
  de `@media (hover: hover) and (pointer: fine)`; en táctil el hover se queda "pegado".
- **Sin coreografías de carga de página.** Una herramienta se abre en la tarea. La entrada de
  `inicio` (`.reveal-up`, 300 ms) es lo máximo aceptable y respeta movimiento reducido.
- **Indicadores vivos:** el punto de "En vivo" (`.blink-dot`) y los spinners sí se animan en bucle:
  comunican estado.

---

## 4. Accesibilidad

- `main.css` reduce todas las transiciones a 1 ms con `prefers-reduced-motion: reduce`. Las
  animaciones de entrada propias de una página se desactivan en su CSS dentro del mismo media
  query. Movimiento reducido significa menos desplazamiento, no cero feedback: opacidad y color
  se mantienen.
- El anillo de foco usa `:focus-visible` (aparece con teclado, no al hacer clic). No usar
  `outline: none` sin un reemplazo visible.

---

## 5. Formato para revisar animaciones

Al revisar código de interfaz, reportar en una tabla:

| Antes | Después | Por qué |
|---|---|---|
| `transition: all 300ms` | `transition: transform 180ms var(--ease-out)` | Propiedades explícitas; `all` anima lo que no debe |
| `transform: scale(0)` | `transform: scale(0.96); opacity: 0` | Nada aparece de la nada |
| `ease-in` en un menú | `var(--ease-out)` | `ease-in` se siente lento al inicio |
| Botón sin `:active` | `transform: scale(0.97)` en `:active` | El botón debe responder al presionarlo |
| Modal con rebote | `var(--ease-out)`, 240 ms | Precisión, no juego |

## 6. Lista de revisión

| Problema | Corrección |
|---|---|
| `transition: all` | Listar las propiedades |
| Entrada desde `scale(0)` | `scale(0.95)` + `opacity: 0` |
| `ease-in` en interfaz | `var(--ease-out)` |
| Duración > 300 ms en interfaz | 150–250 ms |
| Hover que mueve sin media query | `@media (hover: hover) and (pointer: fine)` |
| Keyframes en algo que se dispara seguido | Transición |
| Entrada y salida con la misma duración | Salida más rápida |
| Animación en acción de teclado | Quitarla |
| Animación sin respaldo para movimiento reducido | Agregar el media query |
