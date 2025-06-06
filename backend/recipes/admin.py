from django.contrib import admin
from .models import FavoriteDish, ComponentRecipe, Dish, ShoppingCart, ShortUrl


class ComponentRecipeInline(admin.StackedInline):
    model = ComponentRecipe
    extra = 0


@admin.register(ComponentRecipe)
class ComponentRecipeAdmin(admin.ModelAdmin):
    list_display = (
        "recipe",
        "ingredient",
        "amount",
    )
    search_fields = ("recipe__name", "ingredient__name")
    list_filter = ("amount",)


@admin.register(Dish)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "created_at", "favorites_count")
    readonly_fields = ("favorites_count",)
    search_fields = (
        "author__username",
        "name",
    )
    search_help_text = "Поиск по названию блюда и автору"
    list_filter = ("created_at",)
    inlines = (ComponentRecipeInline,)

    @admin.display(description="Добавим в избранное")
    def favorites_count(self, obj):
        return obj.favorites.count()


@admin.register(FavoriteDish)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = (
        "recipe",
        "user",
    )
    search_fields = ("recipe__name", "user__username")


@admin.register(ShortUrl)
class ShortUrlAdmin(admin.ModelAdmin):
    list_display = ("origin_url", "short_url")
    search_fields = ("origin_url", "short_url")
    list_per_page = 20


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        "recipe",
        "user",
    )
    search_fields = ("recipe__name", "user__username")
