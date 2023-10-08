from django.contrib import admin

from recipes.models import Tag, Recipe, Ingredient, RecipeIngredient, Favorite, ShoppingCart


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


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name',
        'measurement_unit'
    )
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