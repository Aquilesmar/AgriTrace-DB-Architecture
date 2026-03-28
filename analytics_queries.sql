=========================================================================
  AgriTrace: Consultas Analíticas y de Negocio (PostgreSQL / MySQL)
=========================================================================

   1. REPORTE DE CUMPLIMIENTO EUROPEO (EUDR) POR DEPARTAMENTO
   Calcula cuántas hectáreas totales están listas para exportar a Europa.
SELECT 
    pr.departamento,
    COUNT(DISTINCT p.id) AS total_productores,
    SUM(pa.hectareas) AS total_hectareas_certificadas
FROM modulo_a_productor p
JOIN modulo_a_predio pr ON p.id = pr.productor_id
JOIN modulo_b_parcela pa ON pr.id_predio = pa.predio_id
WHERE pr.eudr_compliant = TRUE
GROUP BY pr.departamento
ORDER BY total_hectareas_certificadas DESC;

  2. IDENTIFICACIÓN DE LOTES EN RIESGO DE DESCALIFICACIÓN
  Encuentra parcelas que están registradas como "100% Orgánicas" en la campaña actual, 
  pero donde se detectó el uso de insumos químicos prohibidos en la última auditoría.
WITH AuditoriaActual AS (
    SELECT 
        predio_id, 
        estatus_general, 
        uso_insumos_prohibidos 
    FROM modulo_b_plancampana 
    WHERE anio_campana = EXTRACT(YEAR FROM CURRENT_DATE)
)
SELECT 
    p.numero_documento,
    p.nombres || ' ' || p.apellidos AS productor,
    pr.nombre_predio,
    a.estatus_general
FROM modulo_a_productor p
JOIN modulo_a_predio pr ON p.id = pr.productor_id
JOIN AuditoriaActual a ON pr.id_predio = a.predio_id
WHERE a.estatus_general = '100_ORGANICO' 
  AND a.uso_insumos_prohibidos = TRUE;

   3. DISTRIBUCIÓN DE VARIEDADES DE CAFÉ POR ALTITUD
    Análisis útil para modelos predictivos de rendimiento y calidad en taza.
SELECT 
    v.nombre_variedad,
    ROUND(AVG(pa.altitud), 2) AS altitud_promedio_metros,
    SUM(pa.hectareas) AS total_hectareas_sembradas
FROM modulo_b_variedadparcela v
JOIN modulo_b_parcela pa ON v.parcela_id = pa.id_parcela
WHERE pa.altitud IS NOT NULL
GROUP BY v.nombre_variedad
HAVING SUM(pa.hectareas) > 5
ORDER BY altitud_promedio_metros DESC;
