from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def sample_user(email='test@londonappdev.com', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_succesful(self):
        # Prueba creando un nuevo usuario de manera exitosa
        email = 'prueba@gmail.com'
        password = 'prueba123'
        usuario = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(usuario.email, email)
        self.assertTrue(usuario.check_password(password))

    def test_nuevo_usuario_email_normalizado(self):
        # Prueba creada para validar correo a lower-case
        email = 'prueba@GMAIL.COM'
        usuario = get_user_model().objects.create_user(email, 'prueba123')

        self.assertEqual(usuario.email, email.lower())

    def test_nuevo_usuario_email_invalido(self):
        # Prueba creada para validar que el email es valido
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_super_usuario_creado(self):
        # Prueba creando un nuevo superusuario
        usuario = get_user_model().objects.create_superuser(
            'test@gmail.com',
            'test123'
        )

        self.assertTrue(usuario.is_superuser)
        self.assertTrue(usuario.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        # Prueba la representacion por string del ingrediente
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        # Prueba que se puede convetir a string
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Carne con champiñon',
            time_minutes=5,
            price=5.00
        )

        self.assertEqual(str(recipe), recipe.title)
