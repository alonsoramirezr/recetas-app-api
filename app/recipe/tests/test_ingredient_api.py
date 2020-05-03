from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTest(TestCase):
    # Prueba endpoint publico

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        # Prueba que ese necesario loguearse para acceder
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTest(TestCase):
    # Prueba que se puede acceder a
    # las api privadas de ingredientes

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@londonappdev.com',
            'testpass'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_test(self):
        # Prueba obteniendo lista de ingredientes
        Ingredient.objects.create(user=self.user, name='Sal')
        Ingredient.objects.create(user=self.user, name='Azucar')
        Ingredient.objects.create(user=self.user, name='Harina')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_user(self):
        # Prueba que solo muestre los ingredientes para el usuario autenticado
        user2 = get_user_model().objects.create_user(
            'otro@gmail.com'
            'testpass'
        )
        Ingredient.objects.create(user=user2, name='Vinagre')
        ingredient = Ingredient.objects.create(user=self.user, name='Tomate')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_succesfull(self):
        # Prueba para validar que el ingrediente se agrego con exito
        payload = {'name': 'Cebolla'}
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        # Prueba que valida si el ingrediente no fue ingresado
        # con exito
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
