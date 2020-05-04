from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe

from recipe import serializers


class BaseRecipeAtributes(viewsets.GenericViewSet, mixins.ListModelMixin,
                          mixins.CreateModelMixin):
    # Clase base para poder usar con tag y ingrediente
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        # Retorna objetos para el usuario autenticado
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        # Crea un nuevo objeto
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAtributes):
    """Manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAtributes):
    # Administra los ingredientes en la base de datos
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    # Adminstra las recetas en la BD
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        # Obtiene las recetas del usuario logeado
        return self.queryset.filter(user=self.request.user)
