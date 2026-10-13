# Calidad visual de CoffeeRen

Referencia de la skill `frontend-coffeeren`. Léela antes de cualquier cambio visual, incluso uno
pequeño. Adapta al proyecto el "craft floor" y el modo *Operate* de **impeccable**
(Paul Bakaus, Apache 2.0) y la auditoría de **redesign-skill** de **taste-skill** (Leonxlnx, MIT).
Se descartó lo que solo aplica a landing pages o sitios de marketing.

---

## 1. Qué tipo de interfaz es CoffeeRen

CoffeeRen es una **herramienta de trabajo** (modo *Operate*): el evaluador, el gerente y el
administrador entran a completar una tarea (registrar una muestra, monitorear un lote, revisar
un reporte, configurar precios). Consecuencias:

- **La herramienta desaparece en la tarea.** Un usuario que conoce sistemas parecidos debe
  confiar en la pantalla de inmediato, sin detenerse en componentes "raros".
- **Familiaridad antes que sorpresa.** Navegación estándar, controles estándar (botones,
  inputs, selects, tablas, pestañas). No inventar controles por estilo.
- **Densidad permitida.** Tablas con muchas filas y paneles con muchas etiquetas son correctos
  cuando el usuario necesita los datos.
- **Consistencia entre pantallas.** Si el botón "Guardar" se ve distinto en dos páginas, una de
  las dos está mal.
- **La identidad vive en los detalles:** el verde bosque, el marrón café, el cuidado en estados
  y foco. No en decoración.

### Refinar no es rediseñar

Un pedido de "mejorar" una pantalla es **refinamiento**: se conserva la identidad visual, el
comportamiento, los textos y todo lo que está fuera del alcance. Si el concepto de la pantalla
está mal, se dice y se propone un rediseño; no se mete un rediseño a escondidas dentro de un
"pulido". Antes de cambiar un texto factual o agregar una afirmación, preguntar.

---

## 2. Piso de calidad (verificar en el resultado, no como intención)

- **Contraste:** texto normal y placeholder ≥ 4.5:1; texto grande ≥ 3:1. Sobre fondos de color,
  el texto secundario se tiñe del mismo tono, nunca gris neutro.
- **Profundidad:** las sombras tienen desplazamiento y desenfoque suave. Un halo de color sin
  desplazamiento es decoración. Las tarjetas se separan con borde, no con sombra; la sombra queda
  para capas elevadas (modal, menú desplegable).
- **Espaciado:** grupos relacionados juntos, grupos distintos bien separados, más espacio sobre
  un título que debajo.
- **Tipografía:** prosa con 65–75 caracteres por línea como máximo; títulos con
  `text-wrap: balance`; párrafos de mensaje con `text-wrap: pretty`. Escala fija en `rem`/`px`
  para la interfaz (no tamaños fluidos que encogen en paneles). Pasos de escala de 1.125–1.2.
- **Cifras:** columnas numéricas con `font-variant-numeric: tabular-nums` (ya global en
  `table`, `input`, `output`). Agregarlo a cualquier métrica o contador fuera de esos elementos.
- **Estados:** todo control interactivo tiene default, hover, foco, activo, deshabilitado,
  cargando y error. No entregar con la mitad.
- **Superficies del navegador:** selección de texto, scrollbar, anillo de foco y controles
  nativos (`accent-color`) toman la paleta. Ya están definidos en `main.css`; no volver a los
  valores por defecto.
- **Texto:** en el idioma del producto. Los botones nombran su acción ("Guardar evaluación", no
  "Aceptar"). Los errores dicen qué pasó y cómo seguir. Sin signos de exclamación en mensajes de
  éxito, sin "¡Ups!".
- **Cobertura:** todo lo que pidió el usuario está presente y se encuentra en segundos.

---

## 3. Lo que no se hace (salvo que el usuario lo pida explícitamente)

Estructura de página:

- Tarjetas iguales de icono + título + texto como estructura de la página. Nunca tarjetas
  dentro de tarjetas.
- La plantilla de "métrica héroe": número gigante, etiqueta chica, estadísticas de relleno.
- Números de sección (01 / 02 / 03) cuando la secuencia no le dice nada al usuario.
- Un modal para algo que no necesita interrumpir ni proteger el foco. Primero agotar opciones en
  línea (edición en la tabla, panel expandible).

Superficies:

