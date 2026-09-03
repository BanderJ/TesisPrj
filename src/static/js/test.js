(() => {
	// Vista de prueba: enciende cámara + modelo (endpoints /video/*), muestra el
	// stream anotado y el conteo en vivo. No registra evaluaciones ni toca la faja.

	const btnIniciar = document.getElementById('btnIniciar');
	const btnResetear = document.getElementById('btnResetear');
	const btnDetener = document.getElementById('btnDetener');

	const cameraStream = document.getElementById('cameraStream');
	const cameraLoading = document.getElementById('cameraLoading');
	const cameraError = document.getElementById('cameraError');
	const cameraErrorMsg = document.getElementById('cameraErrorMsg');
	const cameraIdle = document.getElementById('cameraIdle');

	const totalGrainsEl = document.getElementById('totalGrains');
	const totalDefectsEl = document.getElementById('totalDefects');
	const totalSanosEl = document.getElementById('totalSanos');
	const pctDefectoEl = document.getElementById('pctDefecto');
	const statusEl = document.getElementById('testStatus');

	let activo = false;
	let conteoInterval = null;
	let streamTimeout = null;

	function setStatus(mensaje) {
		statusEl.textContent = mensaje;
	}

	function mostrarFeed(estado) {
		// estado: 'idle' | 'loading' | 'stream' | 'error'
		cameraIdle.style.display = estado === 'idle' ? 'flex' : 'none';
		cameraLoading.style.display = estado === 'loading' ? 'flex' : 'none';
		cameraStream.style.display = estado === 'stream' ? 'block' : 'none';
		cameraError.style.display = estado === 'error' ? 'flex' : 'none';
	}

	function mostrarErrorCamara(mensaje) {
		mostrarFeed('error');
		if (mensaje) cameraErrorMsg.textContent = mensaje;
	}

	function actualizarConteo(data) {
		const total = data.total_granos ?? 0;
		const defectos = data.total_defectos ?? 0;
		const sanos = data.total_sanos ?? 0;
		const pct = total > 0 ? Math.round((defectos / total) * 100) : 0;

		totalGrainsEl.textContent = total;
		totalDefectsEl.textContent = defectos;
		totalSanosEl.textContent = sanos;
		pctDefectoEl.textContent = pct + '%';
	}

	function resetearConteoUI() {
		actualizarConteo({});
	}

	async function refrescarConteo() {
		if (!activo) return;
		try {
			const [rConteo, rStatus] = await Promise.all([
				fetch('/video/lote/conteo'),
				fetch('/video/status'),
			]);
			if (rStatus.ok) {
				const st = await rStatus.json();
				if (st.camara_desconectada) {
					await detenerDeteccion(st.error || 'Se perdió la conexión con la cámara.');
					return;
				}
			}
			if (rConteo.ok) actualizarConteo(await rConteo.json());
		} catch (e) {
			console.error('Error obteniendo conteo:', e);
		}
	}

	function iniciarStream() {
		mostrarFeed('loading');
		cameraStream.onload = () => {
			clearTimeout(streamTimeout);
			if (activo) mostrarFeed('stream');
		};
		cameraStream.onerror = () => {
			clearTimeout(streamTimeout);
			if (activo) mostrarErrorCamara('No se pudo conectar con el stream de video.');
		};
		// cache-buster para forzar una conexión MJPEG nueva en cada arranque
		cameraStream.src = '/video/stream?t=' + Date.now();
		streamTimeout = setTimeout(() => {
			if (activo && cameraStream.style.display !== 'block') {
				mostrarErrorCamara('La cámara no envió imagen. Verifica la conexión y reinténtalo.');
			}
		}, 12000);
	}

	function detenerStream() {
		clearTimeout(streamTimeout);
		cameraStream.onload = null;
		cameraStream.onerror = null;
		cameraStream.src = '';
	}

	function estadoBotones(enMarcha) {
		btnIniciar.disabled = enMarcha;
		btnDetener.disabled = !enMarcha;
		btnResetear.disabled = !enMarcha;
	}

	async function iniciarDeteccion() {
		btnIniciar.disabled = true;
		btnIniciar.textContent = 'Iniciando...';
		setStatus('Cargando modelo y conectando cámara...');
		try {
			const res = await fetch('/video/iniciar', { method: 'POST' });
			if (!res.ok) {
				const err = await res.json().catch(() => ({}));
				throw new Error(err.detail || 'No se pudo iniciar la cámara.');
			}
			activo = true;
			iniciarStream();
			resetearConteoUI();
			conteoInterval = setInterval(refrescarConteo, 1500);
			estadoBotones(true);
			setStatus('Detección en curso. Coloca granos frente a la cámara.');
		} catch (err) {
			activo = false;
			mostrarErrorCamara(err.message);
			setStatus('Error: ' + err.message);
			estadoBotones(false);
		} finally {
			btnIniciar.textContent = 'Iniciar detección';
		}
	}

	async function detenerDeteccion(motivo) {
		activo = false;
		clearInterval(conteoInterval);
		conteoInterval = null;
		detenerStream();
		estadoBotones(false);
		btnDetener.textContent = 'Detener';

		try {
			await fetch('/video/detener', { method: 'POST' });
		} catch { /* el backend igual se detiene solo al perder actividad */ }

		if (motivo) {
			mostrarErrorCamara(motivo);
			setStatus('Detección detenida: ' + motivo);
		} else {
			mostrarFeed('idle');
			setStatus('Detección detenida.');
		}
	}

	async function resetearConteo() {
		btnResetear.disabled = true;
		try {
			const res = await fetch('/video/lote/resetear', { method: 'POST' });
			if (!res.ok) throw new Error('No se pudo reiniciar el conteo.');
			resetearConteoUI();
			setStatus('Conteo reiniciado.');
		} catch (err) {
			setStatus('Error: ' + err.message);
		} finally {
			if (activo) btnResetear.disabled = false;
		}
	}

	btnIniciar.addEventListener('click', iniciarDeteccion);
	btnDetener.addEventListener('click', async () => {
		btnDetener.disabled = true;
		btnDetener.textContent = 'Deteniendo...';
		await detenerDeteccion();
	});
	btnResetear.addEventListener('click', resetearConteo);

	// Si el usuario deja la vista, liberar cámara y modelo.
	window.addEventListener('beforeunload', () => {
		if (activo) navigator.sendBeacon?.('/video/detener');
	});

	// Estado inicial: si ya venía activo (p. ej. recarga), reengancharse.
	(async () => {
		try {
			const res = await fetch('/video/status');
			if (!res.ok) throw new Error();
			const { activo: yaActivo } = await res.json();
			if (yaActivo) {
				activo = true;
				iniciarStream();
				conteoInterval = setInterval(refrescarConteo, 1500);
				estadoBotones(true);
				setStatus('Detección ya estaba activa. Reconectado al stream.');
				refrescarConteo();
			} else {
				mostrarFeed('idle');
				setStatus('Cámara detenida.');
			}
		} catch {
			mostrarFeed('idle');
			setStatus('Cámara detenida.');
		}
	})();
})();
