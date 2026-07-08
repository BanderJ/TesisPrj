/**
 * CoffeeRen Validators
 * Módulo de validaciones reutilizables para formularios.
 *
 * Uso básico:
 *   CoffeeValidators.documento({ tipoEl: '#tipoDoc', numEl: '#numDoc', hintEl: '#hint', onSearch: fn })
 *   CoffeeValidators.contrasena({ inputEl: '#clave', contadorEl: '#contador', reqsPrefix: 'req' })
 *   CoffeeValidators.confirmar({ claveEl: '#clave', confirmarEl: '#confirmar', matchEl: '#match' })
 *   CoffeeValidators.telefono({ inputEl: '#telefono' })
 *   CoffeeValidators.ubigeo({ deptoEl, provEl, distEl })
 */

const CoffeeValidators = (() => {

    const MAX_CLAVE = 30;

    // ── Helpers internos ───────────────────────────────────────────────

    function el(selector) {
        if (!selector) return null;
        if (typeof selector === 'string') return document.getElementById(selector) || document.querySelector(selector);
        return selector;
    }

    function normalizarTexto(texto) {
        return String(texto || '')
            .normalize('NFD').replace(/[̀-ͯ]/g, '')
            .toLowerCase().trim();
    }

    // ── 1. Documento (DNI / Pasaporte / Carnet) ────────────────────────

    /**
     * @param {Object} config
     * @param {string|Element} config.tipoEl      — select tipo documento
     * @param {string|Element} config.numEl       — input número documento
     * @param {string|Element} [config.hintEl]    — elemento para mostrar hint de formato
     * @param {Array}          [config.tiposData] — array de tipos [{id, nombre}] para resolver reglas
     * @param {Function}       [config.onSearch]  — callback(numDoc) cuando longitud alcanza el límite
     * @param {number}         [config.debounce]  — ms debounce (default 320)
     */
    function documento({ tipoEl, numEl, hintEl, tiposData = [], onSearch, debounce = 320 }) {
        const $tipo = el(tipoEl);
        const $num  = el(numEl);
        const $hint = el(hintEl);
        if (!$tipo || !$num) return;

        let timer = null;

        function obtenerRegla(tipoId) {
            const id = Number(tipoId || 0);
            const nombre = normalizarTexto(tiposData.find(t => t.id === id)?.nombre || '');
            if (nombre === 'dni') return {
                maxLength: 8, soloNumeros: true,
                hint: 'DNI: exactamente 8 dígitos numéricos.',
                placeholder: 'Ingrese 8 dígitos',
                regex: /^\d{8}$/,
                longitudesAutoBusqueda: [8],
            };
            if (nombre === 'pasaporte' || nombre === 'carnet de extranjeria') return {
                maxLength: 12, soloNumeros: false,
                hint: 'Pasaporte/Carnet: 8 a 12 caracteres alfanuméricos.',
                placeholder: 'Ingrese 8-12 caracteres',
                regex: /^[A-Za-z0-9]{8,12}$/,
                longitudesAutoBusqueda: [12],
            };
            return {
                maxLength: 12, soloNumeros: false,
                hint: 'Documento: 8 a 12 caracteres.',
                placeholder: 'Ingrese documento',
                regex: /^[A-Za-z0-9]{8,12}$/,
                longitudesAutoBusqueda: [8, 12],
            };
        }

        function limpiar(valor, regla) {
            const txt = String(valor || '');
            if (regla.soloNumeros) return txt.replace(/\D/g, '').slice(0, regla.maxLength);
            return txt.replace(/[^A-Za-z0-9]/g, '').toUpperCase().slice(0, regla.maxLength);
        }

        function aplicarRegla() {
            const regla = obtenerRegla($tipo.value);
            $num.maxLength   = regla.maxLength;
            $num.placeholder = regla.placeholder;
            $num.inputMode   = regla.soloNumeros ? 'numeric' : 'text';
            if ($hint) $hint.textContent = regla.hint;
            $num.value = limpiar($num.value, regla);
        }

        $tipo.addEventListener('change', () => {
            aplicarRegla();
            $num.value = '';
        });

        $num.addEventListener('input', () => {
            const regla = obtenerRegla($tipo.value);
            $num.value = limpiar($num.value, regla);
            clearTimeout(timer);
            if (onSearch && regla.longitudesAutoBusqueda.includes($num.value.length)) {
                timer = setTimeout(() => onSearch($num.value), debounce);
            }
        });

        // Exponer para uso externo
        return { obtenerRegla, limpiar, aplicarRegla };
    }

    // ── 2. Contraseña con requisitos y contador ────────────────────────

    /**
     * @param {Object} config
     * @param {string|Element} config.inputEl     — input password
     * @param {string|Element} [config.contadorEl] — span contador "0/30"
     * @param {number}         [config.max]        — máximo de caracteres (default 30)
     * @param {Object}         [config.reqs]       — { length, uppercase, number, special } → IDs o Elements
     * @param {Function}       [config.onChange]   — callback al escribir
     */
    function contrasena({ inputEl, contadorEl, max = MAX_CLAVE, reqs = {}, onChange }) {
        const $input    = el(inputEl);
        const $contador = el(contadorEl);
        if (!$input) return;

        $input.maxLength = max;

        const $reqs = {
            length:    el(reqs.length),
            uppercase: el(reqs.uppercase),
            number:    el(reqs.number),
            special:   el(reqs.special),
        };

        function validar(password) {
            return {
                length:    password.length >= 8,
                uppercase: /[A-Z]/.test(password),
                number:    /\d/.test(password),
                special:   /[!@#%^&*(),.=?":{}$¿?¡]/.test(password),
            };
        }

        function actualizarReqs(result) {
            for (const [key, $req] of Object.entries($reqs)) {
                if (!$req) continue;
                $req.classList.toggle('active',   !!result[key]);
                $req.classList.toggle('inactive', !result[key]);
            }
        }

        function actualizarContador(len) {
            if (!$contador) return;
            $contador.textContent = `${len}/${max}`;
            $contador.style.color = len >= max ? 'var(--destructive)' : 'var(--muted-foreground)';
            if (len >= max && typeof CoffeeModal !== 'undefined') {
                CoffeeModal.warning(`La contraseña no puede exceder ${max} caracteres.`);
            }
        }

        $input.addEventListener('input', () => {
            const val = $input.value;
            actualizarContador(val.length);
            actualizarReqs(validar(val));
            if (onChange) onChange(val);
        });

        return { validar };
    }

    // ── 3. Confirmar contraseña ────────────────────────────────────────

    /**
     * @param {Object} config
     * @param {string|Element} config.claveEl     — input contraseña
     * @param {string|Element} config.confirmarEl — input confirmar contraseña
     * @param {string|Element} config.matchEl     — contenedor del indicador
     * @param {string|Element} [config.matchTextEl] — span del texto del match
     */
    function confirmar({ claveEl, confirmarEl, matchEl, matchTextEl }) {
        const $clave     = el(claveEl);
        const $confirmar = el(confirmarEl);
        const $match     = el(matchEl);
        const $matchText = el(matchTextEl);
        if (!$clave || !$confirmar || !$match) return;

        function actualizar() {
            if (!$clave.value || !$confirmar.value) {
                $match.classList.remove('show', 'match', 'mismatch');
                return;
            }
            $match.classList.add('show');
            const coincide = $clave.value === $confirmar.value;
            $match.classList.toggle('match',    coincide);
            $match.classList.toggle('mismatch', !coincide);
            if ($matchText) $matchText.textContent = coincide ? 'Las contraseñas coinciden' : 'Las contraseñas no coinciden';
        }

        $clave.addEventListener('input', actualizar);
        $confirmar.addEventListener('input', actualizar);

        return { esValida: () => $clave.value === $confirmar.value && $clave.value.length > 0 };
    }

    // ── 4. Teléfono — solo dígitos, 9 caracteres ──────────────────────

    /**
     * @param {string|Element} inputEl
     */
    function telefono(inputEl) {
        const $input = el(inputEl);
        if (!$input) return;
        $input.maxLength = 9;
        $input.inputMode = 'numeric';
        $input.addEventListener('input', () => {
            $input.value = $input.value.replace(/\D/g, '').slice(0, 9);
        });
    }

    // ── 5. Cascada de ubigeo ───────────────────────────────────────────

    /**
     * @param {Object} config
     * @param {string|Element} config.deptoEl  — select departamento
     * @param {string|Element} config.provEl   — select provincia
     * @param {string|Element} config.distEl   — select distrito
     */
    function ubigeo({ deptoEl, provEl, distEl }) {
        const $depto = el(deptoEl);
        const $prov  = el(provEl);
        const $dist  = el(distEl);
        if (!$depto || !$prov || !$dist) return;

        async function cargarDepartamentos() {
            try {
                const res  = await fetch('/ubigeo/departamentos');
                const data = await res.json();
                $depto.innerHTML = '<option value="">Selecciona...</option>';
                data.forEach(d => {
                    const opt = document.createElement('option');
                    opt.value       = d.codigo;
                    opt.textContent = d.nombre;
                    $depto.appendChild(opt);
                });
            } catch (e) { console.error('ubigeo departamentos:', e); }
        }

        async function cargarProvincias(depCode) {
            try {
                $prov.innerHTML = '<option value="">Cargando...</option>';
                const res  = await fetch(`/ubigeo/provincias?departamento=${depCode}`);
                const data = await res.json();
                $prov.innerHTML = '<option value="">Selecciona...</option>';
                data.forEach(p => {
                    const opt = document.createElement('option');
                    opt.value       = p.codigo;
                    opt.textContent = p.nombre;
                    $prov.appendChild(opt);
                });
                $prov.disabled = false;
                $dist.disabled = true;
                $dist.innerHTML = '<option value="">Selecciona provincia primero</option>';
            } catch (e) { console.error('ubigeo provincias:', e); $prov.disabled = true; }
        }

        async function cargarDistritos(provCode) {
            try {
                $dist.innerHTML = '<option value="">Cargando...</option>';
                const res  = await fetch(`/ubigeo/distritos?provincia=${provCode}`);
                const data = await res.json();
                $dist.innerHTML = '<option value="">Selecciona...</option>';
                data.forEach(d => {
                    const opt = document.createElement('option');
                    opt.value       = d.codigo;
                    opt.textContent = d.nombre;
                    $dist.appendChild(opt);
                });
                $dist.disabled = false;
            } catch (e) { console.error('ubigeo distritos:', e); $dist.disabled = true; }
        }

        async function seleccionar(ubigeoCode) {
            if (!ubigeoCode || !/^\d{6}$/.test(ubigeoCode)) return;
            const depCode  = ubigeoCode.substring(0, 2);
            const provCode = ubigeoCode.substring(0, 4);
            if (!$depto.querySelector(`option[value="${depCode}"]`)) await cargarDepartamentos();
            $depto.value = depCode;
            await cargarProvincias(depCode);
            $prov.value = provCode;
            await cargarDistritos(provCode);
            $dist.value = ubigeoCode;
        }

        $depto.addEventListener('change', () => {
            if ($depto.value) cargarProvincias($depto.value);
            else { $prov.disabled = true; $dist.disabled = true; }
        });

        $prov.addEventListener('change', () => {
            if ($prov.value) cargarDistritos($prov.value);
            else $dist.disabled = true;
        });

        return { cargarDepartamentos, seleccionar, getUbigeo: () => $dist.value || null };
    }

    // ── 6. Peso de grano bueno (gramos enteros, tope = peso trillado) ──

    /**
     * @param {string|number} valor      — valor ingresado por el usuario
     * @param {number|null}   maxGramos  — peso trillado (tope), o null si no se conoce
     * @returns {{valido: boolean, peso?: number, mensaje?: string}}
     */
    function pesoBueno(valor, maxGramos = null) {
        const texto = String(valor ?? '').trim();
        const peso  = Number(texto);
        if (texto === '' || !Number.isFinite(peso)) return { valido: false, mensaje: 'Ingresa el peso de grano bueno.' };
        if (!Number.isInteger(peso))                return { valido: false, mensaje: 'El peso debe ser un número entero (gramos, sin decimales).' };
        if (peso < 0)                               return { valido: false, mensaje: 'El peso no puede ser negativo.' };
        if (maxGramos !== null && peso > maxGramos) return { valido: false, mensaje: `El peso no puede superar el máximo permitido (${maxGramos} g).` };
        return { valido: true, peso };
    }

    // ── API pública ────────────────────────────────────────────────────

    return { documento, contrasena, confirmar, telefono, ubigeo, pesoBueno };

})();
