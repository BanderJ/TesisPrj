(function () {
    const RANGO_RE = /^\d+(-\d+)?$/;

    /* ── Panel: rangos registrados hoy ───────────────────────────── */
    const panelRangosHoy   = document.getElementById('panelRangosHoy');
    const tablaRangosHoy   = document.getElementById('tablaRangosHoy');
    const subtituloHoy     = document.getElementById('subtituloRangosHoy');
    const btnRefrescar     = document.getElementById('btnRefrescarRangos');

    async function cargarRangosHoy() {
        try {
            const res = await fetch('/valor-cafe/resumen-rangos');
            if (!res.ok) return;
            const { fecha_consultada, data } = await res.json();

            if (!data || data.length === 0) {
                panelRangosHoy.style.display = 'none';
                return;
            }

            panelRangosHoy.style.display = '';
            const d = new Date(fecha_consultada + 'T00:00:00');
            subtituloHoy.textContent = d.toLocaleDateString('es-PE', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
            renderTablaRangos(data);
        } catch { /* no interrumpir si falla */ }
    }

    function renderTablaRangos(rangos) {
        tablaRangosHoy.innerHTML = `
            <table style="width:100%;border-collapse:collapse;font-size:.875rem">
                <thead>
                    <tr style="border-bottom:1px solid var(--border);text-align:left">
                        <th style="padding:.5rem .75rem;font-weight:600;color:var(--muted-foreground)">Rango</th>
                        <th style="padding:.5rem .75rem;font-weight:600;color:var(--muted-foreground)">Precio (S/.)</th>
                        <th style="padding:.5rem .75rem;font-weight:600;color:var(--muted-foreground)">Acciones</th>
                    </tr>
                </thead>
                <tbody id="tbodyRangos"></tbody>
            </table>`;

        const tbody = document.getElementById('tbodyRangos');
        rangos.forEach(item => tbody.appendChild(crearFilaRango(item)));
    }

    function crearFilaRango({ rango, precio }) {
        const tr = document.createElement('tr');
        tr.style.cssText = 'border-bottom:1px solid var(--border);transition:background .15s';
        tr.setAttribute('data-rango', rango);

        tr.innerHTML = `
            <td style="padding:.6rem .75rem;font-weight:500">${rango}</td>
            <td class="celda-precio" style="padding:.6rem .75rem">S/. ${Number(precio).toFixed(2)}</td>
            <td style="padding:.6rem .75rem;display:flex;gap:.5rem;flex-wrap:wrap">
                <button type="button" class="btn btn-secondary btn-editar-precio"
                    style="padding:.3rem .65rem;font-size:.8rem;height:auto">
                    Editar precio
                </button>
                <button type="button" class="btn btn-eliminar-rango"
                    style="padding:.3rem .65rem;font-size:.8rem;height:auto;background:color-mix(in oklab,var(--destructive) 12%,transparent);border-color:color-mix(in oklab,var(--destructive) 38%,var(--border) 62%);color:var(--destructive)">
                    Eliminar
                </button>
            </td>`;

        tr.querySelector('.btn-editar-precio').addEventListener('click', () => activarEdicionPrecio(tr, rango, precio));
        tr.querySelector('.btn-eliminar-rango').addEventListener('click', () => confirmarEliminar(tr, rango));
        return tr;
    }

    function activarEdicionPrecio(tr, rango, precioActual) {
        const celdaPrecio = tr.querySelector('.celda-precio');
        const celdaAcciones = tr.querySelector('td:last-child');

        celdaPrecio.innerHTML = `
            <input type="number" class="input-nuevo-precio" step="0.01" min="0.01"
                value="${Number(precioActual).toFixed(2)}"
                style="width:110px;padding:.3rem .5rem;font-size:.875rem;border:1px solid var(--border);border-radius:6px;background:var(--background);color:var(--foreground)">
            <p class="campo-error-msg precio-edit-error" style="margin:.2rem 0 0"></p>`;

        celdaAcciones.innerHTML = `
            <button type="button" class="btn btn-primary btn-guardar-precio"
                style="padding:.3rem .65rem;font-size:.8rem;height:auto">Guardar</button>
            <button type="button" class="btn btn-secondary btn-cancelar-edicion"
                style="padding:.3rem .65rem;font-size:.8rem;height:auto">Cancelar</button>`;

        const input = celdaPrecio.querySelector('.input-nuevo-precio');
        input.focus();
        input.select();

        celdaAcciones.querySelector('.btn-cancelar-edicion').addEventListener('click', () => {
            celdaPrecio.textContent = `S/. ${Number(precioActual).toFixed(2)}`;
            restaurarBotonesRango(celdaAcciones, tr, rango, precioActual);
        });

        celdaAcciones.querySelector('.btn-guardar-precio').addEventListener('click', () =>
            guardarNuevoPrecio(tr, rango, input, celdaPrecio, celdaAcciones)
        );
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') guardarNuevoPrecio(tr, rango, input, celdaPrecio, celdaAcciones);
            if (e.key === 'Escape') {
                celdaPrecio.textContent = `S/. ${Number(precioActual).toFixed(2)}`;
                restaurarBotonesRango(celdaAcciones, tr, rango, precioActual);
            }
        });
    }

    function restaurarBotonesRango(celdaAcciones, tr, rango, precio) {
        celdaAcciones.innerHTML = `
            <button type="button" class="btn btn-secondary btn-editar-precio"
                style="padding:.3rem .65rem;font-size:.8rem;height:auto">Editar precio</button>
            <button type="button" class="btn btn-eliminar-rango"
                style="padding:.3rem .65rem;font-size:.8rem;height:auto;background:color-mix(in oklab,var(--destructive) 12%,transparent);border-color:color-mix(in oklab,var(--destructive) 38%,var(--border) 62%);color:var(--destructive)">
                Eliminar</button>`;
        celdaAcciones.querySelector('.btn-editar-precio').addEventListener('click', () => activarEdicionPrecio(tr, rango, precio));
        celdaAcciones.querySelector('.btn-eliminar-rango').addEventListener('click', () => confirmarEliminar(tr, rango));
    }

    async function guardarNuevoPrecio(tr, rango, input, celdaPrecio, celdaAcciones) {
        const errEl = celdaPrecio.querySelector('.precio-edit-error');
        const nuevoPrecio = parseFloat(input.value);

        if (!input.value || isNaN(nuevoPrecio) || nuevoPrecio <= 0) {
            input.classList.add('input-invalido');
            errEl.textContent = 'El precio debe ser mayor a 0';
            return;
        }
        input.classList.remove('input-invalido');
        errEl.textContent = '';

        const errorContexto = validarPrecioEnContexto(tr, rango, nuevoPrecio);
        if (errorContexto) {
            input.classList.add('input-invalido');
            errEl.textContent = errorContexto;
            return;
        }

        const btnGuardar = celdaAcciones.querySelector('.btn-guardar-precio');
        btnGuardar.disabled = true;
        btnGuardar.textContent = 'Guardando...';

        try {
            const res = await fetch('/valor-cafe/actualizar-precio', {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rango, precio: nuevoPrecio }),
            });
            if (!res.ok) {
                const err = await res.json();
                CoffeeModal.error(err.detail || 'No se pudo actualizar el precio.');
                btnGuardar.disabled = false;
                btnGuardar.textContent = 'Guardar';
                return;
            }
            const data = await res.json();
            const precioFinal = parseFloat(data.precio);
            celdaPrecio.textContent = `S/. ${precioFinal.toFixed(2)}`;
            restaurarBotonesRango(celdaAcciones, tr, rango, precioFinal);
            CoffeeModal.success(`Precio del rango ${rango} actualizado a S/. ${precioFinal.toFixed(2)}`, 'Precio actualizado');
        } catch {
            CoffeeModal.error('Error de conexión al actualizar el precio.');
            btnGuardar.disabled = false;
            btnGuardar.textContent = 'Guardar';
        }
    }

    async function confirmarEliminar(tr, rango) {
        const ok = await CoffeeModal.confirm({
            type: 'warning',
            title: `Eliminar rango ${rango}`,
            message: `Se eliminarán todos los precios del rango "${rango}" registrados hoy. Esta acción no se puede deshacer.`,
            okText: 'Eliminar',
            cancelText: 'Cancelar',
        });
        if (!ok) return;

        try {
            const res = await fetch(`/valor-cafe/eliminar-rango?rango=${encodeURIComponent(rango)}`, { method: 'DELETE' });
            if (!res.ok) {
                const err = await res.json();
                CoffeeModal.error(err.detail || 'No se pudo eliminar el rango.');
                return;
            }
            tr.remove();
            const filas = document.querySelectorAll('#tbodyRangos tr');
            if (filas.length === 0) panelRangosHoy.style.display = 'none';
            CoffeeModal.success(`Rango ${rango} eliminado correctamente.`, 'Rango eliminado');
        } catch {
            CoffeeModal.error('Error de conexión al eliminar el rango.');
        }
    }

    btnRefrescar.addEventListener('click', cargarRangosHoy);

    /* Cargar rangos al entrar a la página */
    cargarRangosHoy();

    /* ── Helpers de rango ── */
    function validarRango(rango) {
        const r = rango.trim();
        if (!r) return 'El rango es requerido';
        if (!RANGO_RE.test(r)) return 'Use número (ej: 70) o rango X-Y (ej: 60-65)';
        if (r.includes('-')) {
            const [a, b] = r.split('-').map(Number);
            if (a >= b) return 'X debe ser menor a Y en el rango X-Y';
        }
        return null;
    }

    function parseRango(rango) {
        const r = rango.trim();
        if (r.includes('-')) {
            const [a, b] = r.split('-').map(Number);
            return { min: a, max: b };
        }
        const n = Number(r);
        return { min: n, max: n };
    }

    function seSuperponen(p1, p2) {
        return p1.min <= p2.max && p2.min <= p1.max;
    }

    function validarPrecioEnContexto(trEditando, rangoEditando, nuevoPrecio) {
        const rangos = [];
        document.querySelectorAll('#tbodyRangos tr[data-rango]').forEach(tr => {
            const r = tr.getAttribute('data-rango');
            const p = tr === trEditando
                ? nuevoPrecio
                : parseFloat(tr.querySelector('.celda-precio').textContent.replace('S/.', '').trim());
            if (!isNaN(p)) rangos.push({ rango: r, precio: p, parsed: parseRango(r) });
        });

        rangos.sort((a, b) => a.parsed.min - b.parsed.min);

        for (let i = 1; i < rangos.length; i++) {
            if (rangos[i].precio < rangos[i - 1].precio) {
                if (rangos[i].rango === rangoEditando)
                    return `Precio menor al rango inferior "${rangos[i - 1].rango}" (S/. ${rangos[i - 1].precio.toFixed(2)})`;
                if (rangos[i - 1].rango === rangoEditando)
                    return `El precio supera al rango siguiente "${rangos[i].rango}" (S/. ${rangos[i].precio.toFixed(2)})`;
            }
        }
        return null;
    }

    async function obtenerRangosHoyParseados() {
        try {
            const res = await fetch('/valor-cafe/resumen-rangos');
            if (!res.ok) return [];
            const { data } = await res.json();
            return (data || []).map(item => ({
                rango: item.rango,
                precio: parseFloat(item.precio),
                parsed: parseRango(item.rango),
            }));
        } catch { return []; }
    }

    function validarContraExistentes(nuevosRangos, existentes) {
        const errores = [];

        for (const nuevo of nuevosRangos) {
            const solapado = existentes.find(e => seSuperponen(e.parsed, nuevo.parsed));
            if (solapado) {
                errores.push({ tipo: 'overlap', nuevo, con: solapado });
            }
        }

        if (errores.length > 0) return errores;

        const todos = [...existentes, ...nuevosRangos].sort((a, b) => a.parsed.min - b.parsed.min);
        const nuevosSet = new Set(nuevosRangos.map(r => r.rango));
        for (let i = 1; i < todos.length; i++) {
            if (todos[i].precio < todos[i - 1].precio) {
                const afectaANuevo = nuevosSet.has(todos[i].rango) || nuevosSet.has(todos[i - 1].rango);
                if (afectaANuevo) {
                    errores.push({ tipo: 'precio', a: todos[i - 1], b: todos[i] });
                }
            }
        }

        return errores;
    }

    function mensajeHttpError(data, status) {
        if (status === 401) return 'Sesión expirada. Vuelve a iniciar sesión.';
        if (status === 403) return 'Sin permisos para registrar precios.';
        return data.detail || 'Error al registrar.';
    }

    /* ───── Formulario individual ───── */
    const formIndividual = document.getElementById('formValorCafe');

    formIndividual.addEventListener('submit', async (e) => {
        e.preventDefault();
        const rangoInput = document.getElementById('rango');
        const precioInput = document.getElementById('precio');
        const rangoErrorEl = document.getElementById('rangoError');
        const precioErrorEl = document.getElementById('precioError');

        rangoInput.classList.remove('input-invalido');
        precioInput.classList.remove('input-invalido');
        rangoErrorEl.textContent = '';
        precioErrorEl.textContent = '';

        const errorRango = validarRango(rangoInput.value);
        const precio = parseFloat(precioInput.value);
        const errorPrecio = (!precioInput.value || isNaN(precio) || precio <= 0)
            ? 'El precio debe ser mayor a 0' : null;

        if (errorRango) { rangoInput.classList.add('input-invalido'); rangoErrorEl.textContent = errorRango; }
        if (errorPrecio) { precioInput.classList.add('input-invalido'); precioErrorEl.textContent = errorPrecio; }
        if (errorRango || errorPrecio) return;

        const rangoNormalizado = rangoInput.value.trim();
        const existentes = await obtenerRangosHoyParseados();
        if (existentes.length > 0) {
            const erroresCtx = validarContraExistentes(
                [{ rango: rangoNormalizado, precio, parsed: parseRango(rangoNormalizado) }],
                existentes,
            );
            for (const err of erroresCtx) {
                if (err.tipo === 'overlap') {
                    rangoInput.classList.add('input-invalido');
                    rangoErrorEl.textContent = `Se superpone con el rango ya registrado "${err.con.rango}"`;
                } else {
                    precioInput.classList.add('input-invalido');
                    precioErrorEl.textContent = err.b.rango === rangoNormalizado
                        ? `Precio menor al rango inferior ya registrado "${err.a.rango}" (S/. ${err.a.precio.toFixed(2)})`
                        : `El precio supera al rango siguiente ya registrado "${err.b.rango}" (S/. ${err.b.precio.toFixed(2)})`;
                }
            }
            if (erroresCtx.length > 0) return;
        }

        try {
            const res = await fetch('/valor-cafe/crear', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rango: rangoInput.value.trim(), precio }),
            });
            if (!res.ok) {
                CoffeeModal.error(mensajeHttpError(await res.json(), res.status));
                return;
            }
            const data = await res.json();
            CoffeeModal.success(`Rango ${data.rango} registrado — S/. ${data.precio.toFixed(2)}`);
            formIndividual.reset();
            rangoErrorEl.textContent = '';
            precioErrorEl.textContent = '';
            cargarRangosHoy();
        } catch {
            CoffeeModal.error('Error de conexión. Verifica tu red e intenta de nuevo.');
        }
    });

    formIndividual.addEventListener('reset', () => {
        document.getElementById('rangoError').textContent = '';
        document.getElementById('precioError').textContent = '';
        document.getElementById('rango').classList.remove('input-invalido');
        document.getElementById('precio').classList.remove('input-invalido');
    });

    /* ───── Formulario en bloque (dinámico) ───── */
    const contenedor = document.getElementById('bloqueFila');
    const counter = document.getElementById('filaCounter');
    let filaIdx = 0;

    function actualizarCounter() {
        const n = contenedor.querySelectorAll('.bloque-fila').length;
        counter.textContent = `${n} ${n === 1 ? 'rango' : 'rangos'}`;
    }

    function crearFila() {
        const idx = filaIdx++;
        const fila = document.createElement('div');
        fila.className = 'bloque-fila';
        fila.innerHTML = `
            <div class="field-group">
                <label for="fr_${idx}">Rango</label>
                <input id="fr_${idx}" type="text" class="fila-rango" placeholder="Ej: 60-65 o 70" maxlength="10" autocomplete="off">
                <p class="campo-error-msg fila-rango-error"></p>
            </div>
            <div class="field-group">
                <label for="fp_${idx}">Precio (S/.)</label>
                <input id="fp_${idx}" type="number" class="fila-precio" step="0.01" min="0.01" placeholder="Ej: 750.00">
                <p class="campo-error-msg fila-precio-error"></p>
            </div>
            <button type="button" class="btn-remove-fila" title="Eliminar fila" aria-label="Eliminar fila">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                </svg>
            </button>
        `;

        fila.querySelector('.btn-remove-fila').addEventListener('click', () => {
            fila.remove();
            actualizarCounter();
        });

        const rangoInput = fila.querySelector('.fila-rango');
        rangoInput.addEventListener('input', () => {
            const err = validarRango(rangoInput.value);
            const errEl = fila.querySelector('.fila-rango-error');
            if (err) { rangoInput.classList.add('input-invalido'); errEl.textContent = err; }
            else { rangoInput.classList.remove('input-invalido'); errEl.textContent = ''; }
        });

        contenedor.appendChild(fila);
        actualizarCounter();
        rangoInput.focus();
    }

    document.getElementById('btnAgregarFila').addEventListener('click', crearFila);

    document.getElementById('btnLimpiarBloque').addEventListener('click', () => {
        contenedor.innerHTML = '';
        filaIdx = 0;
        crearFila();
    });

    document.getElementById('formValorCafeBloque').addEventListener('submit', async (e) => {
        e.preventDefault();

        const filas = contenedor.querySelectorAll('.bloque-fila');
        if (filas.length === 0) {
            CoffeeModal.warning('Agrega al menos un rango antes de registrar.');
            return;
        }

        /* ── Paso 1: validación individual por fila ── */
        const entradas = [];
        const exactosVistos = new Set();
        let hayError = false;

        filas.forEach((fila) => {
            const rangoInput = fila.querySelector('.fila-rango');
            const precioInput = fila.querySelector('.fila-precio');
            const rangoErrEl = fila.querySelector('.fila-rango-error');
            const precioErrEl = fila.querySelector('.fila-precio-error');

            rangoInput.classList.remove('input-invalido');
            precioInput.classList.remove('input-invalido');
            rangoErrEl.textContent = '';
            precioErrEl.textContent = '';

            const rango = rangoInput.value.trim();
            const precio = parseFloat(precioInput.value);
            let filaInvalida = false;

            const errRango = validarRango(rango);
            if (errRango) {
                rangoInput.classList.add('input-invalido');
                rangoErrEl.textContent = errRango;
                filaInvalida = true;
            } else if (exactosVistos.has(rango)) {
                rangoInput.classList.add('input-invalido');
                rangoErrEl.textContent = `Rango idéntico duplicado: ${rango}`;
                filaInvalida = true;
            } else {
                exactosVistos.add(rango);
            }

            if (!precioInput.value || isNaN(precio) || precio <= 0) {
                precioInput.classList.add('input-invalido');
                precioErrEl.textContent = 'Precio debe ser mayor a 0';
                filaInvalida = true;
            }

            if (filaInvalida) {
                hayError = true;
            } else {
                entradas.push({ rango, precio, parsed: parseRango(rango), rangoInput, rangoErrEl, precioInput, precioErrEl });
            }
        });

        if (hayError) {
            CoffeeModal.warning('Revisa los campos marcados en rojo antes de registrar.');
            return;
        }

        /* ── Paso 2: detección de solapamiento entre rangos ── */
        for (let i = 0; i < entradas.length; i++) {
            for (let j = i + 1; j < entradas.length; j++) {
                if (seSuperponen(entradas[i].parsed, entradas[j].parsed)) {
                    entradas[i].rangoInput.classList.add('input-invalido');
                    entradas[i].rangoErrEl.textContent = `Se superpone con "${entradas[j].rango}"`;
                    entradas[j].rangoInput.classList.add('input-invalido');
                    entradas[j].rangoErrEl.textContent = `Se superpone con "${entradas[i].rango}"`;
                    hayError = true;
                }
            }
        }

        if (hayError) {
            CoffeeModal.error('Los rangos no pueden compartir valores. Ajusta los límites.');
            return;
        }

        /* ── Paso 3: precios deben ser no decrecientes al subir el rango ── */
        const ordenadas = [...entradas].sort((a, b) => a.parsed.min - b.parsed.min);
        for (let i = 1; i < ordenadas.length; i++) {
            if (ordenadas[i].precio < ordenadas[i - 1].precio) {
                ordenadas[i].precioInput.classList.add('input-invalido');
                ordenadas[i].precioErrEl.textContent =
                    `Precio menor al rango inferior "${ordenadas[i - 1].rango}" (S/. ${ordenadas[i - 1].precio.toFixed(2)})`;
                hayError = true;
            }
        }

        if (hayError) {
            CoffeeModal.error('Los precios deben ser mayores o iguales conforme sube el rango.');
            return;
        }

        /* ── Paso 4: validación contra rangos ya registrados hoy ── */
        const existentesHoy = await obtenerRangosHoyParseados();
        if (existentesHoy.length > 0) {
            const nuevos = entradas.map(({ rango, precio, parsed }) => ({ rango, precio, parsed }));
            const erroresCtx = validarContraExistentes(nuevos, existentesHoy);
            for (const err of erroresCtx) {
                if (err.tipo === 'overlap') {
                    const entrada = entradas.find(e => e.rango === err.nuevo.rango);
                    if (entrada) {
                        entrada.rangoInput.classList.add('input-invalido');
                        entrada.rangoErrEl.textContent = `Se superpone con el rango ya registrado "${err.con.rango}"`;
                        hayError = true;
                    }
                } else {
                    const entradaB = entradas.find(e => e.rango === err.b.rango);
                    const entradaA = entradas.find(e => e.rango === err.a.rango);
                    if (entradaB) {
                        entradaB.precioInput.classList.add('input-invalido');
                        entradaB.precioErrEl.textContent = `Precio menor al rango "${err.a.rango}" ya registrado (S/. ${err.a.precio.toFixed(2)})`;
                        hayError = true;
                    } else if (entradaA) {
                        entradaA.precioInput.classList.add('input-invalido');
                        entradaA.precioErrEl.textContent = `El precio supera al rango siguiente ya registrado "${err.b.rango}" (S/. ${err.b.precio.toFixed(2)})`;
                        hayError = true;
                    }
                }
            }
            if (hayError) {
                CoffeeModal.error('Los nuevos rangos tienen conflictos con registros ya existentes de hoy. Revisa los campos marcados.');
                return;
            }
        }

        /* ── Envío ── */
        const precios = entradas.map(({ rango, precio }) => ({ rango, precio }));
        try {
            const res = await fetch('/valor-cafe/crear-bloque', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ precios }),
            });
            if (!res.ok) {
                CoffeeModal.error(mensajeHttpError(await res.json(), res.status));
                return;
            }
            const data = await res.json();
            CoffeeModal.success(`${data.total} ${data.total === 1 ? 'precio guardado' : 'precios guardados'} correctamente.`, 'Bloque registrado');
            contenedor.innerHTML = '';
            filaIdx = 0;
            actualizarCounter();
            crearFila();
            cargarRangosHoy();
        } catch {
            CoffeeModal.error('Error de conexión al registrar el bloque.');
        }
    });

    /* Inicializar con una fila vacía */
    crearFila();
})();
