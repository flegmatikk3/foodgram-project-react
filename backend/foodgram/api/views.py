from django.shortcuts import render, HttpResponse
from djoser.views import UserViewSet
from rest_framework import viewsets, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import get_object_or_404
from django.utils.translation import gettext_lazy as _

from recipes.models import Tag, Recipe, Ingredient, ShoppingCart, Favorite
from .serializers import TagSerializer, RecipeSerializer, RecipeCreateSerializer, IngredientSerializer, UserSerializer, FollowSerializer
from .permission import IsAuthorOrReadOnly
from .pagination import CustomPagination
from users.models import User, Follow


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    @api_view(['GET', 'PATCH'])
    @permission_classes([IsAuthenticated])
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

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, *args, **kwargs):
        author = get_object_or_404(User, id=self.kwargs.get('pk'))
        user = self.request.user

        if request.method == 'POST':
            serializer = FollowSerializer(data=request.data, context={'request': request, 'author': author})
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=author, user=user)
                message = _('Subscription successfully created')
                status_code = status.HTTP_201_CREATED
            else:
                message = _('Object not found')
                status_code = status.HTTP_404_NOT_FOUND
        else:
            if Follow.objects.filter(author=author, user=user).exists():
                Follow.objects.get(author=author, user=user).delete()
                message = _('Successful unsubscription')
                status_code = status.HTTP_204_NO_CONTENT
            else:
                message = _('Object not found')
                status_code = status.HTTP_404_NOT_FOUND
    
        return Response({'message': message}, status=status_code)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        follows = Follow.objects.filter(user=request.user)
        serializer = FollowSerializer(follows, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
