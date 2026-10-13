-- Migración: se retira el grado SCA de las evaluaciones (2026-10-13).
-- El grado depende del tipo de defecto (primario/secundario) y el modelo actual
-- solo distingue defecto/verde, así que la categoría asignada no era válida.
-- La tabla CATEGORIA y la columna EVALUACION.categoria_id se conservan para cuando
-- el modelo clasifique por tipo de defecto; la aplicación ya no las escribe ni las lee.

UPDATE EVALUACION SET categoria_id = NULL WHERE categoria_id IS NOT NULL;
