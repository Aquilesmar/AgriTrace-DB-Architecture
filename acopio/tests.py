import json
from io import BytesIO
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Campana, Cupo, Entrega, Productor
from .services import calcular_acopio


class AcopioTests(TestCase):
    fixtures = ["acopio_demo"]

    def consultar(self, campana="demo-2026"):
        return self.client.get(reverse("resumen-acopio", args=[campana]))

    def consultar_productor(self, codigo):
        respuesta = self.consultar()
        self.assertEqual(respuesta.status_code, 200)
        return next(fila for fila in respuesta.json()["productores"] if fila["productor"] == codigo)

    def test_saldo_normal_suma_entregas(self):
        productor = self.consultar_productor("P-001")

        self.assertEqual(productor["acopiado_kg"], 600)
        self.assertEqual(productor["saldo_kg"], 400)
        self.assertIs(productor["desvio"], False)

    def test_saldo_cero_sin_desvio(self):
        productor = self.consultar_productor("P-002")

        self.assertEqual(productor["saldo_kg"], 0)
        self.assertIs(productor["desvio"], False)

    def test_exceso_conserva_saldo_negativo_y_marca_desvio(self):
        productor = self.consultar_productor("P-003")

        self.assertEqual(productor["cupo_kg"], 500)
        self.assertEqual(productor["acopiado_kg"], 625)
        self.assertEqual(productor["saldo_kg"], -125)
        self.assertIs(productor["desvio"], True)

    def test_campana_inexistente(self):
        respuesta = self.consultar("inexistente")

        self.assertEqual(respuesta.status_code, 404)
        self.assertEqual(respuesta.json(), {"error": "campana_inexistente"})

    def test_resumen_cuenta_excesos_sin_compensarlos_con_saldos_positivos(self):
        campana = Campana.objects.get(codigo="demo-2026")

        self.assertEqual(
            calcular_acopio(campana)["resumen"],
            {
                "productores_con_cupo": 3,
                "cupo_total_kg": 2300,
                "acopiado_total_kg": 2025,
                "productores_con_desvio": 1,
                "exceso_total_kg": 125,
            },
        )

    def test_cupo_sin_entregas_y_aislamiento_entre_campanas(self):
        otra_campana = Campana.objects.create(codigo="otra-campana")
        productor = Productor.objects.get(codigo="P-001")
        cupo = Cupo.objects.create(campana=otra_campana, productor=productor, limite_kg=100)

        respuesta = self.consultar("otra-campana")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            respuesta.json()["productores"],
            [{
                "productor": "P-001",
                "cupo_kg": 100,
                "acopiado_kg": 0,
                "saldo_kg": 100,
                "desvio": False,
            }],
        )

        Entrega.objects.create(cupo=cupo, peso_kg=110)
        self.assertEqual(self.consultar_productor("P-001")["acopiado_kg"], 600)

    @override_settings(AGRITRACE_EXPLICADOR="simulado", GEMINI_API_KEY=None)
    @patch("acopio.explicacion.urlopen")
    def test_explicacion_simulada_usa_resumen_sin_red(self, urlopen):
        url = reverse("resumen-acopio", args=["demo-2026"])
        respuesta = self.client.get(url, {"explicar": "1"})

        self.assertEqual(respuesta.status_code, 200)
        explicacion = respuesta.json()["explicacion"]
        self.assertEqual(explicacion["modo"], "simulado")
        self.assertEqual(explicacion["estado"], "ok")
        self.assertIn("El exceso acumulado fue de 125 kg.", explicacion["texto"])
        urlopen.assert_not_called()

    @override_settings(AGRITRACE_EXPLICADOR="gemini", GEMINI_API_KEY="clave-ficticia")
    @patch("acopio.explicacion.urlopen")
    def test_gemini_recibe_solo_los_indicadores_agregados(self, urlopen):
        texto = "Hubo desvíos en 1 de 3 productores."
        proveedor = {"candidates": [{"content": {"parts": [{"text": texto}]}}]}
        urlopen.return_value = BytesIO(json.dumps(proveedor).encode())
        url = reverse("resumen-acopio", args=["demo-2026"])
        respuesta = self.client.get(url, {"explicar": "1"})

        self.assertEqual(respuesta.status_code, 200)
        acopio = respuesta.json()
        self.assertEqual(acopio["explicacion"], {"modo": "gemini", "estado": "ok", "texto": texto})
        peticion = urlopen.call_args.args[0]
        prompt = json.loads(peticion.data)["contents"][0]["parts"][0]["text"]
        self.assertEqual(json.loads(prompt.splitlines()[-1]), acopio["resumen"])
        self.assertNotIn("P-003", prompt)
        self.assertNotIn("clave-ficticia", peticion.full_url)
        self.assertEqual(peticion.get_header("X-goog-api-key"), "clave-ficticia")
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 5)

    @override_settings(AGRITRACE_EXPLICADOR="gemini", GEMINI_API_KEY="clave-ficticia")
    @patch("acopio.explicacion.urlopen", side_effect=TimeoutError)
    def test_fallo_de_gemini_conserva_indicadores_y_saldo_negativo(self, urlopen):
        url = reverse("resumen-acopio", args=["demo-2026"])
        esperado = self.client.get(url).json()
        self.assertNotIn("explicacion", esperado)
        urlopen.assert_not_called()

        with self.assertLogs("acopio.explicacion", level="WARNING"):
            respuesta = self.client.get(url, {"explicar": "1"})

        self.assertEqual(respuesta.status_code, 200)
        acopio = respuesta.json()
        self.assertEqual(
            acopio.pop("explicacion"),
            {"modo": "gemini", "estado": "no_disponible", "texto": None},
        )
        self.assertEqual(acopio, esperado)
        self.assertEqual(acopio["productores"][2]["saldo_kg"], -125)
        self.assertIs(acopio["productores"][2]["desvio"], True)
        urlopen.assert_called_once()
