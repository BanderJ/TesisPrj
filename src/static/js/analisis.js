(() => {

	// Bloquear regreso a monitoreo: si el usuario presiona Atrás desde aquí,
	// redirigir siempre a /registro en vez de volver a /monitoreo/{id}.
	history.replaceState(null, '', window.location.href);
	window.addEventListener('popstate', () => {
		window.location.replace('/registro');
	});

	// Datos de la sesión de monitoreo recién terminada (tiempo y peso de báscula). No existen si se entra más tarde: ahí todo sale de la BD.
	const storedStats = sessionStorage.getItem('coffeeren.stats');
	const stats = storedStats ? JSON.parse(storedStats) : null;

	let pesoTrilladoMax   = null;
	let totalDefectosEval = 0;

	async function cargarResumen() {
		try {
			const res = await fetch(`/evaluacion/${EVALUACION_ID}/resumen`);
			if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo cargar el resumen.'));
			const d = await res.json();

			if (!CoffeeResumen.pintar(d)) prepararPesoBueno(d);
			cargarStats();
		} catch (e) {
			console.error(e);
			CoffeeModal.error(e.message, 'Error de carga');
		}
	}

	function cargarStats() {
		if (!stats) return;

		const {
			totalGrains    = 0,
			totalDefectos  = 0,
			peso_capturado = null,
			elapsedSeconds = 0,
			incidencias    = null,
		} = stats;

		CoffeeResumen.conteo(totalDefectos, Math.max(totalGrains - totalDefectos, 0));
		document.querySelectorAll('[data-sesion]').forEach((el) => { el.hidden = false; });

		const mins = Math.floor(elapsedSeconds / 60);
		const secs = elapsedSeconds % 60;
		document.getElementById('statTiempo').textContent = mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;

		// Sin celda de carga no hay lectura: la fila de báscula queda oculta.
		if (peso_capturado > 0) {
			document.getElementById('pesoCaptEl').textContent = `${peso_capturado} g`;
			document.getElementById('pesoCaptRow').hidden = false;
		}
		if (incidencias && incidencias.length) {
			CoffeeResumen.incidencias(incidencias);
		}

		sessionStorage.removeItem('coffeeren.stats');
	}

	// ── Factor de rendimiento pendiente: pedir el peso de grano bueno ─────────
	function prepararPesoBueno(d) {
		pesoTrilladoMax   = d.peso_trillado != null ? Number(d.peso_trillado) : null;
		totalDefectosEval = d.total_defectos ?? stats?.totalDefectos ?? 0;
		if (pesoTrilladoMax !== null) {
			document.getElementById('inputPesoBuenoAnalisis').max = Math.floor(pesoTrilladoMax);
			document.getElementById('pesoBuenoHintAnalisis').textContent =
				`Gramos enteros. Máximo: ${pesoTrilladoMax} g (peso trillado).`;
		}
	}

	async function guardarPesoBuenoAnalisis() {
		const input   = document.getElementById('inputPesoBuenoAnalisis');
		const errorEl = document.getElementById('pesoBuenoErrorAnalisis');
		const btn     = document.getElementById('btnGuardarPesoBuenoAnalisis');
		errorEl.hidden = true;

		const validacion = CoffeeValidators.pesoBueno(input.value, pesoTrilladoMax);
		if (!validacion.valido) {
			errorEl.textContent = validacion.mensaje;
			errorEl.hidden = false;
			return;
		}
		const peso = validacion.peso;

		btn.disabled = true;
		btn.textContent = 'Calculando...';
		try {
			const res = await fetch(`/evaluacion/${EVALUACION_ID}/completar`, {
				method: 'PATCH',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ total_defectos: totalDefectosEval, peso_bueno: peso }),
			});
			if (!res.ok) {
				throw new Error(await CoffeeHttp.mensajeError(res, 'No se pudo calcular el rendimiento.'));
			}
			const data = await res.json();
			CoffeeResumen.rendimiento({ ...data, peso_bueno: peso });
		} catch (err) {
			errorEl.textContent = err.message;
			errorEl.hidden = false;
		} finally {
			btn.disabled = false;
			btn.textContent = 'Calcular rendimiento';
		}
	}

	document.getElementById('btnGuardarPesoBuenoAnalisis').addEventListener('click', guardarPesoBuenoAnalisis);
	document.getElementById('inputPesoBuenoAnalisis').addEventListener('keydown', (e) => {
		if (e.key === 'Enter') { e.preventDefault(); guardarPesoBuenoAnalisis(); }
	});
	document.getElementById('btnExcel').addEventListener('click', CoffeeResumen.exportarExcel);

	cargarResumen();
})();
