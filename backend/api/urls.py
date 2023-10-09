from rest_framework import routers
from django.urls import path, include
from .views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                    TagViewSet)


router = routers.DefaultRouter()
router.register('users', CustomUserViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
]