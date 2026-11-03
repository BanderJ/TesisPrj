/**
 * CoffeeHttp — utilidades HTTP compartidas del frontend.
 *
 * Regla del proyecto: el texto de un error de negocio lo decide el backend
 * (campo `detail` de la respuesta JSON). El frontend NO reescribe ese texto;
 * solo aporta un mensaje de respaldo cuando el backend no manda nada legible.
 *
 * Uso:
 *   const res = await fetch('/ruta', { ... });
 *   if (!res.ok) throw new Error(await CoffeeHttp.mensajeError(res, 'texto de respaldo'));
 */
window.CoffeeHttp = (() => {
    'use strict';

    /**
     * Extrae el mensaje de una respuesta de error.
     * Soporta `detail` como string, como lista (422 de Pydantic sin aplanar),
     * como objeto `{msg}`, y cuerpos sin JSON (p. ej. una página de error HTML).
     * @param {Response} res
     * @param {string} [fallback]
     * @returns {Promise<string>}
     */
    async function mensajeError(res, fallback) {
        let cuerpo = null;
        try {
            cuerpo = await res.clone().json();
        } catch (_) {
            /* respuesta vacía o no-JSON */
        }
        const detalle = cuerpo && cuerpo.detail;

        if (typeof detalle === 'string' && detalle.trim()) {
            return detalle;
        }
        if (Array.isArray(detalle) && detalle.length) {
            return detalle
                .map((e) => (e && e.msg ? String(e.msg) : String(e)))
                .join('. ')
                .replace(/Value error, /g, '');
        }
        if (detalle && typeof detalle === 'object' && detalle.msg) {
            return String(detalle.msg);
        }
        return fallback || `Error ${res.status}`;
    }

    return { mensajeError };
})();
