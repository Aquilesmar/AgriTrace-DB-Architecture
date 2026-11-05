-- Esquema y registros ficticios para el catálogo de consultas SQLite.
PRAGMA foreign_keys = ON;

CREATE TABLE modulo_a_productor (
    id INTEGER PRIMARY KEY,
    numero_documento TEXT NOT NULL UNIQUE,
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL
);

CREATE TABLE modulo_a_predio (
    id_predio INTEGER PRIMARY KEY,
    productor_id INTEGER NOT NULL REFERENCES modulo_a_productor (id),
    nombre_predio TEXT NOT NULL,
    departamento TEXT NOT NULL,
    eudr_compliant INTEGER NOT NULL CHECK (eudr_compliant IN (0, 1))
);

CREATE TABLE modulo_b_parcela (
    id_parcela INTEGER PRIMARY KEY,
    predio_id INTEGER NOT NULL REFERENCES modulo_a_predio (id_predio),
    hectareas REAL NOT NULL CHECK (hectareas > 0),
    altitud INTEGER
);

CREATE TABLE modulo_b_plancampana (
    id INTEGER PRIMARY KEY,
    predio_id INTEGER NOT NULL REFERENCES modulo_a_predio (id_predio),
    anio_campana INTEGER NOT NULL,
    fecha_auditoria TEXT NOT NULL,
    estatus_general TEXT NOT NULL,
    uso_insumos_prohibidos INTEGER NOT NULL CHECK (uso_insumos_prohibidos IN (0, 1))
);

CREATE TABLE modulo_b_variedadparcela (
    parcela_id INTEGER NOT NULL REFERENCES modulo_b_parcela (id_parcela),
    nombre_variedad TEXT NOT NULL,
    hectareas_sembradas REAL NOT NULL CHECK (hectareas_sembradas > 0),
    PRIMARY KEY (parcela_id, nombre_variedad)
);

INSERT INTO modulo_a_productor (id, numero_documento, nombres, apellidos) VALUES
    (1, 'DEMO-P01', 'Ana', 'Demo'),
    (2, 'DEMO-P02', 'Bruno', 'Demo'),
    (3, 'DEMO-P03', 'Carla', 'Demo');

INSERT INTO modulo_a_predio (id_predio, productor_id, nombre_predio, departamento, eudr_compliant) VALUES
    (1, 1, 'Predio Demo A', 'Norte', 1),
    (2, 1, 'Predio Demo B', 'Norte', 1),
    (3, 2, 'Predio Demo C', 'Sur', 1),
    (4, 3, 'Predio Demo D', 'Sur', 0);

INSERT INTO modulo_b_parcela (id_parcela, predio_id, hectareas, altitud) VALUES
    (1, 1, 8, 1500),
    (2, 1, 4, 1700),
    (3, 2, 3, 1900),
    (4, 3, 6, 1300),
    (5, 4, 10, NULL);

INSERT INTO modulo_b_plancampana (
    id, predio_id, anio_campana, fecha_auditoria, estatus_general, uso_insumos_prohibidos
) VALUES
    (1, 1, 2026, '2026-04-10', '100_ORGANICO', 1),
    (2, 1, 2026, '2026-06-15', '100_ORGANICO', 0),
    (3, 2, 2026, '2026-05-20', '100_ORGANICO', 1),
    (4, 3, 2025, '2025-06-15', '100_ORGANICO', 1),
    (5, 4, 2026, '2026-06-15', 'CONVENCIONAL', 1);

INSERT INTO modulo_b_variedadparcela (parcela_id, nombre_variedad, hectareas_sembradas) VALUES
    (1, 'Caturra', 6),
    (1, 'Bourbon', 2),
    (2, 'Caturra', 3),
    (2, 'Bourbon', 1),
    (3, 'Bourbon', 3),
    (4, 'Typica', 6),
    (5, 'Typica', 10);
