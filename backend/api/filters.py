from django_filters.rest_framework import CharFilter, FilterSet, BooleanFilter
from ingredients.models import IngredientModel
from recipes.models import Dish


class ComponentFilter(FilterSet):
    name = CharFilter(field_name="name", lookup_expr="istartswith")

    class Meta:
        model = IngredientModel
        fields = ("name",)


class DishFilter(FilterSet):
    is_favorited = BooleanFilter(method="filter_favorited")
    is_in_shopping_cart = BooleanFilter(method="filter_in_shopping_cart")

    class Meta:
        model = Dish
        fields = ("author", "is_favorited", "is_in_shopping_cart")

    def filter_favorited(self, queryset, name, value):
        return self.filter_by_user(queryset, "favorites", value)

    def filter_in_shopping_cart(self, queryset, name, value):
        return self.filter_by_user(queryset, "shopping_cart", value)

    def filter_by_user(self, queryset, field, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(**{f"{field}__user": user})
        return queryset
