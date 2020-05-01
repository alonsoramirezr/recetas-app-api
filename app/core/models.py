from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                       PermissionsMixin
from django.conf import settings


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        # Crea y guarda un nuevo crear_usuario
        if not email:
            raise ValueError('El usuario debe un email')
        usuario = self.model(email=self.normalize_email(email), **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)

        return usuario

    def create_superuser(self, email, password):
        # Crea y guarda un nuevo super usuario
        usuario = self.create_user(email, password)
        usuario.is_staff = True
        usuario.is_superuser = True
        usuario.save(using=self._db)

        return usuario


class User(AbstractBaseUser, PermissionsMixin):
    # Modelo custom que soporta el uso de email en vez de el numero de usuario
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Tag(models.Model):
    # Tag que sera usado para una receta
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name
