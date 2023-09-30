from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db import models


User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
    
    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        verbose_name = _('Ingredient')
        verbose_name_plural = _('Ingredients')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag)
    name = models.CharField(max_length=200)
    cooking_time = models.PositiveIntegerField() # dobavit validation na min znach
    text = models.TextField()
    image =
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient')
    )
    pub_date = 

    class Meta:
        verbose_name = _('Recipe')
        verbose_name_plural = _('Recipes')
    
    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='recipe_ingredients', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()


class Favorite(models.Model):
    pass


class ShoppingCart(models.Model):
    pass
