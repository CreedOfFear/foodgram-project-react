from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.utils import create_ingredients
from recipes.models import (
    Favourite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
    )
from users.models import Subscription, UserFoodgram


class UserSignUpSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователей."""
    class Meta:
        model = UserFoodgram
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password"
            )


class UserGetSerializer(UserSerializer):
    """Сериализатор для работы с информацией о пользователях."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = UserFoodgram
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed"
            )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        return (
            request.user.is_authenticated
            and Subscription.objects.filter(
                user=request.user, author=obj
            ).exists())


class RecipeSmallSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с краткой информацией о рецепте."""
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time"
            )


class UserSubscribeRepresentSerializer(UserGetSerializer):
    """"Сериализатор для предоставления информации
    о подписках пользователя.
    """
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = UserFoodgram
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count"
            )
        read_only_fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count"
            )

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get("recipes_limit")
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        return RecipeSmallSerializer(
            recipes,
            many=True,
            context={"request": request}
            ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class UserSubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки/отписки от пользователей."""
    class Meta:
        model = Subscription
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=("user", "author"),
                message="Вы уже подписаны на этого пользователя"
            )
        ]

    def validate(self, data):
        request = self.context.get("request")
        if request.user == data["author"]:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя!'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get("request")
        return UserSubscribeRepresentSerializer(
            instance.author, context={"request": request}
        ).data


class TagSerialiser(serializers.ModelSerializer):
    """Сериализатор для работы с тегами."""
    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug"
            )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с ингредиентами."""
    class Meta:
        model = Ingredient
        fields = "__all__"


class IngredientGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации об ингредиентах.
    Используется при работе с рецептами.
    """
    id = serializers.IntegerField(source="ingredient.id", read_only=True)
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurent_unit = serializers.CharField(
        source="ingredient.measurent_unit",
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "name",
            "measurent_unit",
            "amount"
            )


class IngredientPostSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов.
    Используется при работе с рецептами.
    """
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "amount"
            )


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации о рецепте."""
    tags = TagSerialiser(many=True, read_only=True)
    author = UserGetSerializer(read_only=True)
    ingredients = IngredientGetSerializer(many=True, read_only=True,
                                          source="recipeingredients")
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time"
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        return (request and request.user.is_authenticated
                and Favourite.objects.filter(
                    user=request.user, recipe=obj
                ).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        return (
            request and request.user.is_authenticated
            and ShoppingCart.objects.filter(
                    user=request.user, recipe=obj
            ).exists())


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добаления/обновления рецепта."""
    ingredients = IngredientPostSerializer(
        many=True, source="recipeingredients"
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time"
        )

    def validate(self, data):
        ingredients_list = []
        for ingredient in data.get("recipeingredients"):
            if ingredient.get("amount") <= 0:
                raise serializers.ValidationError(
                    'Количество не может быть меньше 1'
                )
            ingredients_list.append(ingredient.get("id"))
        if len(set(ingredients_list)) != len(ingredients_list):
            raise serializers.ValidationError(
                "Вы пытаетесь добавить в рецепт два одинаковых ингредиента"
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")
        ingredients = validated_data.pop("recipeingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        create_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop("recipeingredients")
        tags = validated_data.pop("tags")
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        create_ingredients(ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get("request")
        return RecipeGetSerializer(
            instance,
            context={"request": request}
        ).data
