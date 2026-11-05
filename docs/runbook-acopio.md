# Runbook de acopio y explicación

Uso este recorrido para diagnosticar por separado los indicadores de acopio y la explicación. Para reproducirlo, prepará el entorno y los datos ficticios como indica el [README](../README.md#probar-en-local) y ejecutá los comandos desde la raíz del repositorio en PowerShell.

## Reproducir la falla de Gemini

```powershell
.\.venv\Scripts\python.exe manage.py test acopio.tests.AcopioTests.test_fallo_de_gemini_conserva_indicadores_y_saldo_negativo -v 2
```

La prueba simula un tiempo de espera agotado sin red ni credenciales. Debe terminar con `OK`. Comprueba HTTP 200, `explicacion.estado` igual a `no_disponible` y los mismos indicadores que la respuesta sin explicación. En particular, `P-003` conserva `saldo_kg` de `-125` y `desvio` en `true`.

## Diagnosticar una respuesta real de la demo

1. Pedí primero `/api/campanas/demo-2026/acopio/` sin `?explicar=1`. Si responde 404, revisá el código de campaña y cargá `acopio_demo` siguiendo el README. Si responde HTTP 200 con los indicadores esperados, revisá por separado la explicación.
2. Si la explicación indica `no_disponible`, revisá la terminal de Django. El aviso `Explicación de Gemini no disponible` muestra el tipo de error. Para `TimeoutError` o `URLError`, revisá la conectividad y el tiempo de respuesta. Para `HTTPError`, revisá la disponibilidad del modelo, los permisos y la cuota. Comprobá que el proceso de Django reciba `GEMINI_API_KEY` y, si elegiste otro modelo, `GEMINI_MODEL`. Mantené el valor de la clave fuera de los registros. Si el aviso es `Modo de explicación inválido`, revisá `AGRITRACE_EXPLICADOR`.

## Recuperar la explicación en modo simulado

Detené Django con `Ctrl+C` y arrancalo de nuevo en modo simulado.

```powershell
$env:AGRITRACE_EXPLICADOR = "simulado"
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

En otra terminal, pedí la explicación.

```powershell
curl.exe -i "http://127.0.0.1:8000/api/campanas/demo-2026/acopio/?explicar=1"
```

La verificación pasa si obtenés HTTP 200, `explicacion.modo` igual a `simulado`, `explicacion.estado` igual a `ok` y `P-003` conserva el saldo de `-125 kg` con desvío. Registrá el modo, el estado HTTP y el resultado en la [bitácora](bitacora.md).
