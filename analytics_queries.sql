-- Catálogo de consultas SQLite para analytics_example.sql.

-- consulta: eudr
-- Superficie de predios con el indicador EUDR marcado en los datos de ejemplo.
SELECT
    pr.departamento,
    COUNT(DISTINCT p.id) AS total_productores,
    SUM(pa.hectareas) AS total_hectareas
FROM modulo_a_productor AS p
JOIN modulo_a_predio AS pr ON pr.productor_id = p.id
JOIN modulo_b_parcela AS pa ON pa.predio_id = pr.id_predio
WHERE pr.eudr_compliant = 1
GROUP BY pr.departamento
ORDER BY total_hectareas DESC, pr.departamento;

-- consulta: riesgo
-- Predios declarados orgánicos con insumos prohibidos en la última auditoría del año.
WITH auditorias AS (
    SELECT
        predio_id,
        estatus_general,
        uso_insumos_prohibidos,
        ROW_NUMBER() OVER (
            PARTITION BY predio_id ORDER BY fecha_auditoria DESC, id DESC
        ) AS posicion
    FROM modulo_b_plancampana
    WHERE anio_campana = :anio_campana
)
SELECT
    p.numero_documento,
    p.nombres || ' ' || p.apellidos AS productor,
    pr.nombre_predio,
    a.estatus_general
FROM modulo_a_productor AS p
JOIN modulo_a_predio AS pr ON pr.productor_id = p.id
JOIN auditorias AS a ON a.predio_id = pr.id_predio
WHERE a.posicion = 1
  AND a.estatus_general = '100_ORGANICO'
  AND a.uso_insumos_prohibidos = 1
ORDER BY pr.id_predio;

-- consulta: variedades
-- Usa el área asignada a cada variedad y solo las parcelas con altitud conocida.
SELECT
    v.nombre_variedad,
    ROUND(AVG(pa.altitud), 2) AS altitud_promedio_metros,
    SUM(v.hectareas_sembradas) AS total_hectareas_sembradas
FROM modulo_b_variedadparcela AS v
JOIN modulo_b_parcela AS pa ON pa.id_parcela = v.parcela_id
WHERE pa.altitud IS NOT NULL
GROUP BY v.nombre_variedad
HAVING SUM(v.hectareas_sembradas) > 5
ORDER BY altitud_promedio_metros DESC, v.nombre_variedad;
