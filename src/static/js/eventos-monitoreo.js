/**
 * Traza del monitoreo — renderer compartido.
 *
 * El análisis (tras finalizar) y el reporte (búsqueda por código EVA) muestran
 * exactamente lo mismo: la diferencia entre ambas vistas es cómo se llega a la
 * evaluación, no qué se ve. Por eso el render vive aquí una sola vez y ambas
 * páginas lo invocan con los eventos que trae /evaluacion/... en el mismo campo.
 */
(() => {
	const ETIQUETAS_TIPO = {
		inicio:             'Inicio',
		fin:                'Fin',
		camara:             'Cámara',
		objeto_desconocido: 'Objeto extraño',
	};

	function _formatSegundo(s) {
		const seg = Number(s) || 0;
		return `${String(Math.floor(seg / 60)).padStart(2, '0')}:${String(seg % 60).padStart(2, '0')}`;
	}

	function _celda(texto, clase) {
		const td = document.createElement('td');
		td.textContent = texto;
		if (clase) td.className = clase;
		return td;
	}

	function _fila(ev) {
		const tr = document.createElement('tr');
		tr.appendChild(_celda(_formatSegundo(ev.segundo)));
		tr.appendChild(_celda(ETIQUETAS_TIPO[ev.tipo] || ev.tipo));
		tr.appendChild(_celda(ev.mensaje, `evento-msg evento-${ev.severidad}`));

		const tdEvidencia = document.createElement('td');
		if (ev.imagen_url) {
			const link = document.createElement('a');
			link.href      = ev.imagen_url;
			link.target    = '_blank';
			link.rel       = 'noopener';
			link.className = 'evento-thumb';
			const img = document.createElement('img');
			img.src     = ev.imagen_url;
			img.alt     = 'Evidencia del objeto detectado';
			img.loading = 'lazy';
			link.appendChild(img);
			tdEvidencia.appendChild(link);
		} else {
			tdEvidencia.textContent = '—';
		}
		tr.appendChild(tdEvidencia);
		return tr;
	}

	/**
	 * Pinta la traza. Sin eventos deja la sección oculta, igual que incidencias.
	 * @param {Array<{segundo:number,tipo:string,severidad:string,mensaje:string,imagen_url:?string}>} eventos
	 */
	function render(eventos) {
		const seccion = document.getElementById('eventosSection');
		const tbody   = document.getElementById('eventosTbody');
		if (!seccion || !tbody) return;

		if (!eventos || eventos.length === 0) {
			seccion.style.display = 'none';
			return;
		}

		tbody.replaceChildren(...eventos.map(_fila));
		seccion.style.display = '';

		const galeria = document.getElementById('eventosGaleria');
		if (!galeria) return;
		const conFoto = eventos.filter(ev => ev.imagen_url);
		galeria.replaceChildren(...conFoto.map(ev => {
			const fig = document.createElement('figure');
			fig.className = 'evidencia-item';
			const link = document.createElement('a');
			link.href   = ev.imagen_url;
			link.target = '_blank';
			link.rel    = 'noopener';
			const img = document.createElement('img');
			img.src     = ev.imagen_url;
			img.alt     = `Objeto extraño detectado en el segundo ${ev.segundo}`;
			img.loading = 'lazy';
			link.appendChild(img);
			const cap = document.createElement('figcaption');
			cap.textContent = _formatSegundo(ev.segundo);
			fig.append(link, cap);
			return fig;
		}));
		galeria.parentElement.style.display = conFoto.length ? '' : 'none';
	}

	window.CoffeeEventos = { render };
})();
