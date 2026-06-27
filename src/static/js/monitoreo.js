	(() => {
		const TIMEOUT_INACTIVIDAD_MS = 10_000; // 10 s sin nuevas detecciones a auto-finalizar

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
		const negroValueEl    = document.getElementById('defectNegroValue');
		const negroBarEl      = document.getElementById('defectNegroBar');
		const sanoValueEl     = document.getElementById('defectBrocadoValue');
		const sanoBarEl       = document.getElementById('defectBrocadoBar');
		const eventLog        = document.getElementById('eventLog');
		const finishBtn         = document.getElementById('finishBtn');
		const startBtn          = document.getElementById('startBtn');

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
		let _fpsCount = 0;
		let _fpsWindowStart = 0;

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

			let frameTimeout;
			let isFirstFrame = true;

			const refrescarFrame = async () => {
				try {
					const res = await fetch('/video/frame');
					if (res.status === 503) { frameTimeout = setTimeout(refrescarFrame, 33); return; }
					if (!res.ok) throw new Error('Error obteniendo frame');
					const url = URL.createObjectURL(await res.blob());
					cameraStreamEl.src = url;
					if (isFirstFrame) {
						isFirstFrame = false;
						clearTimeout(connectTimeout);
						cameraLoadingEl.style.display = 'none';
						cameraStreamEl.style.display  = 'block';
						if (fpsBadgeEl) { fpsBadgeEl.style.display = 'block'; _fpsWindowStart = performance.now(); _fpsCount = 0; }
					}
					_fpsCount++;
					const _now = performance.now();
					if (_now - _fpsWindowStart >= 1000) {
						const fps = Math.round(_fpsCount * 1000 / (_now - _fpsWindowStart));
						if (fpsBadgeEl) fpsBadgeEl.textContent = fps + ' FPS';
						_fpsCount = 0;
						_fpsWindowStart = _now;
					}
					frameTimeout = setTimeout(refrescarFrame, 33);
				} catch {
					if (isFirstFrame) { clearTimeout(connectTimeout); mostrarErrorCamara('No se pudo conectar con el stream de video'); }
				}
			};

			connectTimeout = setTimeout(() => {
				if (isFirstFrame) mostrarErrorCamara('Tiempo de espera agotado. Verifique la cámara.');
			}, 10000);

			refrescarFrame();
		}

		function detenerStream() {
			clearTimeout(connectTimeout);
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
				const { activo } = await res.json();
				if (activo) {
					// YOLO
					capturandoYOLO        = true;
					elapsedSeconds        = 0;
					tiempoUltimaDeteccion = Date.now();
					totalGranosUltimo     = 0;
					iniciarStream();
					timerInterval = setInterval(() => {
						elapsedSeconds += 1;
						if (timerEl) timerEl.textContent = formatTimer(elapsedSeconds);
					}, 1000);
					conteoInterval = setInterval(async () => {
						if (!capturandoYOLO || finalizando) return;
						try {
							const [rConteo, rStatus] = await Promise.all([
								fetch('/video/lote/conteo'),
								fetch('/video/status'),
							]);
							if (rStatus.ok) {
								const st = await rStatus.json();
								if (st.camara_desconectada) { _manejarDesconexionCamara(st.error); return; }
							}
							const data = await rConteo.json();
							conteoActual = data.conteo;
							gruposActual = data.conteo_agrupado ?? {};
							actualizarUIdesdeConteo(data.total_defectos, data.total_sanos, gruposActual);
						} catch (e) { console.error('Error obteniendo conteo:', e); }
					}, 1500);
					appendLog('Cámara conectada. Monitoreo en curso.');
				} else {
					await iniciarCaptura();
				}
			} catch {
				appendLog('No se pudo verificar el servidor. Reintentando arranque...');
				await iniciarCaptura();
			}
		})();

		// ── Estado compartido ─────────────────────────────────────────────────
		let monitoreoActivo       = true;
		let capturandoYOLO        = false;
		let finalizando           = false;
		let elapsedSeconds        = 0;
		let conteoActual          = {};
		let gruposActual          = {};
		let reporteActual         = null;
		let tiempoUltimaDeteccion = 0;
		let totalGranosUltimo     = 0;
		let timerInterval         = null;
		let conteoInterval        = null;

		// ── UI helpers ────────────────────────────────────────────────────────
		function appendLog(message) {
			if (eventLog) eventLog.innerHTML = `<p class="log-item">${elapsedSeconds}s - ${message}</p>`;
		}

		function formatTimer(v) {
			return `${String(Math.floor(v / 60)).padStart(2, '0')}:${String(v % 60).padStart(2, '0')}`;
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

		// ── Desconexión de cámara ─────────────────────────────────────────────
		function _manejarDesconexionCamara(errorMsg) {
			if (finalizando) return;
			capturandoYOLO = false;
			clearInterval(timerInterval);
			clearInterval(conteoInterval);
			detenerStream();

			const mensaje = errorMsg || 'Desconexión con cámara. La clasificación se ha detenido.';
			mostrarErrorCamara(mensaje);
			appendLog(mensaje);

			if (startBtn) { startBtn.style.display = 'inline-flex'; startBtn.textContent = 'Reintentar captura'; }
		}

		// ── Faja (Arduino) ────────────────────────────────────────────────────
		async function iniciarFaja() {
			try {
				const res  = await fetch('/arduino/motor/iniciar', { method: 'POST' });
				const data = await res.json();
				appendLog(data.mensaje || 'Faja iniciada.');
			} catch {
				appendLog('No se pudo iniciar la faja. Verifique la conexión Arduino.');
			}
		}

		async function detenerFaja() {
			try {
				await fetch('/arduino/motor/detener', { method: 'POST' });
			} catch {
				appendLog('No se pudo detener la faja. Verifique la conexión Arduino.');
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
				// 1. Iniciar YOLO + cámara primero
				appendLog('Cargando modelo y conectando cámara...');
				const res = await fetch('/video/iniciar', { method: 'POST' });
				if (!res.ok) {
					const err = await res.json().catch(() => ({ detail: 'Error desconocido' }));
					throw new Error(err.detail || 'Error al iniciar captura');
				}

				// 2. Esperar a que la cámara produzca el primer frame real
				appendLog('Esperando primer frame de la cámara...');
				const camaraLista = await esperarPrimerFrame(15000);
				if (!camaraLista) throw new Error('La cámara no respondió a tiempo. Verifique la conexión.');

				// 3. Cámara confirmada — arrancar faja
				appendLog('Cámara activa. Arrancando faja transportadora...');
				await iniciarFaja();

				capturandoYOLO        = true;
				elapsedSeconds        = 0;
				tiempoUltimaDeteccion = Date.now();
				totalGranosUltimo     = 0;

				appendLog('Faja en marcha. Captura YOLO activa.');
				iniciarStream();

				// Timer de sesión
				timerInterval = setInterval(() => {
					elapsedSeconds += 1;
					if (timerEl) timerEl.textContent = formatTimer(elapsedSeconds);
				}, 1000);

				// Conteo + detección de desconexión de cámara + auto-stop
				conteoInterval = setInterval(async () => {
					if (!capturandoYOLO || finalizando) return;
					try {
						const [rConteo, rStatus] = await Promise.all([
							fetch('/video/lote/conteo'),
							fetch('/video/status'),
						]);

						if (rStatus.ok) {
							const status = await rStatus.json();
							if (status.camara_desconectada) {
								_manejarDesconexionCamara(status.error);
								return;
							}
						}

						const data = await rConteo.json();
						conteoActual = data.conteo;
						gruposActual = data.conteo_agrupado ?? {};
						actualizarUIdesdeConteo(data.total_defectos, data.total_sanos, gruposActual);
					} catch (e) {
						console.error('Error obteniendo conteo:', e);
					}
				}, 1500);

			} catch (err) {
				appendLog('Error: ' + err.message);
				if (startBtn) { startBtn.style.display = 'inline-flex'; startBtn.textContent = 'Reintentar captura'; }
				await detenerFaja();
			}
		}

		async function detenerCaptura() {
			clearInterval(timerInterval);
			clearInterval(conteoInterval);
			capturandoYOLO = false;
			try { await fetch('/video/detener', { method: 'POST' }); } catch { /* ignorar */ }
			detenerStream();
			await detenerFaja();
		}

		async function generarReporte() {
			try {
				appendLog('Generando reporte ...');
				const res = await fetch('/video/lote/generar-reporte', { method: 'POST' });
				if (!res.ok) throw new Error('Error generando reporte');
				reporteActual = await res.json();
				const { grado, total_defectos, apto_specialty } = reporteActual;
				appendLog(`Reporte: Grado ${grado} | ${total_defectos} defectos | Specialty: ${apto_specialty ? 'Apto' : 'No apto'}`);
			} catch (err) {
				appendLog('Error al generar reporte: ' + err.message);
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
				: 'Por favor espera mientras se guardan los datos y se genera el reporte.';
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
			finDescripcion.textContent = 'El proceso finalizó correctamente. Revisa el resumen antes de continuar al análisis.';

			document.getElementById('resCode').textContent     = codigo || '—';
			document.getElementById('resGranos').textContent   = Object.values(conteoActual).reduce((a,b)=>a+b,0);
			document.getElementById('resGrado').textContent    = reporteActual?.grado ? `Grado ${reporteActual.grado}` : '—';
			document.getElementById('resSpecialty').textContent= reporteActual?.apto_specialty ? 'Apto ✓' : 'No apto';
			document.getElementById('resPeso').textContent     = `${Number(pesoGramos).toFixed(2)} g`;
			finResultado.style.display = 'block';

			btnIrAnalisis.disabled = false;
			btnIrAnalisis.style.cursor = 'pointer';
			btnIrAnalisis.style.background = 'var(--primary)';
			btnIrAnalisis.style.color = 'var(--primary-foreground, #fff)';
			btnIrAnalisis.textContent = 'Ir al análisis →';
		}

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
			_pasoOk(1);
			if (capturandoYOLO) await detenerCaptura();

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

			const _negro   = gruposActual.negro   ?? 0;
			const _brocado = gruposActual.brocado ?? 0;
			const _partido = gruposActual.partido ?? 0;
			const stats = {
				totalGrains:      reporteActual?.total_granos_analizados || 0,
				defectNegro:      _negro,
				defectBrocado:    _brocado,
				defectFermentado: _partido,
				totalDefectos:    reporteActual?.total_defectos || 0,
				grado:            reporteActual?.grado          || 'Sin clasificar',
				aptEspecialty:    reporteActual?.apto_specialty || false,
				peso_capturado:   pesoCapturado,
				elapsedSeconds,
			};
			sessionStorage.setItem('coffeeren.stats', JSON.stringify(stats));

			// Paso 3: guardar evaluacion
			try {
				const res = await fetch(`/evaluacion/${EVALUACION_ID}/finalizar`, {
					method: 'PATCH',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ reporte_yolo: reporteActual }),
				});
				if (!res.ok) {
					const err = await res.json();
					throw new Error(err.detail || 'Error al finalizar la evaluacion.');
				}
				const { codigo } = await res.json();
				_pasoOk(3);
				sessionStorage.removeItem('coffeeren.evaluacion');
				appendLog(`Evaluacion finalizada. Código: ${codigo}`);
				history.replaceState(null, '', '/registro');
				completarOverlay(codigo, pesoCapturado);
			} catch (err) {
				_pasoError(3);
				appendLog('Error: ' + err.message);
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
			if (capturandoYOLO) {
				capturandoYOLO = false;
				await fetch('/video/detener', { method: 'POST' }).catch(() => {});
			}
			detenerStream();
			await detenerFaja();
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
