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

    function _formatearValor(valor) {
        return typeof valor === 'number' ? valor.toLocaleString('es-PE') : (valor ?? '—');
    }

    // === Tabla ===
    function _renderTabla(reporte) {
        const wrapper = document.createElement('div');
        wrapper.className = 'tabla-usuarios-wrapper';

        const ths = reporte.columnas.map(c => `<th>${c.titulo}</th>`).join('');
        const filas = reporte.filas.map(fila => {
            const tds = reporte.columnas.map(c => {
                const esNumero = typeof fila[c.campo] === 'number';
                return `<td${esNumero ? ' style="font-variant-numeric:tabular-nums;"' : ''}>${_formatearValor(fila[c.campo])}</td>`;
            }).join('');
            return `<tr>${tds}</tr>`;
        }).join('');

        // Fila de total cuando el gráfico declara un campo de valor numérico
        let tfoot = '';
        if (reporte.grafico?.campo_valor) {
            const total = reporte.filas.reduce((suma, f) => suma + (Number(f[reporte.grafico.campo_valor]) || 0), 0);
            const celdas = reporte.columnas.map((c, i) => {
                if (i === 0) return '<td style="font-weight:600;">Total</td>';
                if (c.campo === reporte.grafico.campo_valor) return `<td style="font-weight:600;font-variant-numeric:tabular-nums;">${total.toLocaleString('es-PE')}</td>`;
                return '<td></td>';
            }).join('');
            tfoot = `<tfoot><tr style="border-top:2px solid var(--border);">${celdas}</tr></tfoot>`;
        }

        wrapper.innerHTML = `
            <table class="tabla-usuarios">
                <thead><tr>${ths}</tr></thead>
                <tbody>${filas || '<tr><td colspan="' + reporte.columnas.length + '" style="text-align:center;padding:2rem;color:var(--muted-foreground);">Sin datos</td></tr>'}</tbody>
                ${tfoot}
            </table>`;
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
    function render(contenedor, reporte) {
        const previa = instancias.get(contenedor);
        if (previa) {
            previa.chart?.dispose();
            instancias.delete(contenedor);
        }
        contenedor.innerHTML = '';

        const grid = document.createElement('div');
        grid.className = 'reporte-grid' + (reporte.grafico ? '' : ' reporte-grid--solo-tabla');
        grid.appendChild(_renderTabla(reporte));

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
