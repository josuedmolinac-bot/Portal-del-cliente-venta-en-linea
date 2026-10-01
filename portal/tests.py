from django.test import TestCase
from django.urls import reverse


class InicioTests(TestCase):
    def test_inicio_responde_correctamente(self):
        response = self.client.get(reverse("portal:inicio"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Portal del Cliente")

    def test_salud_entrega_estado(self):
        response = self.client.get(reverse("portal:salud"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"estado": "disponible"})

    def test_inicio_rechaza_metodo_post(self):
        response = self.client.post(reverse("portal:inicio"))
        self.assertEqual(response.status_code, 405)
