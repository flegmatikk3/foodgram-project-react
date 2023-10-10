from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import serializers, status, validators
from users.models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            follower=request.user,
            author=obj.id
        ).exists()

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class TagSerializer(serializers.ModelSerializer):
    pagination_class = None

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id', 'name',
            'measurement_unit', 'amount'
        )


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = RecipeIngredientSerializer(
        many=True, read_only=True,
        source='recipe_ingredients'
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'name', 'image',
            'text', 'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            author=request.user, recipe=obj.id
        ).exists()


class MiniRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id', 'name',
            'image', 'cooking_time'
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time', 'author')

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                _('Minimum 1 ingredient')
            )

        ingredients_list = []
        for item in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=item['id']
            )
            if ingredient in ingredients_list:
                raise serializers.ValidationError(
                    _('Ingredients should be unique')
                )
            if int(item['amount']) <= 0:
                raise serializers.ValidationError(
                    _('Amount should be more than 0!')
                )
            ingredients_list.append(ingredient)

        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                _('Minimum 1 tag')
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                _('Tags should be unique')
            )
        return tags

    def create(self, validated_data):
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')

        with transaction.atomic():
            recipe = Recipe.objects.create(
                author=author, **validated_data
            )
            recipe.tags.set(tags_data)

            recipe_ingredients = [
                RecipeIngredient(
                    ingredient=get_object_or_404(
                        Ingredient, pk=ingredient['id']
                    ),
                    recipe=recipe,
                    amount=ingredient['amount']
                )
                for ingredient in ingredients_data
            ]
            RecipeIngredient.objects.bulk_create(recipe_ingredients)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        instance = super().update(instance, validated_data)

        with transaction.atomic():
            if tags is not None:
                instance.tags.clear()
                instance.tags.set(tags)

            if ingredients is not None:
                new_recipe_ingredients = []
                instance.ingredients.clear()

                for ingredient in ingredients:
                    amount = ingredient['amount']
                    ingredient_id = ingredient['id']
                    ingredient = get_object_or_404(
                        Ingredient, pk=ingredient_id
                    )

                    recipe_ingredient, created = (
                        RecipeIngredient.objects.update_or_create(
                            recipe=instance,
                            ingredient=ingredient,
                            defaults={'amount': amount}
                        )
                    )
                    new_recipe_ingredients.append(recipe_ingredient.pk)

                RecipeIngredient.objects.filter(
                    recipe=instance
                ).exclude(
                    pk__in=new_recipe_ingredients
                ).delete()

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance)
        return serializer.data


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Follow.objects.filter(
                follower=obj.follower,
                author=obj.author).exists()
        return False

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.author)
        if limit and limit.isdigit() and int(limit) > 0:
            recipes = recipes[:int(limit)]
        return MiniRecipeSerializer(recipes, many=True).data

    def validate(self, data):
        author = self.context.get('author')
        user = self.context.get('request').user
        if Follow.objects.filter(author=author, follower=user).exists():
            raise serializers.ValidationError(
                detail=_('You are already following this user!'),
                code=status.HTTP_400_BAD_REQUEST)
        if user == author:
            raise serializers.ValidationError(
                detail=_('You can not subscribe to yourself!'),
                code=status.HTTP_400_BAD_REQUEST)
        return data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message=_(
                    'You have already added this recipe to your favorites'
                )
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = '__all__'
        validators = [
            validators.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message=_(
                    'You have already added this recipe to your shopping cart'
                )
            )
        ]
