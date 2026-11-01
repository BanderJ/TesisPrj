(() => {
    const form          = document.getElementById('formBuscar');
    const inputCodigo   = document.getElementById('inputCodigo');
    const btnBuscar     = document.getElementById('btnBuscar');
    const emptyState    = document.getElementById('emptyState');
    const notFoundState = document.getElementById('notFoundState');
    const resultados    = document.getElementById('resultados');
    const exportar      = document.getElementById('reporteExport');
    const btnOriginal   = btnBuscar.innerHTML;

    function mostrarEstado(state) {
        emptyState.hidden    = state !== 'empty';
        notFoundState.hidden = state !== 'notfound';
        resultados.hidden    = state !== 'results';
        exportar.hidden      = state !== 'results';
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
        btnBuscar.textContent = 'Buscando…';

        try {
            const res = await fetch(`/evaluacion/buscar?codigo=${encodeURIComponent(codigo)}`);
            if (res.status === 404) {
                mostrarEstado('notfound');
                return;
            }
            if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo realizar la búsqueda. Intente de nuevo.'));
            const d = await res.json();
            CoffeeResumen.pintar(d);
            document.getElementById('btnCalcularRendimiento').href = `/analisis/${encodeURIComponent(d.evaluacion_id)}`;
            mostrarEstado('results');
        } catch (err) {
            mostrarEstado('empty');
            CoffeeModal.error(err.message, 'Error');
        } finally {
            btnBuscar.disabled  = false;
            btnBuscar.innerHTML = btnOriginal;
        }
    });

    document.getElementById('btnExcel').addEventListener('click', CoffeeResumen.exportarExcel);
})();
