from django.db import models
from foodgram.const import max_len_ingredient

class IngredientModel(models.Model):
    name = models.CharField(
        "Название", max_length=max_len_ingredient, db_index=True
    )
    measurement_unit = models.CharField("Ед измерения", max_length=64)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="name_measurement_unit",
            )
        ]

    def __str__(self):
        return f"{self.name}"