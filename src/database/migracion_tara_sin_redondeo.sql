-- Migración: tara del lote sin redondeo (2026-11-02).
-- Para bases creadas antes de esta fecha; script.sql ya lo incluye para instalaciones nuevas.
-- La tara es num_sacos × 0.25 kg y se resta tal cual del peso bruto (2 sacos = 0.50 kg), así que
-- EVALUACION.tara_total deja de ser entero. Las evaluaciones ya completadas conservan su valor.

ALTER TABLE EVALUACION ALTER COLUMN tara_total TYPE numeric(7, 2);
