from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import F, Sum

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from django_units.models import (
    Recipe,
    Tag,
    Ingredient,
    RecipeIngredient,
    FavoriteRecipe,
    Subscriber,
    ShoppingCart,
)

from api.renderers import DownloadRenderer
from api.permissions import IsAuthor
from api.pagination import PageLimitPagination
from api.serializers import (
    UserSerializer,
    UserCreateRequestSerializer,
    UserCreateResponseSerializer,
    UserSetPasswordSerializer,
    IngredientSerializer,
    TagSerializer,
    RecipeSerializer,
    RecipeCreateRequestSerializer,
    RecipeShortSerializer,
    DownloadSerializer,
    SubscriberSerializer,
)


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    pagination_class = PageLimitPagination
    http_method_names = ["get", "post"]
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == "set_password":
            return UserSetPasswordSerializer
        if self.action == "subscriptions":
            return SubscriberSerializer
        if self.request.method == "POST":
            return UserCreateRequestSerializer
        return UserSerializer

    def get_permissions(self):
        if self.get_view_name() == "User Instance" or self.action in [
            "me",
            "set_password",
            "subscriptions",
        ]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_user = User.objects.create_user(**serializer.validated_data)
        return Response(
            UserCreateResponseSerializer(new_user).data,
            status=status.HTTP_201_CREATED,
        )

    @action(["get"], detail=False)
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not self.request.user.check_password(
            serializer.validated_data["current_password"]
        ):
            return Response(
                {"detail": "Учетные данные не были предоставлены."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        self.request.user.set_password(
            serializer.validated_data["new_password"]
        )
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["get"], detail=False)
    def subscriptions(self, request):
        author_ids = Subscriber.objects.filter(user=request.user).values(
            "author__id"
        )
        queryset = User.objects.filter(id__in=author_ids)
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(
            paginated_queryset,
            context={"request": request},
            many=True,
        )
        return paginator.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ModelViewSet):
    http_method_names = ["get"]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)


