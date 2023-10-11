from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name',
        'color', 'slug',
    )
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline, )
    list_display = (
        'id', 'name', 'text',
        'cooking_time', 'get_tags', 'get_ingredients', 'get_favorite_count')
    search_fields = (
        'name', 'cooking_time', 'tags__name',
        'author__email', 'ingredients__name')
    list_filter = ('tags', 'author', 'name')

    def get_tags(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])

    def get_ingredients(self, obj):
        return ', '.join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )

    def get_favorite_count(self, obj):
        return obj.favorite_recipes.count()

    def save_model(self, request, obj, form, change):
        if obj.ingredients.count() == 0:
            raise admin.ValidationError(
                "Рецепт должен содержать хотя бы один ингредиент!"
            )
        super().save_model(request, obj, form, change)
        obj.save()


class IngredientResource(resources.ModelResource):
    class Meta:
        model = Ingredient


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin):
    resource_class = IngredientResource
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
    search_fields = ('user',)
    list_filter = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'recipe'
    )
    search_fields = ('author',)
    list_filter = ('author',)
