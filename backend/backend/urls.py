from django.contrib import admin
from django.urls import include, path

from rest_framework.routers import DefaultRouter

from api.views import (
    UserViewSet,
    IngredientViewSet,
    TagViewSet,
    RecipeViewSet,
    FavoriteViewSet,
    ShoppingCartViewSet,
    SubscriberViewSet,
)


router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("tags", TagViewSet)
router.register("ingredients", IngredientViewSet)
router.register(
    "recipes/(?P<recipe_id>[^/.]+)/favorite",
    FavoriteViewSet,
    basename="favorite",
)
router.register(
    "recipes/(?P<recipe_id>[^/.]+)/shopping_cart",
    ShoppingCartViewSet,
    basename="shopping_cart",
)
router.register(
    "users/(?P<author_id>[^/.]+)/subscribe",
    SubscriberViewSet,
    basename="subscribe",
)
router.register("recipes", RecipeViewSet, basename="recipes")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/auth/", include("djoser.urls.authtoken")),
]
