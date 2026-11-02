-- Migración de la revisión técnica (2026-11-02):
--   1. Código EVA único y correlativo con secuencia.
--   2. VALOR_CAFE.precio de float4 a numeric(7, 2): el pago no se calcula sobre un float.
-- Para bases creadas antes de esta fecha; script.sql ya lo incluye para instalaciones nuevas.
--
-- Antes de ejecutarla, comprobar que no haya códigos repetidos (si la consulta devuelve
-- filas, la restricción UNIQUE falla y hay que corregir esas evaluaciones primero):
--   SELECT codigo, COUNT(*) FROM evaluacion WHERE codigo IS NOT NULL GROUP BY codigo HAVING COUNT(*) > 1;

BEGIN;

ALTER TABLE EVALUACION ADD CONSTRAINT uq_evaluacion_codigo UNIQUE (codigo);

CREATE SEQUENCE IF NOT EXISTS evaluacion_codigo_seq;

-- La secuencia continúa desde el mayor código ya emitido.
SELECT setval(
    'evaluacion_codigo_seq',
    COALESCE((SELECT MAX(CAST(SUBSTRING(codigo FROM 4) AS INTEGER))
              FROM evaluacion WHERE codigo ~ '^EVA[0-9]{7}$'), 0) + 1,
    false
);

ALTER TABLE VALOR_CAFE ALTER COLUMN precio TYPE numeric(7, 2) USING round(precio::numeric, 2);

COMMIT;
