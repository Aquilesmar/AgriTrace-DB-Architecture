# Revisión técnica de AgroTrace

## Qué quise resolver

Tomé una pregunta del trabajo con AgroTrace y la llevé a una demo con datos ficticios. Quería que una persona de acopio pudiera distinguir a quien llegó justo a su cupo de quien se pasó y, en ese caso, saber por cuántos kilos. Por eso definí el saldo como cupo menos acopio y dejé que el signo se conserve en la respuesta.

Usé Codex para preparar la implementación, los datos de prueba y los casos de regresión. Le marqué los casos que tenía que cubrir y el límite de la integración con Gemini. El cálculo queda en Django y Gemini recibe el resumen para explicarlo.

## Revisión manual del caso P-003

Mi primera comprobación es seguir las entregas de un productor desde la [carga ficticia](../acopio/fixtures/acopio_demo.json) hasta la respuesta de la API. Para `P-003` hay dos entregas, de 300 y 325 kg, y un cupo de 500 kg. La cuenta es `500 - (300 + 325) = -125 kg`.

Con el servidor levantado según el [README](../README.md#probar-en-local), esta consulta permite revisar ese registro en PowerShell.

```powershell
$acopio = Invoke-RestMethod 'http://127.0.0.1:8000/api/campanas/demo-2026/acopio/'
$acopio.productores | Where-Object { $_.productor -eq 'P-003' }
```

Espero ver `acopiado_kg = 625`, `saldo_kg = -125` y `desvio = true`. En `P-002`, el saldo es exactamente cero y el desvío queda en `false`. El resumen de la campaña conserva los 125 kg de exceso aunque otro productor todavía tenga cupo disponible.

## Qué detecta la regresión

Como experimento se recortó temporalmente el saldo a cero en memoria. La prueba falló con `0 != -125` y volvió a pasar al quitar el recorte. Ese es el cambio que más me interesa detectar en una revisión de código. Si la respuesta pierde el signo, el equipo de acopio pierde la cifra exacta con la que puede priorizar el seguimiento.

También quise que la consulta siguiera siendo útil durante una caída de Gemini. La prueba simula un tiempo de espera agotado y comprueba HTTP 200, los mismos indicadores y `explicacion.estado = no_disponible`. El [runbook](runbook-acopio.md) describe cómo diagnosticar el fallo y verificar la recuperación. Las nueve pruebas pasaron en Python 3.10 y 3.14. [Ejecución en GitHub Actions](https://github.com/Aquilesmar/AgroTrace-DB-Architecture/actions/runs/42119247448)

## Qué cambió en el SQL

La primera ejecución del catálogo publicado en SQLite devolvió `near "==": syntax error` porque el encabezado estaba escrito como texto suelto. El ajuste lo convirtió en un comentario y dejó el simulador leyendo las consultas del mismo archivo. La verificación en consola confirmó los resultados de los tres ejemplos del README.
