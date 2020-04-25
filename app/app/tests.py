from django.test import TestCase
from app.calc import add, substraccion


class CalcTest(TestCase):
    def test_add_numbers(self):
        # Prueba unitaria de la funcion adduser
        self.assertEqual(add(3, 8), 11)

    def test_substraer_numeros(self):
        self.assertEqual(substraccion(5, 11), 6)
