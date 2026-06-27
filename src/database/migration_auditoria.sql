-- Migración: Tabla AUDITORIA
-- Ejecutar en la base de datos existente (no recrea las demás tablas)

CREATE TABLE IF NOT EXISTS AUDITORIA (
    id              uuid            DEFAULT uuidv7() NOT NULL,
    personal_id     uuid,
    usuario         varchar(30),
    tipo_personal_id int2,
    rol             varchar(50),
    accion          varchar(60)     NOT NULL,
    tabla_afectada  varchar(50),
    registro_id     varchar(100),
    descripcion     text,
    datos_anteriores jsonb,
    datos_nuevos    jsonb,
    ip_cliente      varchar(45),
    fecha_hora      timestamp       NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS idx_auditoria_fecha_hora     ON AUDITORIA (fecha_hora DESC);
CREATE INDEX IF NOT EXISTS idx_auditoria_personal_id    ON AUDITORIA (personal_id);
CREATE INDEX IF NOT EXISTS idx_auditoria_accion         ON AUDITORIA (accion);
CREATE INDEX IF NOT EXISTS idx_auditoria_tipo_personal  ON AUDITORIA (tipo_personal_id);
