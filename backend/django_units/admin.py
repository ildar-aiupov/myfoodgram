from django.contrib import admin

from .models import (
    CustomUser,
    Ingredient,
    Tag,
    Recipe,
    RecipeIngredient,
    FavoriteRecipe,
    ShoppingCart,
    Subscriber,
)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ["id", "username"]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["id", "author"]


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ["id", "recipe", "ingredient", "amount"]


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "recipe"]


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "recipe"]


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "author"]
