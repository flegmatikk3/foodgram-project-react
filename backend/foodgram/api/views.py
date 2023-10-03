from django.shortcuts import render, HttpResponse
from djoser.views import UserViewSet
from rest_framework import viewsets, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from django.utils.translation import gettext_lazy as _

from recipes.models import Tag, Recipe, Ingredient, ShoppingCart, Favorite
from .serializers import TagSerializer, RecipeSerializer, RecipeCreateSerializer, IngredientSerializer
from .permission import IsAuthorOrReadOnly
from .pagination import CustomPagination


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
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnly,)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        return RecipeSerializer

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        user = self.request.user

        if request.method == 'POST':
            created = ShoppingCart.objects.get_or_create(author=user, recipe=recipe)
            if created:
                return Response({'message': _('Recipe added to shopping cart.')},
                                status=status.HTTP_201_CREATED)
            else:
                return Response({'errors': _('Recipe is already in shopping cart.')},
                                status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            deleted, _ = ShoppingCart.objects.filter(author=user, recipe=recipe).delete()
            if deleted:
                return Response({'message': _('Recipe deleted from shopping cart.')},
                                status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'errors': _('Recipe not found in shopping cart.')},
                                status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        user = self.request.user

        if request.method == 'POST':
            created = Favorite.objects.get_or_create(author=user, recipe=recipe)
            if created:
                return Response({'message': _('Recipe added to favorite.')},
                                status=status.HTTP_201_CREATED)
            else:
                return Response({'errors': _('Recipe already in favorite.')},
                                status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            deleted, _ = Favorite.objects.filter(author=user, recipe=recipe).delete()
            if deleted:
                return Response({'message': _('Recipe deleted from favorite.')},
                                status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'errors': _('Recipe not found in favorites.')},
                                status=status.HTTP_404_NOT_FOUND)