class TagViewSet(viewsets.ModelViewSet):
    http_method_names = ["get"]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = PageLimitPagination
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_queryset(self):
        queryset = Recipe.objects.all()
        if self.action != "list":
            return queryset
        # фильтрация по is_favorited
        if self.request.GET.get("is_favorited") == "1":
            favorite_recipes_ids = FavoriteRecipe.objects.filter(
                user=self.request.user
            ).values("recipe__id")
            queryset = queryset.filter(id__in=favorite_recipes_ids)
        # фильтрация по is_in_shopping_cart
        if self.request.GET.get("is_in_shopping_cart") == "1":
            recipes_in_shopping_cart_ids = ShoppingCart.objects.filter(
                user=self.request.user
            ).values("recipe__id")
            queryset = queryset.filter(id__in=recipes_in_shopping_cart_ids)
        # фильтрация по author
        author_id = self.request.GET.get("author")
        if author_id:
            queryset = queryset.filter(author__id=int(author_id))
        # фильтрация по tags
        tag_slugs = dict(self.request.GET).get("tags")
        if tag_slugs:
            tag_ids = Tag.objects.filter(slug__in=tag_slugs).values("id")
            queryset = queryset.filter(tags__in=tag_ids).distinct()
        return queryset

    def get_permissions(self):
        if self.action in [
            "create",
            "download_shopping_cart",
        ]:
            return [IsAuthenticated()]
        if self.action in ["destroy", "partial_update"]:
            return [IsAuthor()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action == "download_shopping_cart":
            return DownloadSerializer
        if self.request.method in ["POST", "PATCH"]:
            return RecipeCreateRequestSerializer
        return RecipeSerializer

    def get_renderers(self):
        if (
            self.action == "download_shopping_cart"
            and self.request.user.is_authenticated
        ):
            return [DownloadRenderer()]
        return super().get_renderers()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # извлекаем ингредиенты
        ingredients = serializer.validated_data.pop("ingredients")
        ingredient_ids = [ingredient["id"] for ingredient in ingredients]
        # создаем новый рецепт
        new_recipe = serializer.save(
            ingredients=ingredient_ids, author=request.user
        )
        # заполняем связанную таблицу
        for ingredient in ingredients:
            ingredient_id = ingredient["id"]
            ingredient_amount = ingredient["amount"]
            RecipeIngredient.objects.create(
                recipe=new_recipe,
                ingredient=Ingredient.objects.get(id=ingredient_id),
                amount=ingredient_amount,
            )
        # возвращаем новый рецепт
        return Response(
            RecipeSerializer(new_recipe, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, pk=None):
        updated_recipe = get_object_or_404(Recipe, pk=pk)
        self.check_object_permissions(self.request, updated_recipe)
        serializer = self.get_serializer(
            updated_recipe, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        # извлекаем ингредиенты
        ingredients = serializer.validated_data.pop("ingredients")
        ingredient_ids = [ingredient["id"] for ingredient in ingredients]
        # обновляем рецепт
        serializer.save(ingredients=ingredient_ids)
        # удаляем старые данные из связанной таблицы
        RecipeIngredient.objects.filter(recipe=updated_recipe).delete()
        # заполняем связанную таблицу новыми данными
        for ingredient in ingredients:
            ingredient_id = ingredient["id"]
            ingredient_amount = ingredient["amount"]
            RecipeIngredient.objects.create(
                recipe=updated_recipe,
                ingredient=Ingredient.objects.get(id=ingredient_id),
                amount=ingredient_amount,
            )
        # возвращаем новый рецепт
        return Response(
            RecipeSerializer(
                updated_recipe, context={"request": request}
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(methods=["get"], detail=False)
    def download_shopping_cart(self, request):
        recipes = ShoppingCart.objects.filter(user=request.user).values(
            "recipe"
        )
        queryset = (
            RecipeIngredient.objects.filter(recipe__in=recipes)
            .select_related("ingredient")
            .values("ingredient__name")
            .annotate(total_amount=Sum("amount"))
            .annotate(measurement_unit=F("ingredient__measurement_unit"))
            .annotate(ingredient_name=F("ingredient__name"))
        )
        serializer = self.get_serializer(queryset, many=True)
        file_name = "shopping_cart.txt"
        return Response(
            serializer.data,
            headers={
                "Content-Disposition": f'attachment; filename="{file_name}"'
            },
            status=status.HTTP_200_OK,
        )


class FavoriteViewSet(viewsets.ModelViewSet):
    http_method_names = ["delete", "post"]
    permission_classes = [IsAuthenticated]

    def create(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if FavoriteRecipe.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            return Response(
                {"errors": "Ошибка добавления - рецепт уже в избранном"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        FavoriteRecipe.objects.create(user=request.user, recipe=recipe)
        return Response(
            RecipeShortSerializer(recipe).data,
            status=status.HTTP_201_CREATED,
        )

    @action(methods=["delete"], detail=False)
    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if not FavoriteRecipe.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            return Response(
                {"errors": "Ошибка удаления - рецепта нет в избранном"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        FavoriteRecipe.objects.get(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    http_method_names = ["delete", "post"]
    permission_classes = [IsAuthenticated]

    def create(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            return Response(
                {"errors": "Ошибка добавления - рецепт уже в списке покупок"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ShoppingCart.objects.create(user=request.user, recipe=recipe)
        return Response(
            RecipeShortSerializer(recipe).data,
            status=status.HTTP_201_CREATED,
        )

    @action(methods=["delete"], detail=False)
    def delete(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if not ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            return Response(
                {"errors": "Ошибка удаления - рецепта нет в списке покупок"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ShoppingCart.objects.get(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriberViewSet(viewsets.ModelViewSet):
    http_method_names = ["post", "delete"]
    permission_classes = [IsAuthenticated]

    def create(self, request, author_id):
        author = get_object_or_404(User, id=author_id)
        if request.user == author:
            return Response(
                {"errors": "Ошибка - нельзя подписать на себя"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Subscriber.objects.filter(
            user=request.user, author=author
        ).exists():
            return Response(
                {"errors": "Ошибка - подписка на этого автора уже оформлена"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Subscriber.objects.create(user=request.user, author=author)
        return Response(
            SubscriberSerializer(author, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(methods=["delete"], detail=False)
    def delete(self, request, author_id):
        author = get_object_or_404(User, id=author_id)
        if not Subscriber.objects.filter(
            user=request.user, author=author
        ).exists():
            return Response(
                {"errors": "Ошибка удаления - подписки на этого автора нет"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Subscriber.objects.get(user=request.user, author=author).delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
