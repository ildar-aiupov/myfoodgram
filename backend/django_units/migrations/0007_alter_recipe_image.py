# Generated by Django 3.2 on 2023-08-09 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_units', '0006_alter_recipe_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='recipes/images'),
        ),
    ]
