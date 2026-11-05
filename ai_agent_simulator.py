"""Ejecuta preguntas de ejemplo con SQL predefinido sobre datos ficticios."""

import argparse
import json
import sqlite3
from contextlib import closing
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PREGUNTAS = {
    "eudr": "¿Cuántos productores y hectáreas tienen el indicador EUDR marcado por departamento?",
    "riesgo": "¿Qué predios declarados orgánicos registran insumos prohibidos en su última auditoría de la campaña?",
    "variedades": "¿Qué altitud promedio tienen las variedades con más de cinco hectáreas y altitud conocida?",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("consulta", nargs="?", choices=PREGUNTAS, default="eudr")
    parser.add_argument("--campana", type=int, default=2026, help="Año para la consulta de riesgo")
    args = parser.parse_args()

    catalogo = (RAIZ / "analytics_queries.sql").read_text(encoding="utf-8")
    consultas = {}
    for bloque in catalogo.split("-- consulta: ")[1:]:
        nombre, sentencia = bloque.split("\n", maxsplit=1)
        consultas[nombre] = sentencia.strip()

    sql = consultas[args.consulta]
    with closing(sqlite3.connect(":memory:")) as conexion:
        conexion.row_factory = sqlite3.Row
        conexion.executescript((RAIZ / "analytics_example.sql").read_text(encoding="utf-8"))
        filas = conexion.execute(sql, {"anio_campana": args.campana}).fetchall()

    print(PREGUNTAS[args.consulta])
    print(f"\n{sql}\n")
    print(json.dumps([dict(fila) for fila in filas], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
