	(() => {
		// ── Datos de la muestra ───────────────────────────────────────────────
		const storedEval = sessionStorage.getItem('coffeeren.evaluacion');
		const sample     = storedEval ? JSON.parse(storedEval) : null;

		const sampleDni            = document.getElementById('sampleDni');
		const sampleName           = document.getElementById('sampleName');
		const sampleTipoCaficultor = document.getElementById('sampleTipoCaficultor');
		const sampleTamiz          = document.getElementById('sampleTamiz');
		const sampleGrano          = document.getElementById('sampleGrano');
		const sampleSacos          = document.getElementById('sampleSacos');
		const samplePeso           = document.getElementById('samplePeso');
		const timerEl              = document.getElementById('sessionTimer');

		const totalGrainsEl   = document.getElementById('totalGrains');
		const totalDefectsEl  = document.getElementById('totalDefects');
		const totalSanosEl    = document.getElementById('totalSanos');
		const iaPerformanceEl = document.getElementById('iaPerformance');
		const negroValueEl    = document.getElementById('defectosValue');
		const negroBarEl      = document.getElementById('defectosBar');
		const sanoValueEl     = document.getElementById('sanosValue');
		const sanoBarEl       = document.getElementById('sanosBar');
		const eventLog        = document.getElementById('eventLog');
		const foreignAlertEl  = document.getElementById('foreignAlert');
		const foreignCountEl  = document.getElementById('foreignCount');
		const finishBtn         = document.getElementById('finishBtn');
		const startBtn          = document.getElementById('startBtn');

		const chipCamara  = document.getElementById('chipCamara');
		const chipFaja    = document.getElementById('chipFaja');
		const chipArduino = document.getElementById('chipArduino');
		const chipModelo  = document.getElementById('chipModelo');

		if (sample) {
			sampleDni.textContent            = sample.num_documento    || '-';
			sampleName.textContent           = sample.caficultor_nombre || '-';
			sampleTipoCaficultor.textContent = sample.tipo_caficultor   || '-';
			sampleTamiz.textContent          = sample.num_tamiz ? `N° ${sample.num_tamiz}` : '-';
			sampleGrano.textContent          = sample.tipo_grano_nombre || '-';
			sampleSacos.textContent          = sample.num_sacos ?? '-';
			samplePeso.textContent           = sample.peso_bruto != null ? `${sample.peso_bruto} kg` : '-';
		} else {
			document.querySelectorAll('.strip-field strong').forEach(el => { el.textContent = '—'; });
		}

		// ── Cámara ────────────────────────────────────────────────────────────
		const cameraLoadingEl = document.getElementById('cameraLoading');
		const cameraStreamEl  = document.getElementById('cameraStream');
		const cameraErrorEl   = document.getElementById('cameraError');
		const cameraErrorMsg  = document.getElementById('cameraErrorMsg');
		const fpsBadgeEl      = document.getElementById('fpsBadge');

		let connectTimeout = null;
		let frameTimeout   = null;   // reintento del bucle de frames — debe poder cancelarse desde detenerStream()
		let streamActivo   = false;
		let _ultimoBlobUrl = null;

		function mostrarErrorCamara(msg) {
			clearTimeout(connectTimeout);
			cameraLoadingEl.style.display = 'none';
			cameraStreamEl.style.display  = 'none';
			cameraErrorEl.style.display   = 'flex';
			if (fpsBadgeEl) fpsBadgeEl.style.display = 'none';
			if (msg) cameraErrorMsg.textContent = msg;
		}

		function iniciarStream() {
			cameraLoadingEl.style.display = 'flex';
			cameraStreamEl.style.display  = 'none';
			cameraErrorEl.style.display   = 'none';

			streamActivo = true;
			let isFirstFrame = true;

			const refrescarFrame = async () => {
				if (!streamActivo) return;
				try {
					const res = await fetch('/video/frame');
					if (!streamActivo) return;
					if (res.status === 503) { frameTimeout = setTimeout(refrescarFrame, 33); return; }
					if (!res.ok) throw new Error('Error obteniendo frame');
					const url = URL.createObjectURL(await res.blob());
					if (_ultimoBlobUrl) URL.revokeObjectURL(_ultimoBlobUrl);   // liberar el frame anterior
					_ultimoBlobUrl = url;
					cameraStreamEl.src = url;
					if (isFirstFrame) {
						isFirstFrame = false;
						clearTimeout(connectTimeout);
						cameraLoadingEl.style.display = 'none';
						cameraStreamEl.style.display  = 'block';
						if (fpsBadgeEl) fpsBadgeEl.style.display = 'block';
					}
					frameTimeout = setTimeout(refrescarFrame, 33);
				} catch {
					if (isFirstFrame) { clearTimeout(connectTimeout); mostrarErrorCamara('No se pudo conectar con el video.'); }
				}
			};

			connectTimeout = setTimeout(() => {
				if (isFirstFrame) mostrarErrorCamara('Tiempo de espera agotado. Verifique la cámara.');
			}, 10000);

			refrescarFrame();
		}

		function detenerStream() {
			streamActivo = false;
			clearTimeout(connectTimeout);
			clearTimeout(frameTimeout);
			if (_ultimoBlobUrl) { URL.revokeObjectURL(_ultimoBlobUrl); _ultimoBlobUrl = null; }
			cameraStreamEl.src            = '';
			cameraStreamEl.style.display  = 'none';
			cameraLoadingEl.style.display = 'none';
			cameraErrorEl.style.display   = 'none';
			if (fpsBadgeEl) fpsBadgeEl.style.display = 'none';
		}

		// ── Arranque automático al cargar ────────────────────────────────────
		(async () => {
			try {
				const res = await fetch('/video/status');
				if (!res.ok) throw new Error();
				const { activo, evaluacion_id: loteDe } = await res.json();
				if (loteDe && loteDe !== EVALUACION_ID) {
					const resumen = await fetch(`/evaluacion/${encodeURIComponent(loteDe)}/resumen`)
						.then(res => res.ok ? res.json() : null)
						.catch(() => null);
					const referencia = resumen?.caficultor_nombre && resumen?.fecha
						? `otra evaluación en monitoreo (${resumen.caficultor_nombre}, ${resumen.fecha})`
						: 'una evaluación anterior en monitoreo';
					const aceptar = await CoffeeModal.confirm({
						title: 'Otra evaluación en monitoreo',
						message: `Hay ${referencia}. ¿Detenerla para iniciar esta muestra? Su conteo se perderá.`,
						okText: 'Detener e iniciar esta muestra',
						cancelText: 'Cancelar',
					});
					if (!aceptar) return;
					await detenerCapturaDeEvaluacion(loteDe, true);
					await iniciarCaptura();
				} else if (activo && loteDe === EVALUACION_ID) {
					// YOLO
					capturandoYOLO        = true;
					elapsedSeconds        = 0;
					iniciarStream();
					iniciarTimer();
					iniciarPoll();
					appendLog('Cámara conectada. Monitoreo en curso.', 'ok');
				} else {
					if (activo) await detenerCapturaDeEvaluacion();
					await iniciarCaptura();
				}
			} catch (err) {
				appendLog(err.message || 'No se pudo verificar el servidor.', 'error');
			}
		})();

		// ── Estado compartido ─────────────────────────────────────────────────
		let monitoreoActivo       = true;
		let capturandoYOLO        = false;
		let finalizando           = false;
		let elapsedSeconds        = 0;
		let conteoActual          = {};
		let gruposActual          = {};
		let totalDefectosActual   = 0;
		let totalSanosActual      = 0;
		let reporteActual         = null;
		let timerInterval         = null;
		let conteoInterval        = null;

		// ── Estado de tapa ────────────────────────────────────────────────────
		let tapaCerrada     = true;  // ya fue validada antes de iniciar monitoreo
		let msAperturaTapa  = 0;     // Date.now() cuando se abrió
		let segAperturaTapa = 0;     // elapsedSeconds cuando se abrió
		let incidencias     = [];    // [{seg_apertura, seg_cierre, duracion_s}]

		// ── UI helpers ────────────────────────────────────────────────────────
		// Registro cronológico ACUMULATIVO: cada evento se apila (lo más reciente
		// arriba) con su marca mm:ss y su severidad. Antes se hacía
		// `eventLog.innerHTML = ...`, que dejaba visible un único mensaje y borraba
		// toda la traza del lote — el operario no podía reconstruir qué pasó.
		const LOG_MAX_ENTRADAS = 80;

		// `segundo` llega en los eventos del backend: es el segundo real del lote
		// medido contra su inicio. Al recargar la pestaña a mitad de lote el
		// cronómetro del navegador vuelve a 0, así que usar elapsedSeconds ahí
		// fecharía mal toda la traza previa.
		function appendLog(message, severidad = 'info', imagenUrl = null, segundo = null) {
			if (!eventLog) return;

			const item = document.createElement('p');
			item.className = `log-item log-${severidad}`;

			const marca = document.createElement('time');
			marca.className = 'log-time';
			marca.textContent = formatTimer(segundo != null ? segundo : elapsedSeconds);
			item.appendChild(marca);

			// textContent, nunca innerHTML: el mensaje puede venir del backend.
			const texto = document.createElement('span');
			texto.className = 'log-msg';
			texto.textContent = message;
			item.appendChild(texto);

			if (imagenUrl) {
				const link = document.createElement('a');
				link.href      = imagenUrl;
				link.target    = '_blank';
				link.rel       = 'noopener';
				link.className = 'log-thumb';
				link.title     = 'Ver evidencia completa';
				const img = document.createElement('img');
				img.src     = imagenUrl;
				img.alt     = 'Evidencia del objeto detectado';
				img.loading = 'lazy';
				link.appendChild(img);
				item.appendChild(link);
			}

			eventLog.insertAdjacentElement('afterbegin', item);
			while (eventLog.children.length > LOG_MAX_ENTRADAS) {
				eventLog.lastElementChild.remove();
			}
		}

		function formatTimer(v) {
			return `${String(Math.floor(v / 60)).padStart(2, '0')}:${String(v % 60).padStart(2, '0')}`;
		}

		// ── Estados en vivo ───────────────────────────────────────────────────
		// Traduce a texto los estados que el sistema ya conocía pero no mostraba.
		// No hace peticiones propias: se alimenta de las respuestas del poll.
		function _pintarChip(el, texto, estado) {
			if (!el) return;
			el.textContent    = texto;
			el.dataset.estado = estado;   // ok | alerta | error | neutro
		}

		function actualizarChipsCamara(status) {
			if (status.camara_desconectada)  _pintarChip(chipCamara, 'Cámara: desconectada', 'error');
			else if (status.activo)          _pintarChip(chipCamara, 'Cámara: en vivo', 'ok');
			else                             _pintarChip(chipCamara, 'Cámara: detenida', 'alerta');
			_pintarChip(chipModelo, `Modelo: ${status.modelo || '—'}`, status.activo ? 'ok' : 'neutro');
		}

		function actualizarChipFaja(activa) {
			_pintarChip(chipFaja, activa ? 'Faja: en marcha' : 'Faja: detenida', activa ? 'ok' : 'alerta');
		}

		function actualizarUIdesdeConteo(totalDefectos = 0, totalSanos = 0, grupos = {}) {
			const totalGranos = totalDefectos + totalSanos;
			const pct = totalGranos > 0 ? Math.round((totalDefectos / totalGranos) * 100) : 0;

			totalGrainsEl.textContent   = totalGranos;
			totalDefectsEl.textContent  = totalDefectos;
			totalSanosEl.textContent    = totalSanos;
			iaPerformanceEl.textContent = pct + '%';

			negroValueEl.textContent  = totalDefectos;
			sanoValueEl.textContent   = totalSanos;
			negroBarEl.style.width    = pct + '%';
			sanoBarEl.style.width     = (100 - pct) + '%';
		}

		// Objetos que el modelo nunca reconoció como grano (piedra, pajilla, palito):
		// tracker.py los enmarca en azul sobre el video, el servo los desvía al canal
		// de defecto y cuentan como defecto (materia extraña). Aquí solo se
		// mantiene el contador: el AVISO de cada objeto llega como evento del
		// backend (con su segundo real y la foto del recorte), no se infiere
		// restando contadores entre polls.
		function avisarDesconocidos(n = 0) {
			if (foreignCountEl) foreignCountEl.textContent = n;
			if (foreignAlertEl) foreignAlertEl.hidden = n === 0;
		}

		// Lote nuevo: POST /video/iniciar reinicia la secuencia de eventos en el
		// backend, así que el cursor del cliente TIENE que volver a 0 — si no, los
		// primeros eventos del lote nuevo caerían por debajo del cursor viejo y
		// nunca se mostrarían.
		function resetearEstadoLote() {
			cursorEventos       = 0;
			_primerGranoAvisado = null;
			_inactividadAvisada = false;
			if (finishBtn) finishBtn.classList.remove('btn-atencion');
			if (foreignCountEl) foreignCountEl.textContent = '0';
			if (foreignAlertEl) foreignAlertEl.hidden = true;
		}

		// El backend ya calculaba segundos_sin_deteccion y el frontend lo descartaba.
		// Aquí se traduce en dos avisos: confirmación de que el conteo arrancó, y
		// alerta de racha sin granos (el operario decide si el lote terminó).
		const SEG_INACTIVIDAD = 10;
		// null = todavía sin sincronizar con el backend. Al recargar la pestaña a
		// mitad de lote el primer poll adopta el estado en silencio, en vez de
		// anunciar como recién ocurrido lo que ya estaba contado.
		let _primerGranoAvisado = null;
		let _inactividadAvisada = false;

		function avisarActividad(totalGranos = 0, segundosSinDeteccion = null) {
			if (_primerGranoAvisado === null) {
				_primerGranoAvisado = totalGranos > 0;
			} else if (!_primerGranoAvisado && totalGranos > 0) {
				_primerGranoAvisado = true;
				appendLog('Primer grano detectado. Conteo en marcha.', 'ok');
			}
			if (segundosSinDeteccion == null || !_primerGranoAvisado) return;

			if (segundosSinDeteccion >= SEG_INACTIVIDAD) {
				if (!_inactividadAvisada) {
					_inactividadAvisada = true;
					appendLog(
						`Sin granos hace ${SEG_INACTIVIDAD} s — si el lote terminó, presione Finalizar monitoreo.`,
						'alerta',
					);
					if (finishBtn) finishBtn.classList.add('btn-atencion');
				}
			} else if (_inactividadAvisada) {
				_inactividadAvisada = false;
				if (finishBtn) finishBtn.classList.remove('btn-atencion');
			}
		}

		// ── Poll unificado ────────────────────────────────────────────────────
		// Una sola implementación para conteo + estado de cámara + eventos del
		// backend + tapa. Antes este bloque estaba duplicado (arranque automático
		// e iniciarCaptura) y cada añadido había que hacerlo dos veces.
		let cursorEventos = 0;

		async function pollEstado() {
			if (!capturandoYOLO || finalizando) return;
			try {
				const [rConteo, rStatus, rEventos] = await Promise.all([
					fetch('/video/lote/conteo'),
					fetch('/video/status'),
					fetch(`/video/eventos?desde=${cursorEventos}`),
				]);

				if (rStatus.ok) {
					const status = await rStatus.json();
					actualizarChipsCamara(status);
					// Velocidad del modelo (promedio del último segundo en el servidor),
					// no la del refresco de imágenes en el navegador.
					if (fpsBadgeEl && status.fps != null) fpsBadgeEl.textContent = `${Math.round(status.fps)} FPS`;
					if (status.camara_desconectada) {
						_manejarDesconexionCamara(status.error);
						return;
					}
				}

				if (rConteo.ok) {
					const data = await rConteo.json();
					conteoActual        = data.conteo;
					gruposActual        = data.conteo_agrupado ?? {};
					totalDefectosActual = data.total_defectos ?? 0;
					totalSanosActual    = data.total_sanos ?? 0;
					actualizarUIdesdeConteo(totalDefectosActual, totalSanosActual, gruposActual);
					avisarDesconocidos(data.total_desconocidos ?? 0);
					avisarActividad(data.total_granos ?? 0, data.segundos_sin_deteccion);
				}

				if (rEventos.ok) {
					const { eventos, cursor } = await rEventos.json();
					(eventos || []).forEach(ev => appendLog(ev.mensaje, ev.severidad, ev.imagen_url, ev.segundo));
					if (cursor != null) cursorEventos = cursor;
				}

				await _verificarTapa();
			} catch (e) {
				console.error('Error en el poll de monitoreo:', e);
			}
		}

		function iniciarPoll() {
			clearInterval(conteoInterval);
			conteoInterval = setInterval(pollEstado, 1500);
		}

		function iniciarTimer() {
			clearInterval(timerInterval);
			timerInterval = setInterval(() => {
				elapsedSeconds += 1;
				if (timerEl) timerEl.textContent = formatTimer(elapsedSeconds);
			}, 1000);
		}

		// ── Desconexión de cámara ─────────────────────────────────────────────
		function _manejarDesconexionCamara(errorMsg) {
			if (finalizando) return;
			capturandoYOLO = false;
			clearInterval(timerInterval);
			clearInterval(conteoInterval);
			detenerStream();

			const mensaje = errorMsg || 'Desconexión con cámara. La clasificación se ha detenido.';
			mostrarErrorCamara(mensaje);
			appendLog(mensaje, 'error');
			_pintarChip(chipCamara, 'Cámara: desconectada', 'error');

			if (startBtn) { startBtn.style.display = 'inline-flex'; startBtn.textContent = 'Reintentar captura'; }
		}

		// ── Verificación de tapa durante monitoreo ───────────────────────────
		// Solo REGISTRA las aperturas como incidencias — nunca detiene la faja.
		// La faja corre hasta que el evaluador presiona Regresar o Finalizar;
		// él decide qué hacer con el lote según las incidencias registradas.
		async function _verificarTapa() {
			try {
				const rTapa = await fetch('/arduino/estado');
				if (!rTapa.ok) { _pintarChip(chipArduino, 'Arduino: sin respuesta', 'error'); return; }
				const tapa = await rTapa.json();
				if (!tapa.conectado) { _pintarChip(chipArduino, 'Arduino: sin conexión', 'error'); return; }
				_pintarChip(chipArduino, 'Arduino: conectado', 'ok');

				if (tapaCerrada && !tapa.listo) {
					tapaCerrada     = false;
					msAperturaTapa  = Date.now();
					segAperturaTapa = elapsedSeconds;
					appendLog('Tapa abierta — se registrará como incidencia.', 'alerta');
				} else if (!tapaCerrada && tapa.listo) {
					tapaCerrada = true;
					const segsAbierta = Math.round((Date.now() - msAperturaTapa) / 1000);
					incidencias.push({ seg_apertura: segAperturaTapa, seg_cierre: elapsedSeconds, duracion_s: segsAbierta });
					appendLog(`Tapa cerrada — estuvo abierta ${segsAbierta}s.`, 'ok');
				}
			} catch { /* ignorar error de tapa */ }
		}

		// ── Faja (Arduino) ────────────────────────────────────────────────────
		async function iniciarFaja() {
			try {
				const res  = await fetch('/arduino/motor/iniciar', { method: 'POST' });
				const data = await res.json();
				appendLog(data.mensaje || 'Faja iniciada.', data.activo ? 'ok' : 'error');
				actualizarChipFaja(Boolean(data.activo));
			} catch {
				appendLog('No se pudo iniciar la faja. Verifique la conexión Arduino.', 'error');
				actualizarChipFaja(false);
			}
		}

		async function detenerFaja() {
			try {
				await fetch('/arduino/motor/detener', { method: 'POST', keepalive: true });
				actualizarChipFaja(false);
			} catch {
				appendLog('No se pudo detener la faja. Verifique la conexión Arduino.', 'error');
			}
		}

		// ── Esperar primer frame ──────────────────────────────────────────────
		async function esperarPrimerFrame(timeoutMs = 15000) {
			const inicio = Date.now();
			while (Date.now() - inicio < timeoutMs) {
				const res = await fetch('/video/frame').catch(() => null);
				if (res && res.ok) return true;
				await new Promise(r => setTimeout(r, 300));
			}
			return false;
		}

		// ── Captura YOLO ──────────────────────────────────────────────────────
		async function iniciarCaptura() {
			if (capturandoYOLO || finalizando) return;

			if (startBtn) { startBtn.style.display = 'none'; }

			try {
				// 1. Iniciar YOLO + cámara primero. El id de evaluación viaja al
				// backend para que los eventos y las evidencias del lote queden
				// asociados a esta evaluación.
				appendLog('Cargando modelo y conectando cámara...');
				const res = await fetch('/video/iniciar', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ evaluacion_id: EVALUACION_ID }),
				});
				if (!res.ok) {
					throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo iniciar la captura.'));
				}

				// 2. Esperar a que la cámara produzca el primer frame real
				appendLog('Esperando primer frame de la cámara...');
				const camaraLista = await esperarPrimerFrame(15000);
				if (!camaraLista) throw new Error('La cámara no respondió a tiempo. Verifique la conexión.');

				// 3. Cámara confirmada — arrancar faja
				appendLog('Cámara activa. Arrancando faja transportadora...', 'ok');
				await iniciarFaja();

				capturandoYOLO        = true;
				elapsedSeconds        = 0;
				resetearEstadoLote();

				appendLog('Faja en marcha. Captura YOLO activa.', 'ok');
				iniciarStream();
				iniciarTimer();
				iniciarPoll();

			} catch (err) {
				appendLog('Error: ' + err.message, 'error');
				if (startBtn) { startBtn.style.display = 'inline-flex'; startBtn.textContent = 'Reintentar captura'; }
				await detenerFaja();
			}
		}

		async function detenerCapturaDeEvaluacion(evaluacionId = EVALUACION_ID, descartarLote = false) {
			const res = await fetch('/video/detener', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ evaluacion_id: evaluacionId, descartar_lote: descartarLote }),
			});
			if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo detener el monitoreo.'));
		}

		async function detenerCaptura() {
			clearInterval(timerInterval);
			clearInterval(conteoInterval);
			await detenerFaja();
			await detenerCapturaDeEvaluacion();
			capturandoYOLO = false;
			detenerStream();
		}

		async function generarReporte() {
			try {
				appendLog('Generando reporte...');
				const res = await fetch('/video/lote/generar-reporte', { method: 'POST' });
				if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo generar el reporte.'));
				reporteActual = await res.json();
				appendLog(`Reporte: ${reporteActual.total_defectos} defectos equiv.`, 'ok');
			} catch (err) {
				appendLog('Error al generar reporte: ' + err.message, 'error');
			}
		}

		// ── Overlay de finalización ───────────────────────────────────────────
		const overlay       = document.getElementById('finalizacionOverlay');
		const finTitulo     = document.getElementById('finTitulo');
		const finDescripcion= document.getElementById('finDescripcion');
		const finSpinner    = document.getElementById('finSpinner');
		const finCheck      = document.getElementById('finCheck');
		const finResultado  = document.getElementById('finResultado');
		const btnIrAnalisis = document.getElementById('btnIrAnalisis');

		function _pasoPendiente(n) {
			const ico = document.getElementById(`paso${n}ico`);
			const row = document.getElementById(`paso${n}`);
			if (ico) ico.textContent = '⏳';
			if (row) row.style.color = 'var(--muted-foreground)';
		}
		function _pasoOk(n) {
			const ico = document.getElementById(`paso${n}ico`);
			const row = document.getElementById(`paso${n}`);
			if (ico) ico.textContent = '✅';
			if (row) row.style.color = 'var(--foreground)';
		}
		function _pasoError(n) {
			const ico = document.getElementById(`paso${n}ico`);
			if (ico) ico.textContent = '❌';
		}

		function mostrarOverlay(automatico) {
			overlay.style.display = 'flex';
			document.body.style.overflow = 'hidden';
			finTitulo.textContent = automatico
				? 'Clasificación finalizada automáticamente'
				: 'Finalizando monitoreo...';
			finDescripcion.textContent = automatico
				? 'No se detectaron nuevos granos en los últimos 10 segundos. El sistema detuvo el proceso y está guardando los resultados.'
				: 'Por favor, espera mientras se guardan los datos y se genera el reporte.';
			[1,2,3].forEach(_pasoPendiente);
			finSpinner.style.display = 'block';
			finCheck.style.display   = 'none';
			finResultado.style.display = 'none';
			btnIrAnalisis.disabled = true;
			btnIrAnalisis.style.cursor = 'not-allowed';
			btnIrAnalisis.style.background = 'color-mix(in oklab,var(--primary) 40%,transparent)';
			btnIrAnalisis.textContent = 'Procesando...';
		}

		function completarOverlay(codigo, pesoGramos = 0) {
			finSpinner.style.display = 'none';
			finCheck.style.display   = 'block';
			finTitulo.textContent    = 'Evaluación completada';
			finDescripcion.textContent = 'Pesa el grano bueno separado e ingresa el valor para calcular el factor de rendimiento.';

			document.getElementById('resCode').textContent     = codigo || '—';
			document.getElementById('resGranos').textContent   = Object.values(conteoActual).reduce((a,b)=>a+b,0);
			document.getElementById('resPeso').textContent     = `${Number(pesoGramos).toFixed(2)} g`;
			// Sin celda de carga no hay lectura: ocultar la fila de báscula
			document.getElementById('resPesoRow').style.display = pesoGramos > 0 ? '' : 'none';
			finResultado.style.display = 'block';

			mostrarFormPesoBueno();
			btnIrAnalisis.textContent = 'Registra el peso bueno para continuar';
		}

		// ── Peso de grano bueno (ingreso manual) + factor de rendimiento ──────
		let pesoTamizadoMax   = null;

		async function mostrarFormPesoBueno() {
			document.getElementById('finPesoForm').style.display = 'block';
			document.getElementById('inputPesoBueno').focus();
			try {
				const res = await fetch(`/evaluacion/${EVALUACION_ID}/resumen`);
				if (res.ok) {
					const data = await res.json();
					pesoTamizadoMax = Number(data.peso_tamizado);
					document.getElementById('inputPesoBueno').max = Math.floor(pesoTamizadoMax);
					document.getElementById('pesoBuenoHint').textContent =
						`Gramos enteros. El peso de grano bueno no puede superar los ${Math.floor(pesoTamizadoMax)} g (peso tamizado).`;
				}
			} catch { /* sin resumen, el backend valida igual */ }
		}

		function _habilitarIrAnalisis() {
			btnIrAnalisis.disabled = false;
			btnIrAnalisis.style.cursor = 'pointer';
			btnIrAnalisis.style.background = 'var(--primary)';
			btnIrAnalisis.style.color = 'var(--primary-foreground, #fff)';
			btnIrAnalisis.textContent = 'Ir al análisis →';
		}

		async function guardarPesoBueno() {
			const input   = document.getElementById('inputPesoBueno');
			const errorEl = document.getElementById('pesoBuenoError');
			const btn     = document.getElementById('btnGuardarPesoBueno');
			errorEl.style.display = 'none';

			const validacion = CoffeeValidators.pesoBueno(input.value, pesoTamizadoMax);
			if (!validacion.valido) {
				errorEl.textContent = validacion.mensaje;
				errorEl.style.display = 'block';
				return;
			}
			const peso = validacion.peso;

			btn.disabled = true;
			btn.textContent = 'Calculando...';
			try {
				const res = await fetch(`/evaluacion/${EVALUACION_ID}/completar`, {
					method: 'PATCH',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ peso_bueno: peso }),
				});
				if (!res.ok) {
					throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo calcular el rendimiento.'));
				}
				const data = await res.json();
				document.getElementById('resFactor').textContent    = Number(data.factor_rendimiento).toFixed(2);
				document.getElementById('resPago').textContent      = Number(data.pago).toFixed(2);
				document.getElementById('finRendimiento').style.display = 'block';
				document.getElementById('finPesoForm').style.display = 'none';
				finDescripcion.textContent = 'Rendimiento calculado. Revisa el resumen antes de continuar al análisis.';
				appendLog(`Peso bueno: ${peso} g — factor de rendimiento ${Number(data.factor_rendimiento).toFixed(2)}`, 'ok');
				_habilitarIrAnalisis();
			} catch (err) {
				errorEl.textContent = err.message;
				errorEl.style.display = 'block';
				btn.disabled = false;
				btn.textContent = 'Calcular rendimiento';
				// Si el cálculo falla por configuración (ej. sin precios de café),
				// no bloquear al evaluador: permitir continuar sin rendimiento.
				_habilitarIrAnalisis();
				btnIrAnalisis.textContent = 'Continuar sin rendimiento →';
			}
		}

		document.getElementById('btnGuardarPesoBueno').addEventListener('click', guardarPesoBueno);
		document.getElementById('inputPesoBueno').addEventListener('keydown', (e) => {
			if (e.key === 'Enter') { e.preventDefault(); guardarPesoBueno(); }
		});

		function errorOverlay(msg) {
			finSpinner.style.display = 'none';
			finTitulo.textContent    = 'Error al finalizar';
			finDescripcion.textContent = msg || 'Ocurrió un error. Intenta nuevamente.';
			_pasoError(3);
			btnIrAnalisis.disabled = false;
			btnIrAnalisis.style.cursor = 'pointer';
			btnIrAnalisis.style.background = 'var(--destructive, #dc2626)';
			btnIrAnalisis.style.color = '#fff';
			btnIrAnalisis.textContent = 'Cerrar e intentar de nuevo';
			btnIrAnalisis.onclick = () => {
				overlay.style.display = 'none';
				document.body.style.overflow = '';
				finalizando = false;
				if (finishBtn) { finishBtn.disabled = false; finishBtn.textContent = 'Finalizar monitoreo'; }
				btnIrAnalisis.onclick = null;
			};
		}

		btnIrAnalisis.addEventListener('click', () => {
			if (!btnIrAnalisis.onclick) {
				finalizando    = false;
				monitoreoActivo = false;
				window.location.href = `/analisis/${EVALUACION_ID}`;
			}
		});

		// ── Finalización compartida (manual y automática) ─────────────────────
		async function finalizarMonitoreo(automatico = false) {
			if (finalizando) return;
			finalizando = true;

			clearInterval(timerInterval);
			clearInterval(conteoInterval);

			mostrarOverlay(automatico);

			// Paso 1: detener faja + captura YOLO
			try {
				if (capturandoYOLO) await detenerCaptura();
				_pasoOk(1);
			} catch (err) {
				errorOverlay(err.message);
				return;
			}

			// Paso 2: capturar peso de la celda de carga + generar reporte SCA
			finDescripcion.textContent = 'Calculando resumen...';
			let pesoCapturado = 0;
			try {
				const ac = new AbortController();
				const pesoTimer = setTimeout(() => ac.abort(), 3000);
				const pesoRes  = await fetch('/arduino/peso', { signal: ac.signal });
				clearTimeout(pesoTimer);
				if (pesoRes.ok) {
					const pesoData = await pesoRes.json();
					pesoCapturado  = pesoData.peso ?? 0;
				}
			} catch { pesoCapturado = 0; }
			finDescripcion.textContent = `Calculando resumen... Peso capturado: ${Number(pesoCapturado).toFixed(2)} g`;

			await generarReporte();
			_pasoOk(2);

			monitoreoActivo = false;
			detenerStream();

			// Totales calculados por el backend en /video/lote/conteo — el frontend no
			// conoce nombres de clases ni decide qué cuenta como defecto. Solo se usan
			// para mostrar: el conteo que se guarda lo toma el servidor al finalizar.
			const _totalDefectoGranos = totalDefectosActual;
			const _totalGranos = reporteActual?.total_granos_analizados || 0;
			const stats = {
				totalGrains:      _totalGranos,
				totalDefectos:    _totalDefectoGranos,
				peso_capturado:   pesoCapturado,
				elapsedSeconds,
				incidencias:      [...incidencias],
			};
			sessionStorage.setItem('coffeeren.stats', JSON.stringify(stats));

			// Paso 3: guardar evaluacion
			try {
				const res = await fetch(`/evaluacion/${EVALUACION_ID}/finalizar`, {
					method: 'PATCH',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ incidencias }),
				});
				if (!res.ok) {
					throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo finalizar la evaluación.'));
				}
				const { codigo } = await res.json();
				_pasoOk(3);
				sessionStorage.removeItem('coffeeren.evaluacion');
				appendLog(`Evaluación finalizada. Código: ${codigo}`, 'ok');
				history.replaceState(null, '', '/registro');
				completarOverlay(codigo, pesoCapturado);
			} catch (err) {
				_pasoError(3);
				appendLog('Error: ' + err.message, 'error');
				sessionStorage.removeItem('coffeeren.stats');
				errorOverlay(err.message);
			}
		}

		// ── Guarda de navegación ──────────────────────────────────────────────

		// Al entrar por back/forward (bfcache), verificar si la evaluación ya fue
		// finalizada en el servidor y redirigir si es así.
		window.addEventListener('pageshow', async (e) => {
			if (!e.persisted) return; // solo interesa la restauración desde bfcache
			try {
				const res = await fetch(`/evaluacion/${EVALUACION_ID}/estado`);
				if (res.ok) {
					const { estado } = await res.json();
					if (estado === 'finalizada') {
						window.location.replace(`/analisis/${EVALUACION_ID}`);
					}
				}
			} catch { /* si falla, el backend redirigirá en el siguiente request */ }
		});

		window.addEventListener('beforeunload', (e) => {
			if (!monitoreoActivo && !finalizando) return;
			e.preventDefault();
			e.returnValue = '';
		});

		document.getElementById('btnVolver').addEventListener('click', async () => {
			const confirmed = await CoffeeModal.confirm({
				title: 'Salir del monitoreo',
				message: 'Si sales ahora, la clasificación en curso se cancelará y los datos de esta sesión no se guardarán. ¿Deseas salir de todas formas?',
			});
			if (!confirmed) return;
			monitoreoActivo = false;
			clearInterval(timerInterval);
			clearInterval(conteoInterval);
			await detenerFaja();
			if (capturandoYOLO) {
				try {
					await detenerCapturaDeEvaluacion();
				} catch (err) {
					CoffeeModal.error(err.message);
					return;
				}
				capturandoYOLO = false;
			}
			detenerStream();
			window.location.replace('/registro');
		});

		// ── Botones ───────────────────────────────────────────────────────────
		if (finishBtn) {
			finishBtn.addEventListener('click', async () => {
				const confirmed = await CoffeeModal.confirm({
					title: '¿Finalizar monitoreo?',
					message: '¿Deseas detener la faja y generar el reporte final?',
				});
				if (!confirmed) return;
				finishBtn.disabled    = true;
				finishBtn.textContent = 'Finalizando...';
				await finalizarMonitoreo(false);
			});
		}

		if (startBtn) {
			startBtn.addEventListener('click', iniciarCaptura);
		}

		actualizarUIdesdeConteo();
		appendLog('Iniciando sistema...');
	})();
