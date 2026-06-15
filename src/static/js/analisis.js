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

			document.getElementById('tdCodigo').textContent     = d.codigo                                             || '—';
			document.getElementById('tdFecha').textContent      = d.fecha                                              || '—';
			document.getElementById('tdSacos').textContent      = d.num_sacos    != null ? `${d.num_sacos} sacos`     : '—';
			document.getElementById('tdPeso').textContent       = d.peso_bruto   != null ? `${d.peso_bruto} kg`       : '—';
			document.getElementById('tdHumedad').textContent    = d.humedad      != null ? `${d.humedad}%`            : '—';
			document.getElementById('tdPesoMuestra').textContent = d.peso_muestra != null ? `${d.peso_muestra} kg`   : '—';
			document.getElementById('tdTrillado').textContent   = d.peso_trillado != null ? `${d.peso_trillado} kg`  : '—';
			document.getElementById('tdTamiz').textContent      = d.num_tamiz    != null ? `N° ${d.num_tamiz}`        : '—';
			document.getElementById('tdTamizado').textContent   = d.peso_tamizado != null ? `${d.peso_tamizado} kg`  : '—';
		} catch (e) {
			console.error(e);
			if (window.CoffeeModal) {
				CoffeeModal.error('No se pudo cargar el resumen de la evaluación.', 'Error de carga');
			}
		}
	}

	function cargarStats() {
		if (!stats) return;

		const { totalGrains = 0, defectNegro = 0, defectBrocado = 0, defectFermentado = 0, elapsedSeconds = 0 } = stats;
		const totalDefects = defectNegro + defectBrocado + defectFermentado;
		const maxDefect    = Math.max(defectNegro, defectBrocado, defectFermentado, 1);

		document.getElementById('statGranos').textContent   = totalGrains.toLocaleString('es-PE');
		document.getElementById('statDefectos').textContent = totalDefects.toLocaleString('es-PE');

		const mins = Math.floor(elapsedSeconds / 60);
		const secs = elapsedSeconds % 60;
		document.getElementById('statTiempo').textContent = mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;

		document.getElementById('dNegroVal').textContent    = defectNegro;
		document.getElementById('dBrocadoVal').textContent  = defectBrocado;
		document.getElementById('dFermentadoVal').textContent = defectFermentado;

		requestAnimationFrame(() => {
			document.getElementById('dNegroBar').style.width    = `${Math.min((defectNegro    / maxDefect) * 100, 100)}%`;
			document.getElementById('dBrocadoBar').style.width  = `${Math.min((defectBrocado  / maxDefect) * 100, 100)}%`;
			document.getElementById('dFermentadoBar').style.width = `${Math.min((defectFermentado / maxDefect) * 100, 100)}%`;
		});

		sessionStorage.removeItem('coffeeren.stats');
	}

	document.getElementById('btnExcel').addEventListener('click', () => {
		const rows = [
			['RESUMEN DE EVALUACIÓN DE CAFÉ - CoffeeRen', ''],
			[],
			['DATOS DE LA MUESTRA', ''],
			['Código evaluación',  document.getElementById('tdCodigo').textContent],
			['Caficultor',         document.getElementById('caficultorNombre').textContent],
			['Documento',          document.getElementById('metaDoc').textContent],
			['Tipo caficultor',    document.getElementById('metaTipoCaf').textContent],
			['Tipo de grano',      document.getElementById('metaGrano').textContent],
			['Registrado por',     document.getElementById('metaRegistradoPor').textContent],
			['Fecha',              document.getElementById('tdFecha').textContent],
			['N° sacos',           document.getElementById('tdSacos').textContent],
			['Peso bruto',         document.getElementById('tdPeso').textContent],
			['Humedad',            document.getElementById('tdHumedad').textContent],
			['Peso muestra',       document.getElementById('tdPesoMuestra').textContent],
			['Peso trillado',      document.getElementById('tdTrillado').textContent],
			['N° tamiz',           document.getElementById('tdTamiz').textContent],
			['Peso tamizado',      document.getElementById('tdTamizado').textContent],
			[],
			['ESTADÍSTICAS DE MONITOREO', ''],
			['Granos evaluados',   document.getElementById('statGranos').textContent],
			['Defectos totales',   document.getElementById('statDefectos').textContent],
			['Rendimiento IA',     document.getElementById('statRendimiento').textContent],
			['Tiempo de análisis', document.getElementById('statTiempo').textContent],
			[],
			['DEFECTOS POR TIPO', ''],
			['Defecto negro',      document.getElementById('dNegroVal').textContent],
			['Brocado',            document.getElementById('dBrocadoVal').textContent],
			['Fermentado',         document.getElementById('dFermentadoVal').textContent],
		];

		const ws = XLSX.utils.aoa_to_sheet(rows);
		ws['!cols'] = [{ wch: 26 }, { wch: 32 }];
		const wb = XLSX.utils.book_new();
		XLSX.utils.book_append_sheet(wb, ws, 'Resumen');
		const codigo = document.getElementById('tdCodigo').textContent.replace(/[^A-Za-z0-9]/g, '') || 'evaluacion';
		XLSX.writeFile(wb, `${codigo}_resumen.xlsx`);
	});

	cargarResumen();
	cargarStats();
})();
