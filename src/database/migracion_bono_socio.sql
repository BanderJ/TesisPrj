-- Migración: beneficio de socio editable con historial (2026-10-12).
-- Para bases creadas antes de esta fecha; script.sql ya lo incluye para instalaciones nuevas.
-- Solo agrega estructura y el monto inicial: no modifica evaluaciones existentes
-- (su bono_socio queda en NULL = registrada antes de existir el beneficio).

CREATE TABLE IF NOT EXISTS BONO_SOCIO (
    id uuid DEFAULT uuidv7(),
    monto numeric(7, 2) NOT NULL,
    fecha timestamp NOT NULL DEFAULT NOW(),
    personal_id uuid NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT FKBONO_SOCIO_PERSONAL FOREIGN KEY (personal_id) REFERENCES PERSONAL (personal_id)
);

ALTER TABLE EVALUACION ADD COLUMN IF NOT EXISTS bono_socio numeric(7, 2);

INSERT INTO BONO_SOCIO (monto, personal_id)
SELECT 10.00, (SELECT personal_id FROM PERSONAL WHERE tipo_personal_id = 3 ORDER BY fecha_registro LIMIT 1)
WHERE NOT EXISTS (SELECT 1 FROM BONO_SOCIO);
