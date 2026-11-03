	(() => {
		const form                  = document.getElementById('registroForm');
		const tipoDocumentoSelect   = document.getElementById('tipoDocumento');
		const numDocumentoInput     = document.getElementById('numDocumento');
		const nombreCaficultorInput = document.getElementById('nombreCaficultor');
		const tipoCaficultorInput   = document.getElementById('tipoCaficultor');
		const caficultorLookupMsg   = document.getElementById('caficultorLookupMessage');
		const tipoGranoSelect       = document.getElementById('tipoGrano');
		const startBtn              = document.getElementById('startMonitoringBtn');
		const clearBtn              = document.getElementById('clearFormBtn');
		const numSacosInput         = document.getElementById('numSacos');
		const numSacosHint          = document.getElementById('numSacosHint');
		const pesoTotalInput        = document.getElementById('pesoTotal');
		const pesoTotalHint         = document.getElementById('pesoTotalHint');
		const humedadInput          = document.getElementById('humedad');
		const humedadHint           = document.getElementById('humedadHint');
		const pesoMuestraInput      = document.getElementById('pesoMuestra');
		const pesoMuestraHint       = document.getElementById('pesoMuestraHint');
		const pesoTrilladoInput     = document.getElementById('pesoTrillado');
		const pesoTrilladoHint      = document.getElementById('pesoTrilladoHint');
		const numTamizInput         = document.getElementById('numTamiz');
		const pesoTamizadoInput     = document.getElementById('pesoTamizado');
		const pesoTamizadoHint      = document.getElementById('pesoTamizadoHint');

		const tiposDocumento = new Map();
		let consultaTimer = null;
		let caficultorValido = false;
		let ultimaClaveBusqueda = '';

		// ── Utilidades ────────────────────────────────────────────────────

				function normalizarTexto(v) {
				return v.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim();
			}

		function setHint(el, msg, esError = false) {
			el.textContent = msg;
			el.classList.toggle('helper-error', esError);
		}

		function rechazar(msg, campo = null) {
			CoffeeModal.warning(msg);
			campo?.focus();
			return false;
		}

		function validarInline(input, testFn, hintEl, errorMsg) {
			if (!input.value) { setHint(hintEl, ''); return; }
			const ok = testFn(input.value);
			setHint(hintEl, ok ? '' : errorMsg, !ok);
		}

		const esEnteroPositivo = (v) => { const n = Number(v); return Number.isFinite(n) && Number.isInteger(n) && n >= 1; };
		const esFloatPositivo  = (v) => { const n = parseFloat(v); return Number.isFinite(n) && n > 0; };
		const redondear2       = (v) => Math.round(parseFloat(v) * 100) / 100;
		// Tara total = sacos × 0.25 kg, sin redondear (igual que el backend:
		// TARA_POR_SACO_KG en src/schemas/evaluacion.py). Solo se fija a 2 decimales.
		const TARA_POR_SACO_KG = 0.25;
		// Tope de sacos por lote: igual que MAX_SACOS_POR_LOTE en src/schemas/evaluacion.py.
		const MAX_SACOS        = 30;
		const esNumSacosValido = (v) => esEnteroPositivo(v) && Number(v) <= MAX_SACOS;
		const calcularTara     = (sacos) => redondear2(sacos * TARA_POR_SACO_KG);

		function forzarEntero(input) {
			input.addEventListener('change', () => {
				const n = parseInt(input.value, 10);
				if (!isNaN(n)) input.value = n;
			});
		}

		function forzar2Decimales(input) {
			input.addEventListener('blur', () => {
				const n = parseFloat(input.value);
				if (input.value && !isNaN(n)) input.value = redondear2(n).toFixed(2);
			});
		}

		// Bloquea e/E/+/- (notación científica y signos que permite <input type="number">).
		// soloEntero=true también bloquea el punto decimal.
		function bloquearCaracteresNumericos(input, soloEntero = false) {
			const bloqueados = new Set(['e', 'E', '+', '-']);
			if (soloEntero) { bloqueados.add('.'); bloqueados.add(','); }
			input.addEventListener('keydown', (e) => {
				if (bloqueados.has(e.key)) e.preventDefault();
			});
		}

		async function cargarSelect(url, selectEl) {
			const res = await fetch(url);
			if (!res.ok) throw new Error(`Error al cargar ${url}`);
			const items = await res.json();
			const frag = document.createDocumentFragment();
			for (const item of items) {
				const opt = document.createElement('option');
				opt.value = String(item.id);
				opt.textContent = item.nombre;
				frag.appendChild(opt);
			}
			selectEl.appendChild(frag);
			return items;
		}

		// ── Documento ─────────────────────────────────────────────────────

		function obtenerReglaDocumento(tipoId) {
			const nombreTipo = normalizarTexto(tiposDocumento.get(Number(tipoId || 0)) || '');
			if (nombreTipo === 'dni') return {
				maxLength: 8, soloNumeros: true,
				hint: 'DNI: exactamente 8 dígitos numéricos.',
				placeholder: 'Ingrese 8 dígitos de DNI',
				validationMessage: 'Para DNI se requieren 8 dígitos numéricos.',
				regex: /^\d{8}$/, longitudesAutoBusqueda: [8],
			};
			if (nombreTipo === 'pasaporte' || nombreTipo === 'carnet de extranjeria') return {
				maxLength: 12, soloNumeros: false,
				hint: 'Pasaporte/Carnet: 8 a 12 caracteres alfanuméricos.',
				placeholder: 'Ingrese 8-12 caracteres',
				validationMessage: 'Para Pasaporte/Carnet se requieren de 8 a 12 caracteres alfanuméricos.',
				regex: /^[A-Za-z0-9]{8,12}$/, longitudesAutoBusqueda: [8, 9, 10, 11, 12],
			};
			return {
				maxLength: 12, soloNumeros: false,
				hint: 'Documento entre 8 y 12 caracteres alfanuméricos.',
				placeholder: 'Ingrese documento (8 a 12 caracteres)',
				validationMessage: 'Documento inválido. Use de 8 a 12 caracteres alfanuméricos.',
				regex: /^[A-Za-z0-9]{8,12}$/, longitudesAutoBusqueda: [8, 12],
			};
		}

		function limpiarDocumentoSegunRegla(valor, regla) {
			const texto = String(valor || '').trim();
			return regla.soloNumeros
				? texto.replace(/\D/g, '').slice(0, regla.maxLength)
				: texto.replace(/[^A-Za-z0-9]/g, '').toUpperCase().slice(0, regla.maxLength);
		}

		function aplicarReglaDocumento() {
			const regla = obtenerReglaDocumento(tipoDocumentoSelect.value);
			numDocumentoInput.maxLength  = regla.maxLength;
			numDocumentoInput.placeholder = regla.placeholder;
			numDocumentoInput.inputMode  = regla.soloNumeros ? 'numeric' : 'text';
			numDocumentoInput.value = limpiarDocumentoSegunRegla(numDocumentoInput.value, regla);
		}

		function limpiarDatosCaficultor() {
			nombreCaficultorInput.value = '';
			tipoCaficultorInput.value   = '';
			caficultorValido = false;
			numDocumentoInput.setCustomValidity('');
		}

		function setLookupMessage(msg, type = 'neutral') {
			caficultorLookupMsg.innerHTML = msg;
			caficultorLookupMsg.classList.remove('helper-success', 'helper-error');
			if (type === 'success') caficultorLookupMsg.classList.add('helper-success');
			if (type === 'error')   caficultorLookupMsg.classList.add('helper-error');
		}

		async function consultarCaficultor(documento) {
			const { ok, mensaje } = validarDocumentoPorTipoId(tipoDocumentoSelect.value, documento);
			if (!ok) { limpiarDatosCaficultor(); setLookupMessage(mensaje, 'error'); return; }

			const clave = `${tipoDocumentoSelect.value}:${documento}`;
			if (clave === ultimaClaveBusqueda && caficultorValido) return;
			ultimaClaveBusqueda = clave;

			try {
				setLookupMessage('Buscando datos del caficultor...');
				const res = await fetch(`/caficultor/consultar/${encodeURIComponent(documento)}`);
				if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo consultar el caficultor.'));
				const payload = await res.json();
				if (!payload.encontrado || !payload.data) {
					limpiarDatosCaficultor();
					setLookupMessage(`${payload.mensaje || 'Caficultor no encontrado.'} <a href="/nuevo-caficultor" style="text-decoration:underline;">Registrar caficultor</a>`, 'error');
					return;
				}
				nombreCaficultorInput.value = payload.data.nombre_completo;
				tipoCaficultorInput.value   = payload.data.tipo_caficultor;
				caficultorValido = true;
				numDocumentoInput.setCustomValidity('');
				setLookupMessage(payload.mensaje || 'Caficultor encontrado.', 'success');
			} catch (err) {
				limpiarDatosCaficultor();
				setLookupMessage(err.message || 'Error al consultar el caficultor.', 'error');
			}
		}

		function validarDocumentoPorTipoId(tipoId, documento) {
			const id = Number(tipoId || 0);
			if (!id) return { ok: false, mensaje: 'Selecciona primero el tipo de documento.' };
			const regla = obtenerReglaDocumento(id);
			return regla.regex.test(documento)
				? { ok: true, mensaje: '' }
				: { ok: false, mensaje: regla.validationMessage };
		}

		function intentarBusquedaAutomatica() {
			const tipoId   = Number(tipoDocumentoSelect.value || 0);
			const regla    = obtenerReglaDocumento(tipoId);
			const documento = limpiarDocumentoSegunRegla(numDocumentoInput.value, regla);
			numDocumentoInput.value = documento;

			if (!tipoId) {
				limpiarDatosCaficultor();
				setLookupMessage(documento.length ? 'Selecciona primero el tipo de documento.' : '', documento.length ? 'error' : 'neutral');
				return;
			}
			if (!regla.longitudesAutoBusqueda.includes(documento.length)) {
				limpiarDatosCaficultor();
				setLookupMessage(documento.length ? regla.hint : '');
				return;
			}
			if (consultaTimer) clearTimeout(consultaTimer);
			consultaTimer = setTimeout(() => consultarCaficultor(documento), 300);
		}

		async function cargarTiposDocumento() {
			try {
				const res = await fetch('/tipo-documento/listar');
				if (!res.ok) throw new Error('HTTP ' + res.status);
				const tipos = await res.json();
				for (const t of tipos) {
					tiposDocumento.set(Number(t.id), String(t.nombre));
					const opt = document.createElement('option');
					opt.value = String(t.id);
					opt.textContent = t.nombre;
					tipoDocumentoSelect.appendChild(opt);
				}
				const entryDni = [...tiposDocumento.entries()].find(([, n]) => normalizarTexto(n) === 'dni');
				if (entryDni) tipoDocumentoSelect.value = String(entryDni[0]);
				aplicarReglaDocumento();
			} catch (err) { console.error('cargarTiposDocumento:', err); }
		}

		// ── Muestra ───────────────────────────────────────────────────────

		async function cargarTiposGrano() {
			try {
				const res = await fetch('/tipo-grano/listar');
				if (!res.ok) throw new Error('HTTP ' + res.status);
				const tipos = await res.json();
				for (const t of tipos) {
					const opt = document.createElement('option');
					opt.value = String(t.id);
					opt.textContent = t.nombre;
					tipoGranoSelect.appendChild(opt);
				}
			} catch (err) { console.error('cargarTiposGrano:', err); }
		}

		function validarPesoRelacionado(hijoInput, padreInput) {
			const minimo = Number(hijoInput.dataset.porcentajeMinimo);
			const maximo = Number(hijoInput.dataset.porcentajeMaximo || 100);
			const nombre = hijoInput.dataset.nombrePeso;
			const referencia = hijoInput.dataset.referenciaPeso;
			const regla = maximo === 100
				? `Mayor al ${minimo}% del ${referencia}, sin superarlo.`
				: `Mayor al ${minimo}% y como máximo ${maximo}% del ${referencia}.`;
			if (!hijoInput.value) return { mensaje: regla, esError: false };
			if (!esFloatPositivo(hijoInput.value))
				return { mensaje: `El peso ${nombre} debe ser un número positivo (gr.).`, esError: true };
			if (!esFloatPositivo(padreInput.value)) return { mensaje: regla, esError: false };
			// El formulario envía dos decimales: comparar centésimas evita errores
			// de coma flotante justo en los límites porcentuales.
			const valor = Math.round(parseFloat(hijoInput.value) * 100);
			const base = Math.round(parseFloat(padreInput.value) * 100);
			const formatearLimite = porcentaje => (base * porcentaje / 10000).toFixed(4).replace(/0{1,2}$/, '');
			if (valor * 100 <= base * minimo)
				return { mensaje: `El peso ${nombre} debe ser mayor al ${minimo}% del ${referencia} (${formatearLimite(minimo)} gr.).`, esError: true };
			if (valor * 100 > base * maximo)
				return { mensaje: maximo === 100
					? `El peso ${nombre} no puede ser mayor al ${referencia} (${formatearLimite(maximo)} gr.).`
					: `El peso ${nombre} no puede superar el ${maximo}% del ${referencia} (${formatearLimite(maximo)} gr.).`, esError: true };
			return { mensaje: `${regla} Máximo: ${(base * maximo / 10000).toFixed(2)} gr.`, esError: false };
		}

		function actualizarHintLimite(hijoInput, padreInput, hintEl) {
			const { mensaje, esError } = validarPesoRelacionado(hijoInput, padreInput);
			setHint(hintEl, mensaje, esError);
		}

		function validarCamposMuestra() {
			const pt = parseFloat(pesoTrilladoInput.value);
			const pm = parseFloat(pesoMuestraInput.value);
			const pz = parseFloat(pesoTamizadoInput.value);

			if (!esNumSacosValido(numSacosInput.value))   return rechazar(`El número de sacos debe ser un entero entre 1 y ${MAX_SACOS}.`, numSacosInput);
			if (!esFloatPositivo(pesoTotalInput.value))   return rechazar('El peso total debe ser un número positivo (en kg).', pesoTotalInput);
			const maxPesoTotal = parseInt(numSacosInput.value, 10) * 70;
			if (parseFloat(pesoTotalInput.value) > maxPesoTotal) return rechazar(`El peso total no puede superar ${maxPesoTotal} kg (${numSacosInput.value} sacos × 70 kg).`, pesoTotalInput);
			const taraTotal = calcularTara(parseInt(numSacosInput.value, 10));
			if (parseFloat(pesoTotalInput.value) <= taraTotal) return rechazar(`El peso total debe ser mayor a la tara de los sacos: ${taraTotal} kg (${numSacosInput.value} sacos × ${TARA_POR_SACO_KG} kg). Verifique el peso total o el número de sacos.`, pesoTotalInput);
			if (!esEnteroPositivo(humedadInput.value))    return rechazar('La humedad debe ser un número entero (sin decimales).', humedadInput);
			if (parseInt(humedadInput.value, 10) > 30)    return rechazar('La humedad no puede superar 30%.', humedadInput);
			if (!esFloatPositivo(pm))                     return rechazar('Seleccione un peso de muestra (100, 150, 200, 250 o 300 gr.).', pesoMuestraInput);
			if (!esFloatPositivo(pt))                     return rechazar('El peso trillado debe ser un número positivo (en gr.).', pesoTrilladoInput);
			if (pt === pm)                                return rechazar('El peso trillado debe ser diferente al peso de muestra.', pesoTrilladoInput);
			if (pt > pm)                                  return rechazar('El peso trillado no puede ser mayor al peso de muestra.', pesoTrilladoInput);
			const trillado = validarPesoRelacionado(pesoTrilladoInput, pesoMuestraInput);
			if (trillado.esError)                        return rechazar(trillado.mensaje, pesoTrilladoInput);
			if (!esEnteroPositivo(numTamizInput.value))   return rechazar('El número de tamiz debe ser un entero positivo (mínimo 1).', numTamizInput);
			if (!esFloatPositivo(pz))                     return rechazar('El peso tamizado debe ser un número positivo (en gr.).', pesoTamizadoInput);
			const tamizado = validarPesoRelacionado(pesoTamizadoInput, pesoTrilladoInput);
			if (tamizado.esError)                        return rechazar(tamizado.mensaje, pesoTamizadoInput);
			return true;
		}

		// ── Persistencia ──────────────────────────────────────────────────

		const submitErrorEl = document.getElementById('submitError');

		async function registrarEvaluacion() {
			submitErrorEl.textContent = '';
			startBtn.disabled = true;
			startBtn.textContent = 'Registrando...';
			try {
				const body = {
					num_documento: numDocumentoInput.value.trim(),
					num_sacos:     parseInt(numSacosInput.value, 10),
					peso_bruto:    redondear2(pesoTotalInput.value),
					humedad:       parseInt(humedadInput.value, 10),
					peso_muestra:  redondear2(pesoMuestraInput.value),
					peso_trillado: redondear2(pesoTrilladoInput.value),
					num_tamiz:     parseInt(numTamizInput.value, 10),
					peso_tamizado: redondear2(pesoTamizadoInput.value),
					tipo_grano_id: parseInt(tipoGranoSelect.value, 10),
				};
				const res = await fetch('/evaluacion/registrar', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify(body),
				});
				if (!res.ok) {
					throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo registrar la evaluación.'));
				}
				const { data } = await res.json();
				sessionStorage.setItem('coffeeren.evaluacion', JSON.stringify(data));
				window.location.href = `/monitoreo/${encodeURIComponent(data.evaluacion_id)}`;
			} catch (err) {
				const msg = err.message || 'Error inesperado. Intente nuevamente.';
				if (msg.includes('precios de café')) {
					CoffeePrecios.avisar();  // mismo texto que el resto, según el rol
				} else {
					submitErrorEl.textContent = msg;
				}
				startBtn.disabled = false;
				startBtn.textContent = 'Iniciar clasificación y monitoreo';
			}
		}

		function clearAll() {
			form.reset();
			limpiarDatosCaficultor();
			setLookupMessage('');
			ultimaClaveBusqueda = '';
			aplicarReglaDocumento();
			for (const h of [numSacosHint, pesoTotalHint, humedadHint, pesoMuestraHint,
			                  pesoTrilladoHint, pesoTamizadoHint]) setHint(h, '');
		}

		function validateForm() {
			for (const f of form.querySelectorAll('input[required], select[required]')) {
				if (!f.value.trim()) { f.reportValidity(); return false; }
			}
			if (!caficultorValido) {
				numDocumentoInput.setCustomValidity('Debe consultar y validar un caficultor registrado para continuar');
				numDocumentoInput.reportValidity();
				numDocumentoInput.setCustomValidity('');
				return false;
			}
			return validarCamposMuestra();
		}

		// ── Eventos ───────────────────────────────────────────────────────

		tipoDocumentoSelect.addEventListener('change', () => {
			aplicarReglaDocumento();
			ultimaClaveBusqueda = '';
			limpiarDatosCaficultor();
			setLookupMessage('');
			if (numDocumentoInput.value) intentarBusquedaAutomatica();
		});

		numDocumentoInput.addEventListener('input', () => {
			numDocumentoInput.setCustomValidity('');
			ultimaClaveBusqueda = '';
			limpiarDatosCaficultor();
			intentarBusquedaAutomatica();
		});

		numSacosInput.addEventListener('input', () => {
			validarInline(numSacosInput, esNumSacosValido, numSacosHint, `Debe ser un entero entre 1 y ${MAX_SACOS}.`);
			pesoTotalInput.dispatchEvent(new Event('input'));
		});

		pesoTotalInput.addEventListener('input', () => {
			if (!pesoTotalInput.value) { setHint(pesoTotalHint, ''); pesoMuestraInput.dispatchEvent(new Event('input')); return; }
			if (!esFloatPositivo(pesoTotalInput.value)) {
				setHint(pesoTotalHint, 'Debe ser un número positivo (kg).', true);
			} else if (esEnteroPositivo(numSacosInput.value)) {
				const maxKg  = parseInt(numSacosInput.value, 10) * 70;
				const taraKg = calcularTara(parseInt(numSacosInput.value, 10));
				if (parseFloat(pesoTotalInput.value) > maxKg) {
					setHint(pesoTotalHint, `No puede superar ${maxKg} kg (${numSacosInput.value} sacos × 70 kg).`, true);
				} else if (parseFloat(pesoTotalInput.value) <= taraKg) {
					setHint(pesoTotalHint, `Debe ser mayor a la tara de los sacos: ${taraKg} kg (${numSacosInput.value} sacos × ${TARA_POR_SACO_KG} kg).`, true);
				} else {
					setHint(pesoTotalHint, `Máximo: ${maxKg} kg.`);
				}
			} else {
				setHint(pesoTotalHint, '');
			}
			pesoMuestraInput.dispatchEvent(new Event('input'));
		});

		humedadInput.addEventListener('input', () => {
			if (!humedadInput.value)              { setHint(humedadHint, ''); return; }
			if (!esEnteroPositivo(humedadInput.value)) setHint(humedadHint, 'Debe ser un número entero (sin decimales).', true);
			else if (parseInt(humedadInput.value, 10) > 30) setHint(humedadHint, 'La humedad no puede superar 30%.', true);
			else                                   setHint(humedadHint, '');
		});

		pesoMuestraInput.addEventListener('input', () => {
			setHint(pesoMuestraHint, '');
			actualizarHintLimite(pesoTrilladoInput, pesoMuestraInput, pesoTrilladoHint);
		});

		pesoTrilladoInput.addEventListener('input', () => {
			actualizarHintLimite(pesoTrilladoInput, pesoMuestraInput, pesoTrilladoHint);
			actualizarHintLimite(pesoTamizadoInput, pesoTrilladoInput, pesoTamizadoHint);
		});

		pesoTamizadoInput.addEventListener('input', () =>
			actualizarHintLimite(pesoTamizadoInput, pesoTrilladoInput, pesoTamizadoHint));

		forzarEntero(numSacosInput);
		forzarEntero(humedadInput);
		[pesoTotalInput, pesoTrilladoInput, pesoTamizadoInput]
			.forEach(forzar2Decimales);

		bloquearCaracteresNumericos(numSacosInput, true);
		bloquearCaracteresNumericos(humedadInput, true);
		[pesoTotalInput, pesoTrilladoInput, pesoTamizadoInput]
			.forEach(i => bloquearCaracteresNumericos(i));

		startBtn.addEventListener('click', async () => {
			// Sin precios de hoy no se puede pasar al monitoreo. Se vuelve a
			// consultar aquí: pudieron registrarse después de abrir la página.
			if (await CoffeePrecios.avisarSiFaltan()) return;
			if (!validateForm()) return;

			// Verificar que el sensor ultrasónico detecta la muestra en la banda
			startBtn.disabled = true;
			startBtn.textContent = 'Verificando sensor...';
			try {
				const res = await fetch('/arduino/estado');
				if (!res.ok) throw new Error('Error del servidor');
				const estado = await res.json();
				if (!estado.listo) {
					CoffeeModal.warning(estado.mensaje || 'Debe cerrar la tapa luego de haber ingresado los granos de café para continuar al monitoreo.');
					startBtn.disabled = false;
					startBtn.textContent = 'Iniciar clasificación y monitoreo';
					return;
				}
			} catch {
				CoffeeModal.warning('No se pudo verificar el sensor Arduino. Revise la conexión USB.');
				startBtn.disabled = false;
				startBtn.textContent = 'Iniciar clasificación y monitoreo';
				return;
			}

			registrarEvaluacion();
		});
		clearBtn.addEventListener('click', clearAll);


		cargarTiposDocumento();
		cargarTiposGrano();
		// El pago se calcula con los precios del día: sin precios de hoy el
		// backend rechaza el registro. Se avisa al abrir la página para no llenar
		// la ficha en vano.
		async function mostrarAvisosRegistro() {
			if (localStorage.getItem('coffeeren.pruebaPendiente') === '1') {
				localStorage.removeItem('coffeeren.pruebaPendiente');
				await CoffeeModal.info(
					'Antes de iniciar el monitoreo, se recomienda comprobar el sistema mediante el botón Prueba.',
					'Prueba del sistema'
				);
			}

			await CoffeePrecios.avisarSiFaltan();
		}

		mostrarAvisosRegistro();
	})();
