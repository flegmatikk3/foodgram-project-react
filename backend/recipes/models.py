from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User

from .constraints import COL, LEN


class Tag(models.Model):
    name = models.CharField(_('title'), max_length=LEN, unique=True)
    color = models.CharField(_('color'), max_length=COL, unique=True)
    slug = models.SlugField(_('slug of tag'), max_length=LEN, unique=True)

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(_('title'), max_length=LEN)
    measurement_unit = models.CharField(_('measurement unit'), max_length=LEN)

    class Meta:
        verbose_name = _('Ingredient')
        verbose_name_plural = _('Ingredients')
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag, verbose_name=_('tags'))
    name = models.CharField(_('title'), max_length=LEN)

    cooking_time = models.PositiveIntegerField(
        _('cookings time in minutes'),
        validators=[
            MinValueValidator(
                1, message=_('minimal time to cook is 1 minute')
            )
        ]
    )

    text = models.TextField(_('description'))
    image = models.ImageField(_('image'), upload_to='media/')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('author')
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        verbose_name=_('ingredients')
    )
    pub_date = models.DateTimeField(
        _('publication date'),
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _('Recipe')
        verbose_name_plural = _('Recipes')
        ordering = ('-id',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredients',
        on_delete=models.CASCADE,
        verbose_name=_('recipe')
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name=_('ingredient')
    )
    amount = models.PositiveIntegerField(
        _('amount'),
        validators=[
            MinValueValidator(
                1, message=_('minimal amount of ingredients 1')
            )
        ]
    )

    class Meta:
        verbose_name = _('ingredient in recipe')
        verbose_name_plural = _('ingredients in recipe')
        ordering = ('-id',)

    def __str__(self):
        return f'{self.ingredient} {self.amount}'


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('recipe'),
        related_name='favorite_recipes',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('user'),
        related_name='favorite_recipes',
    )

    class Meta:
        verbose_name = _('favorite')
        verbose_name_plural = _('favorites')
        constraints = (
            models.UniqueConstraint(
                name='favorite_recipe',
                fields=['user', 'recipe']
            )
        ),

    def __str__(self):
        return _(f"{self.recipe} in {self.user}'s favorites")


class ShoppingCart(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name=_('author'),
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name=_('recipe'),
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )

    class Meta:
        verbose_name = _('shopping cart')
        verbose_name_plural = _('shopping cart')
        constraints = (
            models.UniqueConstraint(
                name='unique_cart',
                fields=['author', 'recipe']
            )
        ),

    def __str__(self):
        return f'{self.recipe}'
