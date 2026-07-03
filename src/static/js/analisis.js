(() => {

	// Bloquear regreso a monitoreo: si el usuario presiona Atrás desde aquí,
	// redirigir siempre a /registro en vez de volver a /monitoreo/{id}.
	history.replaceState(null, '', window.location.href);
	window.addEventListener('popstate', () => {
		window.location.replace('/registro');
	});

	const storedStats = sessionStorage.getItem('coffeeren.stats');
	const stats = storedStats ? JSON.parse(storedStats) : null;

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

		sessionStorage.removeItem('coffeeren.stats');
	}

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
		];

		const ws = XLSX.utils.aoa_to_sheet(rows);
		ws['!cols'] = [{ wch: 26 }, { wch: 32 }];
		const wb = XLSX.utils.book_new();
		XLSX.utils.book_append_sheet(wb, ws, 'Resumen');
		const codigo = g('tdCodigo').replace(/[^A-Za-z0-9]/g, '') || 'evaluacion';
		XLSX.writeFile(wb, `${codigo}_resumen.xlsx`);
	});

	cargarResumen();
	cargarStats();
})();
