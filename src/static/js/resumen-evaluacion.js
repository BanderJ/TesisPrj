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

	/** Totales del lote: indicadores y gráfico circular de distribución. */
	function conteo(defectos, buenos) {
		const disponible = defectos != null && buenos != null;
		const total = disponible ? defectos + buenos : 0;
		const pctDefectos = total > 0 ? (defectos / total) * 100 : 0;
		const pctBuenos = total > 0 ? 100 - pctDefectos : 0;
		const porcentaje = valor => `${numero(Number(valor.toFixed(1)))}%`;
		texto('grainTotal', disponible ? numero(total) : '—');
		texto('grainChartState', disponible ? (total > 0 ? 'Granos evaluados' : 'Sin granos') : 'Sin conteo');
		texto('dNegroVal', disponible ? numero(defectos) : '—');
		texto('dSanoVal', disponible ? numero(buenos) : '—');
		texto('dNegroPct', disponible ? porcentaje(pctDefectos) : '—');
		texto('dSanoPct', disponible ? porcentaje(pctBuenos) : '—');
		$('grainGoodArc').setAttribute('stroke-dasharray', total > 0 ? '100 0' : '0 100');
		$('grainDefectArc').setAttribute('stroke-dasharray', `${pctDefectos} ${100 - pctDefectos}`);
		$('grainChart').setAttribute('aria-label', !disponible
			? 'No hay un conteo disponible para esta evaluación.'
			: total === 0 ? 'Sin granos detectados en esta evaluación.'
				: `${numero(total)} granos evaluados: ${numero(defectos)} defectos (${porcentaje(pctDefectos)}) y ${numero(buenos)} buenos (${porcentaje(pctBuenos)}).`);
		// Sin totales (evaluación sin monitoreo): limpiar lo de una búsqueda anterior.
		if (!disponible) {
			['statGranos', 'statDefectos', 'statSanos', 'statPctDefecto'].forEach((id) => texto(id, '—'));
			return;
		}

		texto('statGranos',     numero(total));
		texto('statDefectos',   numero(defectos));
		texto('statSanos',      numero(buenos));
		texto('statPctDefecto', `${Math.round(pctDefectos)}%`);
	}

	/** Pinta el rendimiento calculado. Devuelve false si la evaluación aún no lo tiene. */
	function rendimiento(r) {
		const calculado = r.factor_rendimiento != null;
		// El peso neto se guarda al calcular el rendimiento: va en Datos de la
		// muestra, pero se pinta aquí para que aparezca también tras completar.
		texto('tdPesoNeto', conUnidad(r.peso_neto, ' kg'));
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
		// Mismo formato mm:ss que la columna Momento del registro del monitoreo.
		const min = (s) => `${CoffeeEventos.formatSegundo(s)} min`;
		tbody.innerHTML = seccion.hidden ? '' : arr.map((inc) =>
			`<tr><td>${min(inc.seg_apertura)}</td><td>${min(inc.seg_cierre)}</td><td>${min(inc.duracion_s)}</td></tr>`
		).join('');
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

	// Paleta de CoffeeRen en hex: Excel no entiende los oklch de input.css.
	const XL = { shell: '153921', primario: '197627', tinte: 'E3EFE5', texto: '0D1117', tenue: '736757', borde: 'DCDBD2' };
	const LINEA  = { style: 'thin', color: { rgb: XL.borde } };
	const BORDES = { top: LINEA, bottom: LINEA, left: LINEA, right: LINEA };
	const ESTILOS = {
		titulo:     { font: { bold: true, sz: 14, color: { rgb: 'FFFFFF' } }, fill: { fgColor: { rgb: XL.shell } }, alignment: { vertical: 'center', indent: 1 } },
		subtitulo:  { font: { sz: 10, color: { rgb: XL.tenue } }, alignment: { vertical: 'center', indent: 1 } },
		seccion:    { font: { bold: true, color: { rgb: XL.primario } }, fill: { fgColor: { rgb: XL.tinte } }, border: { bottom: { style: 'medium', color: { rgb: XL.primario } } }, alignment: { vertical: 'center', indent: 1 } },
		etiqueta:   { font: { color: { rgb: XL.tenue } }, border: BORDES, alignment: { vertical: 'center', indent: 1 } },
		valor:      { font: { bold: true, color: { rgb: XL.texto } }, border: BORDES, alignment: { vertical: 'center', wrapText: true } },
		encabezado: { font: { bold: true, color: { rgb: 'FFFFFF' } }, fill: { fgColor: { rgb: XL.primario } }, border: BORDES, alignment: { horizontal: 'center', vertical: 'center' } },
		celda:      { font: { color: { rgb: XL.texto } }, border: BORDES, alignment: { horizontal: 'center', vertical: 'center' } },
	};

	/** Celda a partir del texto en pantalla. Una cifra ("149.50 kg", "35%", "1,234") se guarda
	 *  como número y la unidad pasa al formato, para que Excel pueda operar con ella. */
	function celdaValor(texto, comoTexto) {
		const t = String(texto ?? '').trim() || '—';
		const m = comoTexto ? null : t.match(/^(-?\d[\d,]*(?:\.(\d+))?)\s*(%|kg|gr|g|sacos)?$/);
		if (!m) return { v: t, t: 's', s: ESTILOS.valor };
		const fmt = `#,##0${m[2] ? '.' + '0'.repeat(m[2].length) : ''}`;
		const n   = Number(m[1].replace(/,/g, ''));
		const [v, z] = m[3] === '%' ? [n / 100, `${fmt}%`] : [n, m[3] ? `${fmt}" ${m[3]}"` : fmt];
		return { v, t: 'n', z, s: { ...ESTILOS.valor, numFmt: z, alignment: { ...ESTILOS.valor.alignment, horizontal: 'right' } } };
	}

	function exportarExcel() {
		const g = (id) => $(id)?.textContent ?? '—';
		const filas = [];
		const agregar = (tipo, valores, extra = {}) => filas.push({ tipo, valores, ...extra });
		const seccion = (titulo) => { agregar('vacio', []); agregar('seccion', [titulo]); };
		const dato = (etiqueta, id, extra) => agregar('dato', [etiqueta, g(id)], extra);
		// Solo las cifras visibles: los datos de sesión no existen al entrar más tarde.
		const datoVisible = (etiqueta, id) => { if ($(id) && !$(id).closest('[hidden]')) dato(etiqueta, id); };

		agregar('titulo', ['CoffeeRen · Resumen de evaluación de muestra de café']);
		agregar('subtitulo', [[g('tdCodigo'), g('caficultorNombre'), g('tdFecha')].join('   ·   ')]);

		seccion('Datos de la muestra');
		dato('Código evaluación',        'tdCodigo', { texto: true });
		dato('Caficultor',               'caficultorNombre');
		dato('Documento',                'metaDoc', { texto: true });
		dato('Tipo caficultor',          'metaTipoCaf');
		dato('Tipo de grano',            'metaGrano');
		dato('Peso por quintal (grano)', 'metaPesoQqGrano');
		dato('Registrado por',           'metaRegistradoPor');
		dato('Fecha',                    'tdFecha', { texto: true });
		dato('N.º de sacos',             'tdSacos');
		dato('Peso bruto',               'tdPeso');
		dato('Peso neto',                'tdPesoNeto');
		dato('Humedad',                  'tdHumedad');
		dato('Peso muestra',             'tdPesoMuestra');
		dato('Peso trillado',            'tdTrillado');
		dato('N.º de tamiz',             'tdTamiz');
		dato('Peso tamizado',            'tdTamizado');

		seccion('Estadísticas de monitoreo');
		dato('Granos evaluados',         'statGranos');
		dato('Defectos totales',         'statDefectos');
		dato('Granos buenos',            'statSanos');
		dato('% Defecto',                'statPctDefecto');
		datoVisible('Tiempo de análisis', 'statTiempo');
		datoVisible('Peso capturado',     'pesoCaptEl');

		seccion('Rendimiento');
		dato('Factor rendimiento',       'rendFactor');
		dato('Peso bueno',               'rendPesoBueno');
		dato('Peso por quintal',         'rendPesoQq');
		agregar('dato', [g('rendPrecioLabel'), g('rendPrecio')]);
		dato('Pago (S/)',                'rendPago', { destacado: true });
		dato('Detalle del pago',         'rendPagoDetalle', { texto: true });

		const tbody = $('incidenciasTbody');
		if (tbody && tbody.rows.length > 0) {
			seccion('Incidencias de tapa');
			agregar('encabezado', ['Apertura', 'Cierre', 'Duración abierta']);
			for (const tr of tbody.rows) agregar('tabla', [...tr.cells].map((td) => td.textContent));
		}

		const ws = XLSX.utils.aoa_to_sheet([]);
		const merges  = [];
		const alturas = [];
		const poner  = (r, c, cel) => { ws[XLSX.utils.encode_cell({ r, c })] = cel; };
		const texto3 = (r, valores, estilo) => [0, 1, 2].forEach((c) => poner(r, c, { v: valores[c] ?? '', t: 's', s: estilo }));
		const ALTURA = { titulo: 30, subtitulo: 18, seccion: 20 };

		filas.forEach((f, r) => {
			switch (f.tipo) {
				case 'titulo':
				case 'subtitulo':
				case 'seccion':
					texto3(r, f.valores, ESTILOS[f.tipo]);
					merges.push({ s: { r, c: 0 }, e: { r, c: 2 } });
					alturas[r] = { hpt: ALTURA[f.tipo] };
					break;
				case 'encabezado':
				case 'tabla':
					texto3(r, f.valores, f.tipo === 'encabezado' ? ESTILOS.encabezado : ESTILOS.celda);
					break;
				case 'dato': {
					const [etiqueta, valor] = f.valores;
					const cel = celdaValor(valor, f.texto);
					let estiloEtiqueta = ESTILOS.etiqueta;
					if (f.destacado) {
						const fill = { fgColor: { rgb: XL.tinte } };
						cel.s = { ...cel.s, fill, font: { ...cel.s.font, sz: 12, color: { rgb: XL.primario } } };
						estiloEtiqueta = { ...ESTILOS.etiqueta, fill, font: { bold: true, color: { rgb: XL.texto } } };
					}
					poner(r, 0, { v: etiqueta, t: 's', s: estiloEtiqueta });
					poner(r, 1, cel);
					poner(r, 2, { v: '', t: 's', s: cel.s });
					merges.push({ s: { r, c: 1 }, e: { r, c: 2 } });
					// Textos largos (detalle del pago): una línea más por cada ~45 caracteres.
					alturas[r] = { hpt: 18 * Math.max(1, Math.ceil(String(valor).length / 45)) };
					break;
				}
				default:
					alturas[r] = { hpt: 8 };
			}
		});

		ws['!ref']    = XLSX.utils.encode_range({ s: { r: 0, c: 0 }, e: { r: filas.length - 1, c: 2 } });
		ws['!merges'] = merges;
		ws['!rows']   = alturas;
		ws['!cols']   = [{ wch: 32 }, { wch: 26 }, { wch: 22 }];

		const wb = XLSX.utils.book_new();
		XLSX.utils.book_append_sheet(wb, ws, 'Resumen');
		const codigo = g('tdCodigo').replace(/[^A-Za-z0-9]/g, '') || 'evaluacion';
		XLSX.writeFile(wb, `${codigo}_resumen.xlsx`);
	}

	window.CoffeeResumen = { pintar, conteo, rendimiento, incidencias, exportarExcel };
})();
