from rest_framework import serializers

from recipes.models import Tag, Recipe, RecipeIngredient, Ingredient, ShoppingCart, Favorite
from users.models import User, Follow

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
    # is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
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
            # 'is_in_shopping_cart',
        )
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj.id).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientCreateSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('tags', 'name', 'cooking_time', 'text', 'ingredients')

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance = super().create(validated_data)

        for ingredient_data in ingredients:
            RecipeIngredient(
                recipe=instance,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            ).save() # вместо этого лучше использовать балк криейт

        return instance
    
    def to_representation(self, instance):
        return super().to_representation(instance)

