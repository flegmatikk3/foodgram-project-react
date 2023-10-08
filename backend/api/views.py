from django.shortcuts import render, HttpResponse
from djoser.views import UserViewSet
from rest_framework import viewsets, permissions, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from django.utils.translation import gettext_lazy as gtl
from datetime import date
from django.db.models import Sum

from recipes.models import Tag, Recipe, Ingredient, ShoppingCart, Favorite, RecipeIngredient
from .serializers import TagSerializer, RecipeSerializer, RecipeCreateSerializer, IngredientSerializer, UserSerializer, FollowSerializer
from .permission import IsAuthorOrReadOnly, AuthenticatedOrReadOnly
from .pagination import CustomPagination
from .filters import IngredientFilter, RecipeFilter
from users.models import User, Follow


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    permission_classes = (AuthenticatedOrReadOnly,)

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_me(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
    
        elif request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data, partial=True, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated], serializer_class=FollowSerializer,)
    def subscribe(self, request, **kwargs):
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        user = self.request.user

        if request.method == 'POST':
            serializer = FollowSerializer(data=request.data, context={'request': request, 'author': author})
            if serializer.is_valid(raise_exception=True):
                serializer.save(follower=user, author=author)
                message = gtl('Subscription successfully created')
                status_code = status.HTTP_201_CREATED
            else:
                message = gtl('Object not found')
                status_code = status.HTTP_404_NOT_FOUND
        else:
            if Follow.objects.filter(follower=user, author=author).exists():
                Follow.objects.get(follower=user, author=author).delete()
                message = gtl('Successful unsubscription')
                status_code = status.HTTP_204_NO_CONTENT
            else:
                message = gtl('Object not found')
                status_code = status.HTTP_404_NOT_FOUND
    
        return Response({'message': message}, status=status_code)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = self.request.user
        queryset = Follow.objects.filter(follower=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages, many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    
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
                return Response({'message': gtl('Recipe added to shopping cart.')},
                                status=status.HTTP_201_CREATED)
            else:
                return Response({'errors': gtl('Recipe is already in shopping cart.')},
                                status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            deleted, _ = ShoppingCart.objects.filter(author=user, recipe=recipe).delete()
            if deleted:
                return Response({'message': gtl('Recipe deleted from shopping cart.')},
                                status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'errors': gtl('Recipe not found in shopping cart.')},
                                status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        user = self.request.user

        if request.method == 'POST':
            created = Favorite.objects.get_or_create(user=user, recipe=recipe)
            if created:
                return Response({'message': gtl('Recipe added to favorite.')},
                                status=status.HTTP_201_CREATED)
            else:
                return Response({'errors': gtl('Recipe already in favorite.')},
                                status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            deleted, _ = Favorite.objects.filter(user=user, recipe=recipe).delete()
            if deleted:
                return Response({'message': gtl('Recipe deleted from favorite.')},
                                status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'errors': gtl('Recipe not found in favorites.')},
                                status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        author = User.objects.get(id=self.request.user.pk)
        if author.shopping_cart.exists():
            ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__author=author
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit'
            ).annotate(
                amounts=Sum('amount', distinct=True)
            ).order_by('amounts')

            today = date.today().strftime("%d-%m-%Y")
            shopping_list = f'Список покупок на: {today}\n\n'

            for ingredient in ingredients:
                shopping_list += (
                    f'{ingredient["ingredient__name"]} - '
                    f'{ingredient["amounts"]} '
                    f'{ingredient["ingredient__measurement_unit"]}\n'
                )

            filename = 'shopping_list.txt'
    
            response = HttpResponse(shopping_list, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename={filename}'
            return response
        return Response(
            gtl('The shopping list is empty.'),
            status=status.HTTP_404_NOT_FOUND
        )