- Texto con degradado. El énfasis sale del peso o del tamaño.
- Vidrio y desenfoque como decoración.
- Borde de color de más de 1 px a la izquierda o derecha de tarjetas, filas o alertas.
- Sombras duras desplazadas (`box-shadow: 4px 4px 0`).
- Sparklines, anillos de progreso o rectángulos con sombra ocupando el lugar del contenido.
- Monospace como disfraz "técnico". Se usa solo para códigos, identificadores y medidas.
- Emojis o caracteres Unicode como iconos. Los iconos son SVG, con un mismo grosor de trazo.
- Colores sueltos en hex para estados. Se usan los tokens `--success`, `--danger`,
  `--warning`, `--info` (y sus variantes `-strong` para texto sobre fondo teñido).

---

## 4. Color en una herramienta de trabajo

- **Restringido por defecto.** El acento (`--primary`) marca acciones principales, selección
  actual e indicadores de estado. No decora.
- **Vocabulario de estado estable:** hover, foco, activo, deshabilitado, seleccionado, cargando,
  error, advertencia, éxito, info. Cada uno con el mismo tratamiento en todas las páginas.
- **Un solo acento cálido** (`--secondary`, marrón café) además del verde. No agregar morados,
  azules eléctricos ni degradados.
- **Rojo y ámbar solo cuando significan algo** (defecto, error, alerta), nunca en estados
  inactivos.
- **Modo oscuro:** los tokens de estado ya tienen variantes más luminosas en `.dark`. Sobre un
  relleno de color claro en oscuro, el texto va oscuro (como hace `--primary-foreground`).

---

## 5. Componentes

- Mismo botón, mismo input, mismo icono en todas las pantallas. Reutilizar `.btn`, `.field-group`,
  `.card`, `.page-hero` de `main.css`.
- **Carga:** el botón que dispara la acción muestra su estado (deshabilitado + texto "Guardando…")
  y se restaura en `finally`. Para secciones que cargan datos, un esqueleto con la forma del
  contenido es mejor que un spinner en el centro.
- **Vacíos:** un estado vacío explica qué hacer ("Ingrese un código EVA para ver el reporte"), no
  solo "Sin datos".
- **Capas que escapan del contenedor:** un menú absoluto dentro de un ancestro con
  `overflow: hidden/auto` queda recortado; usar `position: fixed` o `<dialog>`.
- **Navegación:** el enlace de la página actual se marca (`.nav-link.active`, lo hace `main.js`).
  Toda pantalla tiene un camino de regreso.

---

## 6. Auditoría rápida de una pantalla existente

Recorrer en este orden y anotar cada hallazgo antes de tocar código:

1. **Tareas rotas o bloqueadas**, datos que se pierden, estados engañosos, caminos inaccesibles.
2. **Estados faltantes:** cargando, vacío, error, éxito, deshabilitado, sin permiso.
3. **Jerarquía y flujo:** ¿se entiende qué hacer primero? ¿coincide con las pantallas vecinas?
4. **Consistencia con el sistema:** colores sueltos, componentes duplicados, radios o espaciados
   distintos a los de `main.css`.
5. **Interacción:** hover, `:active`, `:focus-visible`, orden de tabulación, objetivos táctiles
   de al menos 40 px.
6. **Tipografía y texto:** pesos (usar 500 y 600, no solo 400/700), palabras huérfanas, textos
   genéricos, mayúsculas sostenidas.
7. **Código:** estilos en línea que deberían ir al CSS, `z-index` arbitrarios, código comentado,
   `transition: all`.

Clasificar cada desviación antes de corregirla:

- **Falta un token:** el sistema necesita un valor reutilizable → va a `input.css` / `main.css`.
- **Implementación aislada:** ya existe un componente compartido que debería usarse.
- **Desajuste conceptual:** el flujo o la jerarquía difiere de áreas parecidas del producto.
- **Defecto local:** la implementación está incompleta o inconsistente.

Corregir la causa en el nivel más estrecho correcto. Orden de prioridad: tareas rotas → estados
faltantes → flujo y consistencia → detalles visuales y de movimiento → limpieza de código.

---

## 7. Verificación

Inspeccionar en una sola ronda escritorio (1280 px) y móvil (≤ 640 px), en claro y oscuro,
corregir todo lo encontrado en un lote y confirmar con una ronda más como máximo. Revisar:
contraste, foco con teclado, textos largos (nombres de caficultor extensos, montos grandes),
estados vacío y error, consola sin errores.
