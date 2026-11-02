/**
 * CoffeeReport — librería genérica de reportes (tabla + gráfico ECharts).
 *
 * Uso:
 *   CoffeeReport.render(contenedor, reporte)
 *
 * `reporte` es la respuesta de GET /reportes/{codigo}:
 *   { titulo, descripcion, columnas: [{campo, titulo}], filas: [{...}],
 *     grafico: { tipo: 'pie'|'bar', campo_etiqueta, campo_valor } | null }
 *
 * Cualquier reporte nuevo que respete esa forma se renderiza sin tocar este archivo.
 * Requiere /static/js/lib/echarts.min.js cargado antes.
 */
const CoffeeReport = (() => {
    // Paleta categórica validada (CVD + contraste) sobre las superficies del proyecto.
    // Orden fijo: los colores siguen a la categoría, nunca se reordenan.
    const PALETA = {
        light: ['#2a78d6', '#1baf7a', '#eda100', '#008300', '#4a3aa7', '#e34948', '#e87ba4', '#eb6834'],
        dark:  ['#3987e5', '#199e70', '#c98500', '#008300', '#9085e9', '#e66767', '#d55181', '#d95926'],
    };
    const TINTA = {
        light: { primaria: '#0b0b0b', secundaria: '#52514e', superficie: '#ffffff', grid: '#e1e0d9' },
        dark:  { primaria: '#ffffff', secundaria: '#c3c2b7', superficie: '#161922', grid: '#2c2c2a' },
    };

    const instancias = new Map(); // contenedor -> { chart, reporte }

    function _modo() {
        return document.body.classList.contains('dark') ? 'dark' : 'light';
    }

    function _formatearValor(valor, formato) {
        if (valor == null) return '—';
        if (formato) return Number(valor).toLocaleString('es-PE', {
            minimumFractionDigits: formato === 'numero' ? 0 : 2,
            maximumFractionDigits: formato === 'numero' ? 0 : 2,
        });
        return typeof valor === 'number' ? valor.toLocaleString('es-PE') : (valor ?? '—');
    }

    // === Tabla ===
    function _renderTabla(reporte, opciones) {
        const wrapper = document.createElement('div');
        wrapper.className = 'tabla-usuarios-wrapper';
        const tabla = document.createElement('table');
        tabla.className = 'tabla-usuarios';
        const cabecera = tabla.createTHead().insertRow();
        const columnas = [...reporte.columnas];
        if (reporte.detalle_evaluacion) columnas.push({ titulo: 'Detalle', campo: null });
        columnas.forEach(c => {
            const th = document.createElement('th');
            th.scope = 'col';
            th.textContent = c.titulo;
            cabecera.appendChild(th);
        });
        const tbody = tabla.createTBody();
        reporte.filas.forEach(fila => {
            const tr = tbody.insertRow();
            reporte.columnas.forEach(c => {
                tr.insertCell().textContent = _formatearValor(fila[c.campo], c.formato);
            });
            if (reporte.detalle_evaluacion) {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'btn btn-secondary';
                btn.textContent = 'Ver detalle';
                btn.setAttribute('aria-label', `Ver detalle de ${fila.codigo}`);
                btn.addEventListener('click', () => opciones.verDetalle?.(fila, btn));
                tr.insertCell().appendChild(btn);
            }
        });
        if (!reporte.filas.length) {
            const celda = tbody.insertRow().insertCell();
            celda.colSpan = columnas.length;
            celda.className = 'reporte-estado';
            celda.textContent = 'No hay registros para los filtros seleccionados.';
        }
        if (reporte.grafico?.campo_valor && reporte.filas.length) {
            const total = reporte.filas.reduce((suma, f) => suma + (Number(f[reporte.grafico.campo_valor]) || 0), 0);
            const tr = tabla.createTFoot().insertRow();
            reporte.columnas.forEach((c, i) => {
                tr.insertCell().textContent = i === 0 ? 'Total' : c.campo === reporte.grafico.campo_valor ? _formatearValor(total) : '';
            });
        }
        wrapper.appendChild(tabla);
        return wrapper;
    }

    // === Gráfico ===
    function _opcionesGrafico(reporte) {
        const modo = _modo();
        const colores = PALETA[modo];
        const tinta = TINTA[modo];
        const { tipo, campo_etiqueta, campo_valor } = reporte.grafico;
        const datos = reporte.filas.map(f => ({ name: f[campo_etiqueta], value: f[campo_valor] }));

        const base = {
            color: colores,
            textStyle: { fontFamily: 'inherit' },
            tooltip: {
                backgroundColor: tinta.superficie,
                borderColor: tinta.grid,
                textStyle: { color: tinta.primaria },
            },
            legend: {
                bottom: 0,
                icon: 'circle',
                itemWidth: 10,
                itemHeight: 10,
                textStyle: { color: tinta.secundaria, fontSize: 12 },
            },
        };

        if (tipo === 'pie') {
            return {
                ...base,
                tooltip: { ...base.tooltip, trigger: 'item', formatter: '{b}: {c} ({d}%)' },
                series: [{
                    type: 'pie',
                    radius: ['38%', '68%'],
                    center: ['50%', '44%'],
                    // separación de 2px entre segmentos (canal secundario para CVD)
                    itemStyle: { borderColor: tinta.superficie, borderWidth: 2, borderRadius: 4 },
                    // etiquetas directas en tinta de texto, nunca en el color del segmento
                    label: { color: tinta.primaria, fontSize: 12, formatter: '{b}\n{c}' },
                    labelLine: { lineStyle: { color: tinta.grid } },
                    emphasis: { scaleSize: 4 },
                    data: datos,
                }],
            };
        }

        // tipo === 'bar'
        return {
            ...base,
            legend: undefined, // una sola serie: el título la nombra
            tooltip: { ...base.tooltip, trigger: 'axis', axisPointer: { type: 'shadow' } },
            grid: { left: 8, right: 16, top: 16, bottom: 8, containLabel: true },
            xAxis: {
                type: 'category',
                data: datos.map(d => d.name),
                axisLine: { lineStyle: { color: tinta.grid } },
                axisTick: { show: false },
                axisLabel: { color: tinta.secundaria },
            },
            yAxis: {
                type: 'value',
                splitLine: { lineStyle: { color: tinta.grid } },
                axisLabel: { color: tinta.secundaria },
            },
            series: [{
                type: 'bar',
                barMaxWidth: 40,
                itemStyle: { color: colores[0], borderRadius: [4, 4, 0, 0] },
                data: datos.map(d => d.value),
            }],
        };
    }

    // === Render principal ===
    function render(contenedor, reporte, opciones = {}) {
        const previa = instancias.get(contenedor);
        if (previa) {
            previa.chart?.dispose();
            instancias.delete(contenedor);
        }
        contenedor.innerHTML = '';

        if (reporte.indicadores?.length) {
            const lista = document.createElement('dl');
            lista.className = 'reporte-indicadores';
            reporte.indicadores.forEach(indicador => {
                const item = document.createElement('div');
                const titulo = document.createElement('dt');
                titulo.textContent = indicador.titulo;
                const valor = document.createElement('dd');
                valor.textContent = `${_formatearValor(indicador.valor, indicador.unidad ? 'decimal' : 'numero')} ${indicador.unidad}`.trim();
                item.append(titulo, valor);
                lista.appendChild(item);
            });
            contenedor.appendChild(lista);
        }

        const grid = document.createElement('div');
        grid.className = 'reporte-grid' + (reporte.grafico ? '' : ' reporte-grid--solo-tabla');
        grid.appendChild(_renderTabla(reporte, opciones));

        let chart = null;
        if (reporte.grafico && typeof echarts !== 'undefined') {
            const divGrafico = document.createElement('div');
            divGrafico.className = 'reporte-grafico';
            grid.appendChild(divGrafico);
            contenedor.appendChild(grid);
            chart = echarts.init(divGrafico);
            chart.setOption(_opcionesGrafico(reporte));
        } else {
            contenedor.appendChild(grid);
        }

        instancias.set(contenedor, { chart, reporte });
    }

    // Cambio de tema: re-aplicar opciones con la paleta del modo activo
    new MutationObserver(() => {
        instancias.forEach(({ chart, reporte }) => {
            if (chart && reporte.grafico) chart.setOption(_opcionesGrafico(reporte), true);
        });
    }).observe(document.body, { attributes: true, attributeFilter: ['class'] });

    window.addEventListener('resize', () => {
        instancias.forEach(({ chart }) => chart?.resize());
    });

    return { render };
})();
