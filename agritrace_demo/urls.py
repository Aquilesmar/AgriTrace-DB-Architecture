from django.urls import path

from acopio.views import resumen_campana


urlpatterns = [
    path("api/campanas/<slug:codigo>/acopio/", resumen_campana, name="resumen-acopio"),
]
