from django.db.models import Sum

from .models import Cupo


def calcular_acopio(campana):
    cupos = (
        Cupo.objects.filter(campana=campana)
        .annotate(acopiado_kg=Sum("entregas__peso_kg", default=0))
        .order_by("productor__codigo")
        .values("productor__codigo", "limite_kg", "acopiado_kg")
    )
    productores = []
    for cupo in cupos:
        saldo_kg = cupo["limite_kg"] - cupo["acopiado_kg"]
        productores.append(
            {
                "productor": cupo["productor__codigo"],
                "cupo_kg": cupo["limite_kg"],
                "acopiado_kg": cupo["acopiado_kg"],
                "saldo_kg": saldo_kg,
                "desvio": saldo_kg < 0,
            }
        )

    return {
        "campana": campana.codigo,
        "resumen": {
            "productores_con_cupo": len(productores),
            "cupo_total_kg": sum(fila["cupo_kg"] for fila in productores),
            "acopiado_total_kg": sum(fila["acopiado_kg"] for fila in productores),
            "productores_con_desvio": sum(fila["desvio"] for fila in productores),
            "exceso_total_kg": sum(-fila["saldo_kg"] for fila in productores if fila["desvio"]),
        },
        "productores": productores,
    }
