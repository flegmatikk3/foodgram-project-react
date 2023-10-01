from django.shortcuts import render, HttpResponse
from djoser.views import UserViewSet
from rest_framework import viewsets, permissions

from recipes.models import Tag, Recipe, Ingredient
from api.serializers import TagSerializer, RecipeSerializer, RecipeCreateSerializer, IngredientSerializer


class CustomUserViewSet(UserViewSet):
    pass


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def dispatch(self, request, *args, **kwargs):
        res = super().dispatch(request, *args, **kwargs)
        from django.db import connection
        print(len(connection.queries))
        for q in connection.queries:
            print('>>>>', q['sql'])
        return res
    
    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'recipe_ingredients__ingredient', 'tags'
        ).all()
        return recipes
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        return RecipeSerializer # bydet poslozhnee, update serializera..
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
