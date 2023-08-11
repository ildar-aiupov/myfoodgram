from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, max_length=254)
    username = models.CharField(max_length=150, blank=False)
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    password = models.CharField(max_length=150, blank=False)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]


class Recipe(models.Model):
    author = models.ForeignKey(
        "CustomUser", blank=False, on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200, blank=False)
    image = models.ImageField(upload_to="recipes/images", blank=False)
    text = models.CharField(max_length=100, blank=False)
    ingredients = models.ManyToManyField("Ingredient", blank=False)
    tags = models.ManyToManyField("Tag", blank=False)
    cooking_time = models.IntegerField(blank=False)
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-pub_date"]


class Tag(models.Model):
    name = models.CharField(max_length=200, blank=False)
    color = models.CharField(max_length=7, blank=False)
    slug = models.SlugField(max_length=200, blank=False)


class Ingredient(models.Model):
    name = models.CharField(max_length=100, blank=False)
    measurement_unit = models.CharField(max_length=100, blank=False)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE)
    ingredient = models.ForeignKey("Ingredient", on_delete=models.CASCADE)
    amount = models.IntegerField()


class FavoriteRecipe(models.Model):
    recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE)
    user = models.ForeignKey("CustomUser", on_delete=models.CASCADE)


class Subscriber(models.Model):
    user = models.ForeignKey(
        "CustomUser",
        related_name="follower",
        verbose_name="Подписчик",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        "CustomUser",
        related_name="following",
        verbose_name="Автор",
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = [["user", "author"]]


class ShoppingCart(models.Model):
    recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE)
    user = models.ForeignKey("CustomUser", on_delete=models.CASCADE)
