# Bitácora de trabajo con IA

## Aporte y alcance

- **Aquiles Claudio** definió el problema a partir de su experiencia con AgroTrace, el requisito de conservar los saldos negativos y los casos que había que probar. También delimitó el uso de datos ficticios y el papel explicativo de Gemini.
- **Codex** generó el código de la demo, la migración, los datos de ejemplo, la integración con Gemini, las pruebas y esta documentación. También ajustó el SQL y el simulador públicos en una copia local separada.

## Comprobaciones ejecutadas por Codex

- Aplicó la migración, cargó los 12 registros ficticios y ejecutó nueve pruebas con Python 3.14 y Django 5.2.19. Comprobó por HTTP el JSON del README, la explicación simulada y el 404.
- Con una respuesta de Gemini simulada, verificó que la petición incluye los indicadores agregados. Simuló un tiempo de espera agotado y comparó todos los indicadores con la respuesta sin explicación. La llamada al servicio real queda pendiente.
- Ejecutó las tres consultas con el simulador y verificó sus resultados. Para `riesgo` probó 2026, 2025 y un año sin registros.

## Caso para explicar en entrevista

`P-003` tiene dos entregas de 300 y 325 kg y un cupo de 500 kg. El saldo es `500 - 625 = -125 kg`. La prueba comprueba tanto el signo del saldo como el valor `true` del desvío. Codex probó deliberadamente un recorte a cero en memoria. La prueba falló con `0 != -125` y volvió a pasar al ejecutar la implementación original.

## Fallo del ejemplo publicado

Al ejecutar el SQL original en SQLite apareció `near "==": syntax error` por el encabezado sin comentar. Codex convirtió los encabezados en comentarios, adaptó las consultas al esquema ficticio y cambió el simulador para ejecutar ese mismo archivo en memoria. Verificó el resultado al correr los tres ejemplos del README.

## Revisión personal de Aquiles

| Comprobación | Resultado |
| --- | --- |
| Sumar 300 + 325 kg y contrastar `500 − 625 = −125` con la respuesta HTTP de `P-003`. | Pendiente |
| Ejecutar la prueba del exceso y la suite completa con los comandos del README. | Pendiente |
| Revisar el alcance y los archivos del cambio local antes de publicar. | Pendiente |

Al completar una comprobación, anotar la fecha, el comando o la petición y el resultado observado. Si aparece un fallo, registrar qué se esperaba, qué devolvió el sistema, qué se cambió y qué prueba confirmó la corrección.
