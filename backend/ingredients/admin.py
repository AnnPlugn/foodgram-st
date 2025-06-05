from django.contrib import admin
from .models import IngredientModel

@admin.register(IngredientModel)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = (
        "name",
        "measurement_unit",
    )