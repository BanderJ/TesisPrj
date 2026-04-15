ALTER TABLE EVALUACION DROP CONSTRAINT FKEVALUACION381094;
ALTER TABLE PERSONA DROP CONSTRAINT FKPERSONA750498;
ALTER TABLE EVALUACION DROP CONSTRAINT FKEVALUACION377725;
ALTER TABLE CAFICULTOR DROP CONSTRAINT FKCAFICULTOR530757;
ALTER TABLE CAFICULTOR DROP CONSTRAINT FKCAFICULTOR165779;
ALTER TABLE PERSONAL DROP CONSTRAINT FKPERSONAL360810;
ALTER TABLE DETALLE_EVALUACION DROP CONSTRAINT FKDETALLE_EV598148;
ALTER TABLE DETALLE_EVALUACION DROP CONSTRAINT FKDETALLE_EV178048;
ALTER TABLE EVALUACION DROP CONSTRAINT FKEVALUACION949977;
ALTER TABLE PERSONAL DROP CONSTRAINT FKPERSONAL26887;
DROP TABLE IF EXISTS CAFICULTOR CASCADE;
DROP TABLE IF EXISTS DETALLE_EVALUACION CASCADE;
DROP TABLE IF EXISTS EVALUACION CASCADE;
DROP TABLE IF EXISTS PERSONA CASCADE;
DROP TABLE IF EXISTS PERSONAL CASCADE;
DROP TABLE IF EXISTS TIPO_CAFICULTOR CASCADE;
DROP TABLE IF EXISTS TIPO_DEFECTO CASCADE;
DROP TABLE IF EXISTS TIPO_DOCUMENTO CASCADE;
DROP TABLE IF EXISTS TIPO_PERSONAL CASCADE;
DROP TABLE IF EXISTS VALOR_CAFE CASCADE;

CREATE TABLE CAFICULTOR (caficultor_id uuid DEFAULT uuidv7(), tipo_caficultor_id int2 NOT NULL, fecha_registro timestamp NOT NULL, PRIMARY KEY (caficultor_id));
CREATE TABLE DETALLE_EVALUACION (id uuid DEFAULT uuidv7(), cantidad int4 NOT NULL, evaluacion_id uuid NOT NULL, tipo_defecto_id int2 NOT NULL, PRIMARY KEY (id));
CREATE TABLE EVALUACION (id uuid DEFAULT uuidv7(), codigo char(10), personal_id uuid NOT NULL, caficultor_id uuid NOT NULL, valor_cafe_id uuid NOT NULL, fecha timestamp NOT NULL, peso_muestra numeric(10, 2) NOT NULL, peso_cascara numeric(10, 2) NOT NULL, peso_malo numeric(10, 2), peso_bueno numeric(10, 2), puntuacion numeric(10, 2), pago numeric(10, 2), grado_defecto char(1), num_malla int2 NOT NULL, PRIMARY KEY (id));
CREATE TABLE PERSONA (id uuid DEFAULT uuidv7(), nombre varchar(50) NOT NULL, ape_paterno varchar(30) NOT NULL, ape_materno varchar(30) NOT NULL, sexo char(1) NOT NULL, fecha_nacimiento date NOT NULL, tipo_documento_id int2 NOT NULL, num_documento varchar(12) NOT NULL, telefono char(9), estado char(1) NOT NULL, PRIMARY KEY (id));
CREATE TABLE PERSONAL (personal_id uuid DEFAULT uuidv7(), tipo_personal_id int2 NOT NULL, usuario varchar(30) NOT NULL UNIQUE, clave varchar(30) NOT NULL, estado char(1) NOT NULL, fecha_registro timestamp NOT NULL, PRIMARY KEY (personal_id));
CREATE TABLE TIPO_CAFICULTOR (id SERIAL NOT NULL, nombre varchar(50) NOT NULL, PRIMARY KEY (id));
CREATE TABLE TIPO_DEFECTO (id SERIAL NOT NULL, nombre varchar(50) NOT NULL, descripcion text, PRIMARY KEY (id));
CREATE TABLE TIPO_DOCUMENTO (id SERIAL NOT NULL, nombre varchar(50) NOT NULL, PRIMARY KEY (id));
CREATE TABLE TIPO_PERSONAL (id SERIAL NOT NULL, nombre varchar(50) NOT NULL, PRIMARY KEY (id));
CREATE TABLE VALOR_CAFE (id uuid DEFAULT uuidv7(), rango varchar(20) NOT NULL, precio float4 NOT NULL, fecha timestamp NOT NULL, PRIMARY KEY (id));
ALTER TABLE EVALUACION ADD CONSTRAINT FKEVALUACION381094 FOREIGN KEY (valor_cafe_id) REFERENCES VALOR_CAFE (id);
ALTER TABLE PERSONA ADD CONSTRAINT FKPERSONA750498 FOREIGN KEY (tipo_documento_id) REFERENCES TIPO_DOCUMENTO (id);
ALTER TABLE EVALUACION ADD CONSTRAINT FKEVALUACION377725 FOREIGN KEY (caficultor_id) REFERENCES CAFICULTOR (caficultor_id);
ALTER TABLE CAFICULTOR ADD CONSTRAINT FKCAFICULTOR530757 FOREIGN KEY (tipo_caficultor_id) REFERENCES TIPO_CAFICULTOR (id);
ALTER TABLE CAFICULTOR ADD CONSTRAINT FKCAFICULTOR165779 FOREIGN KEY (caficultor_id) REFERENCES PERSONA (id);
ALTER TABLE PERSONAL ADD CONSTRAINT FKPERSONAL360810 FOREIGN KEY (personal_id) REFERENCES PERSONA (id);
ALTER TABLE DETALLE_EVALUACION ADD CONSTRAINT FKDETALLE_EV598148 FOREIGN KEY (tipo_defecto_id) REFERENCES TIPO_DEFECTO (id);
ALTER TABLE DETALLE_EVALUACION ADD CONSTRAINT FKDETALLE_EV178048 FOREIGN KEY (evaluacion_id) REFERENCES EVALUACION (id);
ALTER TABLE EVALUACION ADD CONSTRAINT FKEVALUACION949977 FOREIGN KEY (personal_id) REFERENCES PERSONAL (personal_id);
ALTER TABLE PERSONAL ADD CONSTRAINT FKPERSONAL26887 FOREIGN KEY (tipo_personal_id) REFERENCES TIPO_PERSONAL (id);

