/**
 * Resumen de una evaluación — render compartido.
 *
 * /analisis y /reporte incluyen la misma plantilla (partials/resumen_evaluacion.html)
 * y reciben la misma respuesta de /evaluacion/... (ResumenEvaluacionResponse).
 * Aquí se pinta una sola vez; cada página solo decide de dónde saca la evaluación.
 */
(() => {
	const $ = (id) => document.getElementById(id);
	const texto = (id, valor) => { const el = $(id); if (el) el.textContent = valor; };
	const conUnidad = (v, unidad) => (v != null ? `${v}${unidad}` : '—');
	const numero = (v) => Number(v).toLocaleString('es-PE');

	function datos(d) {
		texto('codEval',           d.codigo || '—');
		texto('caficultorNombre',  d.caficultor_nombre || '—');
		texto('metaDoc',           d.num_documento || '—');
		texto('metaTipoCaf',       d.tipo_caficultor || '—');
		texto('metaGrano',         d.tipo_grano || '—');
		texto('metaPesoQqGrano',   conUnidad(d.peso_qq_grano, ' kg'));
		texto('metaRegistradoPor', d.registrado_por || '—');

		texto('tdCodigo',      d.codigo || '—');
		texto('tdFecha',       d.fecha || '—');
		texto('tdSacos',       conUnidad(d.num_sacos, ' sacos'));
		texto('tdPeso',        conUnidad(d.peso_bruto, ' kg'));
		texto('tdHumedad',     conUnidad(d.humedad, '%'));
		texto('tdPesoMuestra', conUnidad(d.peso_muestra, ' gr'));
		texto('tdTrillado',    conUnidad(d.peso_trillado, ' gr'));
		texto('tdTamiz',       d.num_tamiz != null ? `N° ${d.num_tamiz}` : '—');
		texto('tdTamizado',    conUnidad(d.peso_tamizado, ' gr'));
	}

	/** Totales del lote: indicadores y barras de distribución. */
	function conteo(defectos, buenos) {
		// Sin totales (evaluación sin monitoreo): limpiar lo de una búsqueda anterior.
		if (defectos == null || buenos == null) {
			['statGranos', 'statDefectos', 'statSanos', 'statPctDefecto'].forEach((id) => texto(id, '—'));
			texto('dNegroVal', '0');
			texto('dSanoVal', '0');
			$('dNegroBar').style.width = '0%';
			$('dSanoBar').style.width  = '0%';
			return;
		}
		const total = defectos + buenos;
		const pct   = total > 0 ? Math.round((defectos / total) * 100) : 0;

		texto('statGranos',     numero(total));
		texto('statDefectos',   numero(defectos));
		texto('statSanos',      numero(buenos));
		texto('statPctDefecto', `${pct}%`);
		texto('dNegroVal',      numero(defectos));
		texto('dSanoVal',       numero(buenos));

		requestAnimationFrame(() => {
			$('dNegroBar').style.width = `${pct}%`;
			$('dSanoBar').style.width  = `${total > 0 ? 100 - pct : 0}%`;
		});
	}

	/** Pinta el rendimiento calculado. Devuelve false si la evaluación aún no lo tiene. */
	function rendimiento(r) {
		const calculado = r.factor_rendimiento != null;
		$('rendimientoPendiente').hidden = calculado;
		$('rendimientoCalculado').hidden = !calculado;
		if (!calculado) return false;

		texto('rendFactor',    Number(r.factor_rendimiento).toFixed(2));
		texto('rendPesoBueno', r.peso_bueno != null ? `${Math.round(Number(r.peso_bueno))} g` : '—');
		texto('rendPesoQq',    r.peso_por_qq != null ? Number(r.peso_por_qq).toFixed(2) : '—');
		texto('rendPrecio',    r.precio != null ? Number(r.precio).toFixed(2) : '—');
		texto('rendPrecioLabel', r.rango ? `Precio quintal (S/) — rango ${r.rango}` : 'Precio quintal (S/)');
		texto('rendPago',      r.pago != null ? Number(r.pago).toFixed(2) : '—');
		CoffeePago.pintar($('rendPagoDetalle'), r);
		return true;
	}

	function incidencias(arr) {
		const seccion = $('incidenciasSection');
		const tbody   = $('incidenciasTbody');
		seccion.hidden = !arr || arr.length === 0;
		tbody.innerHTML = seccion.hidden ? '' : arr.map((inc) => {
			const dur = inc.duracion_s;
			const durStr = dur >= 60 ? `${Math.floor(dur / 60)}m ${dur % 60}s` : `${dur}s`;
			return `<tr><td>${inc.seg_apertura}s</td><td>${inc.seg_cierre}s</td><td>${durStr}</td></tr>`;
		}).join('');
	}

	/** Pinta todo lo que trae la respuesta de /evaluacion/... */
	function pintar(d) {
		datos(d);
		conteo(d.total_defectos, d.total_buenos);
		const calculado = rendimiento(d);
		incidencias(d.incidencias);
		CoffeeEventos.render(d.eventos);
		return calculado;
	}

	function exportarExcel() {
		const g = (id) => $(id)?.textContent ?? '—';
		// Solo las cifras visibles: los datos de sesión no existen al entrar más tarde.
		const fila = (etiqueta, id) => ($(id) && !$(id).closest('[hidden]') ? [[etiqueta, g(id)]] : []);

		const rows = [
			['RESUMEN DE EVALUACIÓN DE CAFÉ - CoffeeRen', ''],
			[],
			['DATOS DE LA MUESTRA', ''],
			['Código evaluación',        g('tdCodigo')],
			['Caficultor',               g('caficultorNombre')],
			['Documento',                g('metaDoc')],
			['Tipo caficultor',          g('metaTipoCaf')],
			['Tipo de grano',            g('metaGrano')],
			['Peso por quintal (grano)', g('metaPesoQqGrano')],
			['Registrado por',           g('metaRegistradoPor')],
			['Fecha',                    g('tdFecha')],
			['N.º de sacos',                 g('tdSacos')],
			['Peso bruto',               g('tdPeso')],
			['Humedad',                  g('tdHumedad')],
			['Peso muestra',             g('tdPesoMuestra')],
			['Peso trillado',            g('tdTrillado')],
			['N.º de tamiz',                 g('tdTamiz')],
			['Peso tamizado',            g('tdTamizado')],
			[],
			['ESTADÍSTICAS DE MONITOREO', ''],
			['Granos evaluados',         g('statGranos')],
			['Defectos totales',         g('statDefectos')],
			['Granos buenos',            g('statSanos')],
			['% Defecto',                g('statPctDefecto')],
			...fila('Tiempo de análisis', 'statTiempo'),
			...fila('Peso capturado',    'pesoCaptEl'),
			[],
			['RENDIMIENTO', ''],
			['Factor rendimiento',       g('rendFactor')],
			['Peso bueno',               g('rendPesoBueno')],
			['Peso por quintal',         g('rendPesoQq')],
			[g('rendPrecioLabel'),       g('rendPrecio')],
			['Pago (S/)',                g('rendPago')],
			['Detalle del pago',         g('rendPagoDetalle')],
		];

		const tbody = $('incidenciasTbody');
		if (tbody && tbody.rows.length > 0) {
			rows.push([], ['INCIDENCIAS DE TAPA', '', ''], ['Apertura (s)', 'Cierre (s)', 'Duración abierta']);
			for (const tr of tbody.rows) {
				rows.push([tr.cells[0].textContent, tr.cells[1].textContent, tr.cells[2].textContent]);
			}
		}

		const ws = XLSX.utils.aoa_to_sheet(rows);
		ws['!cols'] = [{ wch: 34 }, { wch: 32 }, { wch: 20 }];
		const wb = XLSX.utils.book_new();
		XLSX.utils.book_append_sheet(wb, ws, 'Resumen');
		const codigo = g('tdCodigo').replace(/[^A-Za-z0-9]/g, '') || 'evaluacion';
		XLSX.writeFile(wb, `${codigo}_resumen.xlsx`);
	}

	window.CoffeeResumen = { pintar, conteo, rendimiento, incidencias, exportarExcel };
})();
