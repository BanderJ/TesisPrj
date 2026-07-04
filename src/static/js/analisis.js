(() => {

	// Bloquear regreso a monitoreo: si el usuario presiona Atrás desde aquí,
	// redirigir siempre a /registro en vez de volver a /monitoreo/{id}.
	history.replaceState(null, '', window.location.href);
	window.addEventListener('popstate', () => {
		window.location.replace('/registro');
	});

	const storedStats = sessionStorage.getItem('coffeeren.stats');
	const stats = storedStats ? JSON.parse(storedStats) : null;

	function renderIncidencias(arr) {
		if (!arr || arr.length === 0) return;
		document.getElementById('incidenciasSection').style.display = '';
		const tbody = document.getElementById('incidenciasTbody');
		tbody.innerHTML = arr.map((inc, i) => {
			const dur = inc.duracion_s;
			const durStr = dur >= 60
				? `${Math.floor(dur / 60)}m ${dur % 60}s`
				: `${dur}s`;
			return `<tr>
				<td>${inc.seg_apertura}s</td>
				<td>${inc.seg_cierre}s</td>
				<td>${durStr}</td>
			</tr>`;
		}).join('');
	}

	async function cargarResumen() {
		try {
			const res = await fetch(`/evaluacion/${EVALUACION_ID}/resumen`);
			if (!res.ok) throw new Error('No se pudo cargar el resumen.');
			const d = await res.json();

			document.getElementById('codEval').textContent           = d.codigo || `EVA-${EVALUACION_ID.slice(0, 8)}`;
			document.getElementById('caficultorNombre').textContent  = d.caficultor_nombre || '—';
			document.getElementById('metaDoc').textContent           = d.num_documento    || '—';
			document.getElementById('metaTipoCaf').textContent       = d.tipo_caficultor  || '—';
			document.getElementById('metaGrano').textContent         = d.tipo_grano       || '—';
			document.getElementById('metaRegistradoPor').textContent = d.registrado_por   || '—';

			document.getElementById('tdCodigo').textContent      = d.codigo                                             || '—';
			document.getElementById('tdFecha').textContent       = d.fecha                                              || '—';
			document.getElementById('tdSacos').textContent       = d.num_sacos     != null ? `${d.num_sacos} sacos`    : '—';
			document.getElementById('tdPeso').textContent        = d.peso_bruto    != null ? `${d.peso_bruto} kg`      : '—';
			document.getElementById('tdHumedad').textContent     = d.humedad       != null ? `${d.humedad}%`           : '—';
			document.getElementById('tdPesoMuestra').textContent = d.peso_muestra  != null ? `${d.peso_muestra} kg`   : '—';
			document.getElementById('tdTrillado').textContent    = d.peso_trillado != null ? `${d.peso_trillado} kg`  : '—';
			document.getElementById('tdTamiz').textContent       = d.num_tamiz     != null ? `N° ${d.num_tamiz}`      : '—';
			document.getElementById('tdTamizado').textContent    = d.peso_tamizado != null ? `${d.peso_tamizado} kg`  : '—';

			renderRendimiento(d);

			// Si es acceso histórico (sin sessionStorage), renderizar incidencias desde la API
			if (!stats && d.incidencias) {
				renderIncidencias(d.incidencias);
			}
		} catch (e) {
			console.error(e);
			if (window.CoffeeModal) {
				CoffeeModal.error('No se pudo cargar el resumen de la evaluación.', 'Error de carga');
			}
		}
	}

	function cargarStats() {
		if (!stats) return;

		const {
			totalGrains    = 0,
			totalDefectos  = 0,
			grado          = null,
			aptEspecialty  = null,
			peso_capturado = null,
			elapsedSeconds = 0,
		} = stats;

		const totalSanos = Math.max(totalGrains - totalDefectos, 0);
		const pct        = totalGrains > 0 ? Math.round((totalDefectos / totalGrains) * 100) : 0;

		document.getElementById('statGranos').textContent     = totalGrains.toLocaleString('es-PE');
		document.getElementById('statDefectos').textContent   = totalDefectos.toLocaleString('es-PE');
		document.getElementById('statSanos').textContent      = totalSanos.toLocaleString('es-PE');
		document.getElementById('statPctDefecto').textContent = pct + '%';

		const mins = Math.floor(elapsedSeconds / 60);
		const secs = elapsedSeconds % 60;
		document.getElementById('statTiempo').textContent = mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;

		// Distribution bars
		document.getElementById('dNegroVal').textContent = totalDefectos.toLocaleString('es-PE');
		document.getElementById('dSanoVal').textContent  = totalSanos.toLocaleString('es-PE');

		requestAnimationFrame(() => {
			document.getElementById('dNegroBar').style.width = pct + '%';
			document.getElementById('dSanoBar').style.width  = (100 - pct) + '%';
		});

		// Classification panel
		if (grado != null) {
			document.getElementById('gradoSCA').textContent = grado;
		}

		if (aptEspecialty != null) {
			const el   = document.getElementById('specialtyVal');
			const card = document.getElementById('specialtyCard');
			el.textContent = aptEspecialty ? 'Apto' : 'No apto';
			card.classList.toggle('apto', !!aptEspecialty);
			card.classList.toggle('no-apto', !aptEspecialty);
		}

		if (peso_capturado != null) {
			document.getElementById('pesoCaptEl').textContent = `${peso_capturado} g`;
		}

		renderIncidencias(stats.incidencias);
		sessionStorage.removeItem('coffeeren.stats');
	}

	// ── Factor de rendimiento: mostrar valores o pedir peso bueno ─────────────
	let pesoTrilladoMax   = null;
	let totalDefectosEval = 0;

	function mostrarRendimientoCalculado(r) {
		document.getElementById('rendFactor').textContent    = Number(r.factor_rendimiento).toFixed(2);
		document.getElementById('rendPesoBueno').textContent = `${Math.round(Number(r.peso_bueno))} g`;
		document.getElementById('rendPesoQq').textContent    = r.peso_por_qq != null ? Number(r.peso_por_qq).toFixed(2) : '—';
		document.getElementById('rendPrecio').textContent    = r.precio != null ? Number(r.precio).toFixed(2) : '—';
		if (r.rango) document.getElementById('rendPrecioLabel').textContent = `Precio quintal (S/) — rango ${r.rango}`;
		document.getElementById('rendPago').textContent      = Number(r.pago).toFixed(2);
		document.getElementById('rendCategoria').textContent = r.categoria || '—';
		document.getElementById('rendimientoPendiente').style.display  = 'none';
		document.getElementById('rendimientoCalculado').style.display  = '';
	}

	function renderRendimiento(d) {
		if (d.factor_rendimiento != null) {
			mostrarRendimientoCalculado(d);
			return;
		}
		pesoTrilladoMax   = d.peso_trillado != null ? Number(d.peso_trillado) : null;
		totalDefectosEval = d.total_defectos ?? stats?.totalDefectos ?? 0;
		if (pesoTrilladoMax !== null) {
			document.getElementById('inputPesoBuenoAnalisis').max = Math.floor(pesoTrilladoMax);
			document.getElementById('pesoBuenoHintAnalisis').textContent =
				`Gramos enteros. Máximo: ${pesoTrilladoMax} g (peso trillado).`;
		}
		document.getElementById('rendimientoPendiente').style.display = '';
	}

	async function guardarPesoBuenoAnalisis() {
		const input   = document.getElementById('inputPesoBuenoAnalisis');
		const errorEl = document.getElementById('pesoBuenoErrorAnalisis');
		const btn     = document.getElementById('btnGuardarPesoBuenoAnalisis');
		errorEl.style.display = 'none';

		const validacion = CoffeeValidators.pesoBueno(input.value, pesoTrilladoMax);
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
				body: JSON.stringify({ total_defectos: totalDefectosEval, peso_bueno: peso }),
			});
			if (!res.ok) {
				const err = await res.json().catch(() => ({}));
				throw new Error(typeof err.detail === 'string' ? err.detail : 'No se pudo calcular el rendimiento.');
			}
			const data = await res.json();
			mostrarRendimientoCalculado({ ...data, peso_bueno: peso });
		} catch (err) {
			errorEl.textContent = err.message;
			errorEl.style.display = 'block';
		} finally {
			btn.disabled = false;
			btn.textContent = 'Calcular rendimiento';
		}
	}

	document.getElementById('btnGuardarPesoBuenoAnalisis').addEventListener('click', guardarPesoBuenoAnalisis);
	document.getElementById('inputPesoBuenoAnalisis').addEventListener('keydown', (e) => {
		if (e.key === 'Enter') { e.preventDefault(); guardarPesoBuenoAnalisis(); }
	});

	document.getElementById('btnExcel').addEventListener('click', () => {
		const g  = (id) => document.getElementById(id)?.textContent ?? '—';

		const rows = [
			['RESUMEN DE EVALUACIÓN DE CAFÉ - CoffeeRen', ''],
			[],
			['DATOS DE LA MUESTRA', ''],
			['Código evaluación',  g('tdCodigo')],
			['Caficultor',         g('caficultorNombre')],
			['Documento',          g('metaDoc')],
			['Tipo caficultor',    g('metaTipoCaf')],
			['Tipo de grano',      g('metaGrano')],
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
			['Granos evaluados',   g('statGranos')],
			['Defectos totales',   g('statDefectos')],
			['Granos buenos',      g('statSanos')],
			['% Defecto',          g('statPctDefecto')],
			['Tiempo de análisis', g('statTiempo')],
			[],
			['CLASIFICACIÓN SCA', ''],
			['Grado SCA',          g('gradoSCA')],
			['Specialty',          g('specialtyVal')],
			['Peso capturado',     g('pesoCaptEl')],
			[],
			['RENDIMIENTO', ''],
			['Factor rendimiento', g('rendFactor')],
			['Peso bueno',         g('rendPesoBueno')],
			['Peso por quintal',   g('rendPesoQq')],
			[g('rendPrecioLabel'), g('rendPrecio')],
			['Pago (S/)',          g('rendPago')],
			['Categoría',          g('rendCategoria')],
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
		ws['!cols'] = [{ wch: 26 }, { wch: 20 }, { wch: 20 }];
		const wb = XLSX.utils.book_new();
		XLSX.utils.book_append_sheet(wb, ws, 'Resumen');
		const codigo = g('tdCodigo').replace(/[^A-Za-z0-9]/g, '') || 'evaluacion';
		XLSX.writeFile(wb, `${codigo}_resumen.xlsx`);
	});

	cargarResumen();
	cargarStats();
})();
