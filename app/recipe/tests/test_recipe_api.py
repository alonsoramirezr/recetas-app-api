from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    # Retorna la url del detalle de la receta
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Main course'):
    # Crea y retorna un tag de ejemplo
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Canela'):
    # Crea y retorna un ingrediente de ejemplo
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    # Crea y retorna una receta de ejemplo
    defaults = {
        'title': 'Receta de ejemplo',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeTestApi(TestCase):
    # Pruebas para probar api publicas

    def setUp(self):
        self.Client = APIClient

    def test_login_required(self):
        # Prueba que requiere autenticacion para obtener las recetas
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeTestApi(TestCase):
    # Prueba que autoriza el acceso a las apis privadas

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password='testpass'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        # Prueba que obtiene las recetas del usuario
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        # Prueba que obtiene las recetas correspondientes del usuario
        user2 = get_user_model().objects.create_user(
            'otrousuario@gmail.com',
            '123456789'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        # Test viendo el detalle de la receta
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        # Prueba para crear una receta nueva
        payload = {
            'title': 'Chocolate cheesecake',
            'time_minutes': 30,
            'price': 5.00
        }
        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        # Creando una receta con tags
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Postre')
        payload = {
            'title': 'Pie de limon',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 20.00
        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        # Prueba creando receta con ingredientes
        ingredient1 = sample_ingredient(user=self.user, name='Pollo')
        ingredient2 = sample_ingredient(user=self.user, name='Arroz')
        payload = {
            'title': 'Pollo con arroz',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 60,
            'price': 15.00
        }
        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)
