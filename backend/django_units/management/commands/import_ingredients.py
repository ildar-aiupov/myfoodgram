from django.core.management.base import BaseCommand

from django_units.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('data/ingredients.csv', encoding='utf-8') as f:
            n = 1
            line = f.readline()
            while line:
                data = line.split(",")
                Ingredient.objects.update_or_create(
                    id=n,
                    defaults={"name": data[0],
                              "measurement_unit": data[1]
                              },
                    )
                n += 1
                line = f.readline()
        print("IMPORT INGREDIENTS SUCCESS!!!")
