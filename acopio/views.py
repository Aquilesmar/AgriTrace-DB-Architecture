from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .explicacion import explicar_acopio
from .models import Campana
from .services import calcular_acopio


@require_GET
def resumen_campana(request, codigo):
    try:
        campana = Campana.objects.get(codigo=codigo)
    except Campana.DoesNotExist:
        return JsonResponse({"error": "campana_inexistente"}, status=404)

    acopio = calcular_acopio(campana)
    if request.GET.get("explicar") == "1":
        acopio["explicacion"] = explicar_acopio(acopio["resumen"])

    return JsonResponse(acopio)
