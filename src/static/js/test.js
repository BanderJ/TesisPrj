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
				validarLoteDePrueba(st);
				if (st.camara_desconectada) {
					await detenerDeteccion(st.error || 'Se perdió la conexión con la cámara.');
					return;
				}
			}
			if (rConteo.ok) actualizarConteo(await rConteo.json());
		} catch (e) {
			liberarVista();
			mostrarErrorCamara(e.message);
			setStatus(e.message);
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
			if (activo) mostrarErrorCamara('No se pudo conectar con el video.');
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

	function validarLoteDePrueba(estado) {
		if (estado.evaluacion_id) {
			throw new Error('Hay un lote asociado a una evaluación. Prueba no puede detener ni reiniciar ese monitoreo.');
		}
	}

	function liberarVista() {
		activo = false;
		clearInterval(conteoInterval);
		conteoInterval = null;
		detenerStream();
		estadoBotones(false);
	}

	async function iniciarDeteccion() {
		btnIniciar.disabled = true;
		btnIniciar.textContent = 'Iniciando...';
		setStatus('Cargando modelo y conectando cámara...');
		try {
			const res = await fetch('/video/iniciar', { method: 'POST' });
			if (!res.ok) {
				throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo iniciar la cámara.'));
			}
			const rStatus = await fetch('/video/status');
			if (!rStatus.ok) throw new Error(await CoffeeHttp.mensajeError(rStatus, 'No se pudo consultar el monitoreo.'));
			validarLoteDePrueba(await rStatus.json());
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
		try {
			const res = await fetch('/video/detener', { method: 'POST' });
			if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo detener la detección.'));
			liberarVista();
			if (motivo) {
				mostrarErrorCamara(motivo);
				setStatus('Detección detenida: ' + motivo);
			} else {
				mostrarFeed('idle');
				setStatus('Detección detenida.');
			}
		} catch (err) {
			liberarVista();
			mostrarErrorCamara(err.message);
			setStatus(err.message);
		} finally {
			btnDetener.textContent = 'Detener';
		}
	}

	async function resetearConteo() {
		btnResetear.disabled = true;
		try {
			const res = await fetch('/video/lote/resetear', { method: 'POST' });
			if (!res.ok) {
				if (res.status === 409 || res.status === 403) liberarVista();
				throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo reiniciar el conteo.'));
			}
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
			const estado = await res.json();
			const { activo: yaActivo } = estado;
			if (yaActivo) {
				validarLoteDePrueba(estado);
				activo = true;
				iniciarStream();
				conteoInterval = setInterval(refrescarConteo, 1500);
				estadoBotones(true);
				setStatus('La detección ya estaba activa. Se restableció la transmisión de video.');
				refrescarConteo();
			} else {
				mostrarFeed('idle');
				setStatus('Cámara detenida.');
			}
		} catch (err) {
			liberarVista();
			mostrarErrorCamara(err.message || 'No se pudo consultar el monitoreo.');
			setStatus(err.message || 'No se pudo consultar el monitoreo.');
		}
	})();
})();
