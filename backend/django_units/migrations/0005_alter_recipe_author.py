# Generated by Django 4.2.4 on 2023-08-03 20:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        (
            "django_units",
            "0004_ingredient_recipe_tag_alter_customuser_first_name_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
