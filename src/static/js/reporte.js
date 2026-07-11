(() => {
    const form          = document.getElementById('formBuscar');
    const inputCodigo   = document.getElementById('inputCodigo');
    const btnBuscar     = document.getElementById('btnBuscar');
    const emptyState    = document.getElementById('emptyState');
    const notFoundState = document.getElementById('notFoundState');
    const resultados    = document.getElementById('resultados');
    const btnOriginal   = btnBuscar.innerHTML;

    function mostrarEstado(state) {
        emptyState.hidden    = state !== 'empty';
        notFoundState.hidden = state !== 'notfound';
        resultados.hidden    = state !== 'results';
    }

    function rellenar(d) {
        document.getElementById('codEval').textContent           = d.codigo || `EVA-${d.evaluacion_id.slice(0, 8)}`;
        document.getElementById('caficultorNombre').textContent  = d.caficultor_nombre || '—';
        document.getElementById('metaDoc').textContent           = d.num_documento     || '—';
        document.getElementById('metaTipoCaf').textContent       = d.tipo_caficultor   || '—';
        document.getElementById('metaGrano').textContent         = d.tipo_grano        || '—';
        document.getElementById('metaPesoQqGrano').textContent   = d.peso_qq_grano != null ? `${d.peso_qq_grano} kg` : '—';
        document.getElementById('metaRegistradoPor').textContent = d.registrado_por    || '—';

        document.getElementById('tdCodigo').textContent      = d.codigo                                             || '—';
        document.getElementById('tdFecha').textContent       = d.fecha                                              || '—';
        document.getElementById('tdSacos').textContent       = d.num_sacos    != null ? `${d.num_sacos} sacos`      : '—';
        document.getElementById('tdPeso').textContent        = d.peso_bruto   != null ? `${d.peso_bruto} kg`        : '—';
        document.getElementById('tdHumedad').textContent     = d.humedad      != null ? `${d.humedad}%`             : '—';
        document.getElementById('tdPesoMuestra').textContent = d.peso_muestra != null ? `${d.peso_muestra} gr`    : '—';
        document.getElementById('tdTrillado').textContent    = d.peso_trillado != null ? `${d.peso_trillado} gr`  : '—';
        document.getElementById('tdTamiz').textContent       = d.num_tamiz    != null ? `N° ${d.num_tamiz}`         : '—';
        document.getElementById('tdTamizado').textContent    = d.peso_tamizado != null ? `${d.peso_tamizado} gr`  : '—';

        rellenarStats(d);
        rellenarRendimiento(d);
        rellenarIncidencias(d.incidencias);
    }

    function rellenarStats(d) {
        const defectos = d.total_defectos;
        const buenos   = d.total_buenos;
        const total    = defectos != null && buenos != null ? defectos + buenos : null;
        const pct      = total > 0 ? Math.round((defectos / total) * 100) : null;

        document.getElementById('rStatGranos').textContent   = total    != null ? total.toLocaleString('es-PE')    : '—';
        document.getElementById('rStatDefectos').textContent = defectos != null ? defectos.toLocaleString('es-PE') : '—';
        document.getElementById('rStatSanos').textContent    = buenos   != null ? buenos.toLocaleString('es-PE')   : '—';
        document.getElementById('rStatPct').textContent      = pct      != null ? pct + '%'                        : '—';
    }

    function rellenarRendimiento(d) {
        const cards = document.getElementById('rRendimiento');
        const nota  = document.getElementById('rendimientoPendienteNota');
        const pendiente = d.factor_rendimiento == null;

        cards.style.display = pendiente ? 'none' : '';
        nota.style.display  = pendiente ? '' : 'none';
        if (pendiente) return;

        document.getElementById('rFactor').textContent    = Number(d.factor_rendimiento).toFixed(2);
        document.getElementById('rPesoBueno').textContent = d.peso_bueno != null ? `${Math.round(Number(d.peso_bueno))} g` : '—';
        document.getElementById('rPesoQq').textContent    = d.peso_por_qq != null ? Number(d.peso_por_qq).toFixed(2) : '—';
        document.getElementById('rPrecio').textContent    = d.precio != null ? Number(d.precio).toFixed(2) : '—';
        if (d.rango) document.getElementById('rPrecioLabel').textContent = `Precio quintal (S/) — rango ${d.rango}`;
        document.getElementById('rPago').textContent      = d.pago != null ? Number(d.pago).toFixed(2) : '—';
        document.getElementById('rCategoria').textContent = d.categoria || '—';
    }

    function rellenarIncidencias(arr) {
        const section = document.getElementById('incidenciasSection');
        const tbody   = document.getElementById('incidenciasTbody');
        if (!arr || arr.length === 0) {
            section.style.display = 'none';
            tbody.innerHTML = '';
            return;
        }
        section.style.display = '';
        tbody.innerHTML = arr.map(inc => {
            const dur = inc.duracion_s;
            const durStr = dur >= 60 ? `${Math.floor(dur / 60)}m ${dur % 60}s` : `${dur}s`;
            return `<tr><td>${inc.seg_apertura}s</td><td>${inc.seg_cierre}s</td><td>${durStr}</td></tr>`;
        }).join('');
    }

    // ── Input mask: prefijo "EVA" fijo, solo dígitos después ──────────────
    const PREFIX     = 'EVA';
    const MAX_DIGITS = 7;

    function applyMask() {
        const digits = inputCodigo.value.slice(PREFIX.length).replace(/\D/g, '').slice(0, MAX_DIGITS);
        inputCodigo.value = PREFIX + digits;
    }

    function clampCursor() {
        const s = inputCodigo.selectionStart;
        const e = inputCodigo.selectionEnd;
        const minPos = PREFIX.length;
        if (s < minPos || e < minPos) {
            const newPos = Math.max(s, minPos);
            inputCodigo.setSelectionRange(newPos, Math.max(e, minPos));
        }
    }

    inputCodigo.addEventListener('focus', () => {
        applyMask();
        const len = inputCodigo.value.length;
        inputCodigo.setSelectionRange(len, len);
    });

    inputCodigo.addEventListener('keydown', (e) => {
        const start = inputCodigo.selectionStart;
        const end   = inputCodigo.selectionEnd;

        // Impedir borrar el prefijo
        if (e.key === 'Backspace' && start <= PREFIX.length && end <= PREFIX.length) {
            e.preventDefault(); return;
        }
        if (e.key === 'Delete' && start < PREFIX.length) {
            e.preventDefault(); return;
        }
        // Bloquear letras y símbolos (permitir Ctrl+A/C/V/X y teclas de control)
        if (e.key.length === 1 && !/\d/.test(e.key) && !e.ctrlKey && !e.metaKey) {
            e.preventDefault(); return;
        }
        // Bloquear si ya hay 7 dígitos y no hay selección
        const digits = inputCodigo.value.slice(PREFIX.length).replace(/\D/g, '');
        if (e.key.length === 1 && /\d/.test(e.key) && digits.length >= MAX_DIGITS && start === end) {
            e.preventDefault();
        }
    });

    inputCodigo.addEventListener('input', applyMask);
    inputCodigo.addEventListener('click', clampCursor);
    inputCodigo.addEventListener('keyup', clampCursor);

    // Inicializar el input con el prefijo al cargar
    applyMask();
    // ───────────────────────────────────────────────────────────────────────

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const digits = inputCodigo.value.slice(PREFIX.length).replace(/\D/g, '');
        if (!digits) { inputCodigo.focus(); return; }
        const codigo = PREFIX + digits.padStart(MAX_DIGITS, '0');

        btnBuscar.disabled  = true;
        btnBuscar.innerHTML = '<span style="opacity:0.7">Buscando...</span>';

        try {
            const res = await fetch(`/evaluacion/buscar?codigo=${encodeURIComponent(codigo)}`);
            if (res.status === 404) {
                mostrarEstado('notfound');
                return;
            }
            if (!res.ok) throw new Error('Error de servidor');
            const d = await res.json();
            rellenar(d);
            mostrarEstado('results');
        } catch {
            mostrarEstado('empty');
            if (window.CoffeeModal) {
                CoffeeModal.error('No se pudo realizar la búsqueda. Intente de nuevo.', 'Error');
            }
        } finally {
            btnBuscar.disabled  = false;
            btnBuscar.innerHTML = btnOriginal;
        }
    });

    document.getElementById('btnExcel').addEventListener('click', () => {
        const g = (id) => document.getElementById(id)?.textContent ?? '—';

        const rows = [
            ['RESUMEN DE EVALUACIÓN DE CAFÉ - CoffeeRen', ''],
            [],
            ['DATOS DE LA MUESTRA', ''],
            ['Código evaluación',  g('tdCodigo')],
            ['Caficultor',         g('caficultorNombre')],
            ['Documento',          g('metaDoc')],
            ['Tipo caficultor',    g('metaTipoCaf')],
            ['Tipo de grano',      g('metaGrano')],
            ['Peso por quintal (grano)', g('metaPesoQqGrano')],
            ['Registrado por',     g('metaRegistradoPor')],
            ['Fecha',              g('tdFecha')],
            ['N° sacos',           g('tdSacos')],
            ['Peso bruto',         g('tdPeso')],
            ['Humedad',            g('tdHumedad')],
            ['Peso muestra',       g('tdPesoMuestra')],
            ['Peso trillado',      g('tdTrillado')],
            ['N° tamiz',           g('tdTamiz')],
            ['Peso tamizado',      g('tdTamizado')],
            [],
            ['ESTADÍSTICAS DE MONITOREO', ''],
            ['Granos evaluados',   g('rStatGranos')],
            ['Defectos totales',   g('rStatDefectos')],
            ['Granos buenos',      g('rStatSanos')],
            ['% Defecto',          g('rStatPct')],
            [],
            ['RENDIMIENTO', ''],
            ['Factor rendimiento', g('rFactor')],
            ['Peso bueno',         g('rPesoBueno')],
            ['Peso por quintal',   g('rPesoQq')],
            [g('rPrecioLabel'),    g('rPrecio')],
            ['Pago (S/)',          g('rPago')],
            ['Categoría',          g('rCategoria')],
        ];

        const tbody = document.getElementById('incidenciasTbody');
        if (tbody && tbody.rows.length > 0) {
            rows.push([]);
            rows.push(['INCIDENCIAS DE TAPA', '', '']);
            rows.push(['Apertura (s)', 'Cierre (s)', 'Duración abierta']);
            for (const tr of tbody.rows) {
                rows.push([tr.cells[0].textContent, tr.cells[1].textContent, tr.cells[2].textContent]);
            }
        }

        const ws = XLSX.utils.aoa_to_sheet(rows);
        ws['!cols'] = [{ wch: 34 }, { wch: 32 }, { wch: 20 }];
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, 'Resumen');
        const codigo = g('tdCodigo').replace(/[^A-Za-z0-9]/g, '') || 'evaluacion';
        XLSX.writeFile(wb, `${codigo}_resumen.xlsx`);
    });
})();
