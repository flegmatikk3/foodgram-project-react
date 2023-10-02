from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.shortcuts import get_object_or_404
from django.db import transaction
from recipes.models import Tag, Recipe, RecipeIngredient, Ingredient, ShoppingCart, Favorite
from users.models import User, Follow
from django.utils.translation import gettext_lazy as _

class UserSerializer(serializers.ModelSerializer):
    # is_subscribed = serializers.SerializerMethodField

    class Meta:
        model = User
        fields = (
            'email', 'id',
            'username',
            'first_name',
            'last_name',
            'password',
            # 'is_subscribed'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            # 'is_subscribed': {'read_only': True}
        }
    
    # def get_is_subscribed(self, obj):
    #    user = self.context.get('request').user
    #    if not user.is_anonymous:
    #        return Follow.objects.filter(user=user, author=obj).exists()
    #    return False
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class TagSerializer(serializers.ModelSerializer):

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
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
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
        return Favorite.objects.filter(user=request.user, recipe=obj.id).exists()
    
    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(author=request.user, recipe=obj.id).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        exclude = ('pub_date')
    

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                _('Minimum 1 ingredient')
            )
        if len(ingredients) != len(set(ingredient['id'] for ingredient in ingredients)):
            raise serializers.ValidationError(
                _('Ingredients should be unique')
            )

    
    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                _('Minimum 1 tag')
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                _('Tags should be unique')
            )

    def create(self, validated_data):
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')

        with transaction.atomic():
            recipe = Recipe.objects.create(author=author, **validated_data)
            recipe.tags.set(tags_data)

            recipe_ingredients = [
                RecipeIngredient(
                    ingredient=get_object_or_404(Ingredient, pk=ingredient['id']),
                    recipe=recipe,
                    amount=ingredient['amount']
                )
                for ingredient in ingredients_data
            ]
            RecipeIngredient.objects.bulk_create(recipe_ingredients)

        return recipe
    
    def to_representation(self, instance):
        return super().to_representation(instance)

