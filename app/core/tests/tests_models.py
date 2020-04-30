from django.test import TestCase
from django.contrib.auth import get_user_model


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