--- INSERTS TABLAS MAESTRAS
INSERT INTO TIPO_CAFICULTOR (nombre) VALUES ('Socio'), ('Externo');
INSERT INTO TIPO_DOCUMENTO (nombre) VALUES ('DNI'), ('Pasaporte'), ('Carnet de Extranjería');
INSERT INTO TIPO_PERSONAL (nombre) VALUES ('Evaluador'), ('Gerente'), ('Administrador');
INSERT INTO TIPO_DEFECTO (nombre) VALUES ('Broca'), ('Cascarilla'), ('Cereza seca'), ('Concha'), ('Hongo'), ('Flotador'), ('Palos'), ('Piedra'), ('Raja'), ('Partido');

--- INSERTS DE PRUEBA PARA CREDENCIALES
INSERT INTO PERSONA (nombre, ape_paterno, ape_materno, sexo, fecha_nacimiento, tipo_documento_id, num_documento, telefono, estado) VALUES ('Anderson', 'Baca', 'Chuquimanco', 'M', '1990-08-20', 1, '70994265', '926607008', 'A');
INSERT INTO PERSONA (nombre, ape_paterno, ape_materno, sexo, fecha_nacimiento, tipo_documento_id, num_documento, telefono, estado) VALUES ('Juan', 'Perez', 'Gomez', 'M', '1980-05-15', 1, '12345678', '987654321', 'A');


--- INSRTS PRUEBA PARA CAFICULTORES
INSERT INTO PERSONA (nombre, ape_paterno, ape_materno, sexo, fecha_nacimiento, tipo_documento_id, num_documento, telefono, estado) VALUES ('Luis', 'Garcia', 'Ilimo', 'M', '1990-08-13', 1, '99988877', '987456456', 'A');
INSERT INTO PERSONA (nombre, ape_paterno, ape_materno, sexo, fecha_nacimiento, tipo_documento_id, num_documento, telefono, estado) VALUES ('Maria', 'Cueva', 'Guerrero', 'F', '1986-08-26', 1, '99988866', '987987987', 'A');

INSERT INTO PERSONAL (personal_id, tipo_personal_id, usuario, clave, estado, fecha_registro) VALUES ('019d6571-179d-7c1a-8c36-7a0de4bc5071',3, 'admin', '$argon2id$v=19$m=65536,t=3,p=4$z6D/NR7dxMYjqZzoFjnXvA$mIqszgfKRmtg+G6xRriSNJcNhq63EvCEEmOig4hUGmQ', 'A', NOW());
INSERT INTO PERSONAL (personal_id, tipo_personal_id, usuario, clave, estado, fecha_registro) VALUES ('019d6525-c02c-7adb-ac14-8f185e7e800c',1, 'evaluador1', '$argon2id$v=19$m=65536,t=3,p=4$z6D/NR7dxMYjqZzoFjnXvA$mIqszgfKRmtg+G6xRriSNJcNhq63EvCEEmOig4hUGmQ', 'A', NOW());

INSERT INTO CAFICULTOR (caficultor_id, tipo_caficultor_id, fecha_registro) VALUES ('019d6571-179d-7c1a-8c36-7a0de4bc5072', 1, NOW());
INSERT INTO CAFICULTOR (caficultor_id, tipo_caficultor_id, fecha_registro) VALUES ('019d6571-179d-7c1a-8c36-7a0de4bc5073', 2, NOW());

select * from persona;

select * from personal;