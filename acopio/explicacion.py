import json
import logging
from http.client import HTTPException
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.conf import settings


logger = logging.getLogger(__name__)


def explicar_acopio(resumen):
    modo = settings.AGROTRACE_EXPLICADOR
    if modo == "simulado":
        texto = (
            f"Se acopiaron {resumen['acopiado_total_kg']} kg sobre un cupo total "
            f"de {resumen['cupo_total_kg']} kg. Hubo desvíos en "
            f"{resumen['productores_con_desvio']} de {resumen['productores_con_cupo']} "
            f"productores con cupo. El exceso acumulado fue de {resumen['exceso_total_kg']} kg."
        )
        return {"modo": modo, "estado": "ok", "texto": texto}

    if modo != "gemini":
        logger.warning("Modo de explicación inválido.")
        return {"modo": None, "estado": "no_disponible", "texto": None}

    try:
        texto = consultar_gemini(resumen)
    except (OSError, HTTPException, ValueError, KeyError, IndexError, TypeError, AttributeError) as error:
        logger.warning("Explicación de Gemini no disponible (%s).", type(error).__name__)
        return {"modo": modo, "estado": "no_disponible", "texto": None}

    return {"modo": modo, "estado": "ok", "texto": texto}


def consultar_gemini(resumen):
    if not settings.GEMINI_API_KEY:
        raise ValueError("Falta la clave de Gemini.")

    instruccion = (
        "Explicá en español y en hasta tres frases el resumen de acopio del JSON. "
        "Conservá sus cifras y unidades. El exceso total suma los excesos individuales."
    )
    cuerpo = {
        "contents": [{"parts": [{"text": f"{instruccion}\n{json.dumps(resumen)}"}]}],
        "generationConfig": {"maxOutputTokens": 512, "thinkingConfig": {"thinkingLevel": "LOW"}},
    }
    modelo = quote(settings.GEMINI_MODEL, safe="")
    peticion = Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent",
        data=json.dumps(cuerpo).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    peticion.add_unredirected_header("x-goog-api-key", settings.GEMINI_API_KEY)
    with urlopen(peticion, timeout=5) as respuesta:
        contenido = json.load(respuesta)

    partes = contenido["candidates"][0]["content"]["parts"]
    texto = "\n".join(
        parte["text"] for parte in partes if "text" in parte and not parte.get("thought")
    ).strip()
    if not texto:
        raise ValueError("Gemini devolvió una explicación vacía.")
    return texto
