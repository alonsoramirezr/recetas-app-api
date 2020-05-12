from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

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

    def test_retrieve_ingredientes_assigned_to_recipe(self):
        # Prueba filtrando ingredientes a aquellas asignadas a la receta
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='Manzanas'
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name='Pavo'
        )
        recipe = Recipe.objects.create(
            title='Pavo con pure de manzana',
            time_minutes=5,
            price=10,
            user=self.user
        )
        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_assigned_by_unique(self):
        # Prueba filtrando ingredientes asignados retornando items unicos
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Papas'
        )
        Ingredient.objects.create(
            user=self.user,
            name='Champinon'
        )
        recipe1 = Recipe.objects.create(
            title='Pescado con pure',
            time_minutes=30,
            price=15,
            user=self.user
        )
        recipe1.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            title='Pizza',
            time_minutes=15,
            price=10,
            user=self.user
        )
        recipe2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
