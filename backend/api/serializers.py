import re

from drf_extra_fields.fields import Base64ImageField

from django.contrib.auth import get_user_model
from django.db.models import F

from rest_framework import serializers

from django_units.models import (
    Ingredient,
    Tag,
    Recipe,
    RecipeIngredient,
    FavoriteRecipe,
    ShoppingCart,
    Subscriber,
)


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        return (
            request.user.is_authenticated
            and Subscriber.objects.filter(
                user=request.user, author=obj
            ).exists()
        )


class UserCreateRequestSerializer(serializers.ModelSerializer):
    def validate_username(self, name):
        if not re.match(r"^[\w.@+-]+\Z", name):
            raise serializers.ValidationError("Недопустимое имя пользователя.")
        return name

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        ]


class UserCreateResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
        ]


class UserSetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=100)
    current_password = serializers.CharField(max_length=100)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = [
            "id",
            "name",
            "measurement_unit",
        ]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            "id",
            "name",
            "color",
            "slug",
        ]


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(many=False)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        ]

    def get_ingredients(self, obj):
        return (
            RecipeIngredient.objects.filter(recipe=obj)
            .select_related("ingredient")
            .values(
                "ingredient__id",
                "ingredient__name",
                "ingredient__measurement_unit",
                "amount",
            )
            .annotate(id=F("ingredient__id"))
            .annotate(name=F("ingredient__name"))
            .annotate(measurement_unit=F("ingredient__measurement_unit"))
            .values("id", "name", "measurement_unit", "amount")
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        return (
            request.user.is_authenticated
            and FavoriteRecipe.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        return (
            request.user.is_authenticated
            and ShoppingCart.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        )


class RecipeCreateRequestSerializer(serializers.ModelSerializer):
    ingredients = serializers.ListField(child=serializers.DictField())
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        ]

    def validate_ingredients(self, ingredients):
        ingredient_ids = [ingredient["id"] for ingredient in ingredients]
        if len(set(ingredient_ids)) < len(ingredient_ids):
            raise serializers.ValidationError("Дубли ингредиентов")
        if len(Ingredient.objects.in_bulk(ingredient_ids)) < len(
            ingredient_ids
        ):
            raise serializers.ValidationError("Не существующие ингредиенты")
        return ingredients


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            "id",
            "name",
            "image",
            "cooking_time",
        ]


class DownloadSerializer(serializers.Serializer):
    ingredient_name = serializers.CharField()
    total_amount = serializers.IntegerField()
    measurement_unit = serializers.CharField()


class SubscriberSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        return (
            request.user.is_authenticated
            and Subscriber.objects.filter(
                user=request.user, author=obj
            ).exists()
        )

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes_limit = int(request.GET.get("recipes_limit", 99999))
        queryset = Recipe.objects.filter(author=obj)[:recipes_limit]
        serializer = RecipeShortSerializer(instance=queryset, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()
