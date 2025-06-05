import json
from django.core.management.base import BaseCommand
from ingredients.models import IngredientModel


class Command(BaseCommand):
    help = "Загружает ингредиенты"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Путь к файлу")

    def handle(self, *args, **options):
        file_path = options["file_path"]
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            IngredientModel.objects.bulk_create(
                [
                    IngredientModel(
                        name=item["name"],
                        measurement_unit=item["measurement_unit"],
                    )
                    for item in data
                ],
                ignore_conflicts=True,
            )
        self.stdout.write(self.style.SUCCESS("Ингредиенты успешно добавлены"))
