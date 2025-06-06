import os as sys_os
from io import BytesIO as StreamIO
from django.conf import settings as config
from fpdf import FPDF as DocumentPDF
from rest_framework import status as api_status
from rest_framework.generics import get_object_or_404 as fetch_obj
from rest_framework.response import Response as WebResponse
from recipes.models import Dish as DishModel, ShoppingCart as UserBasket
from api.serializers import DishSerializer as DishDataSerializer


class CartProcessor:
    @staticmethod
    def fetch_user_cart(user):
        return [item.recipe for item in UserBasket.objects.filter(user=user)]

    @staticmethod
    def handle_dishes(request):
        dishes = CartProcessor.fetch_user_cart(request.user)
        serializer = DishDataSerializer(dishes, many=True, context={"request": request})
        return serializer.data


class DocumentGenerator:
    def __init__(self, dish_data):
        self.dishes = dish_data
        self.pdf = DocumentPDF()
        self._initialize_pdf()

    def _initialize_pdf(self):
        self.pdf.add_page()
        font_path = sys_os.path.join(config.STATIC_ROOT, "fonts", "DejaVuSans.ttf")
        bold_path = sys_os.path.join(config.STATIC_ROOT, "fonts", "DejaVuSans-Bold.ttf")
        self.pdf.add_font("CoreFont", "", font_path, uni=True)
        self.pdf.add_font("CoreFont", "B", bold_path, uni=True)
        self.pdf.set_font("CoreFont", size=12)

    def create(self):
        self._add_heading("Grocery List", 16, "B", "C")
        self.pdf.ln(10)
        ingredient_list = []

        for dish in self.dishes:
            self._handle_dish(dish, ingredient_list)
            self.pdf.ln(10)

        self._generate_ingredient_summary(ingredient_list)
        pdf_output = self.pdf.output(dest="S").encode("latin-1", errors="ignore")
        return StreamIO(pdf_output)

    def _add_heading(self, text, size=12, style="", align="L"):
        self.pdf.set_font("CoreFont", style, size)
        self.pdf.cell(0, 10, text, ln=True, align=align)
        self.pdf.set_font("CoreFont", "", 12)

    def _handle_dish(self, dish_data, ingredient_list):
        self._add_heading(f"Recipe: {dish_data['name']}", 14, "B")
        creator = dish_data["author"]
        self._add_line(
            f"Author: {creator['first_name']} {creator['last_name']} ({creator['username']})"
        )
        self._add_line(f"Cooking time: {dish_data['cooking_time']} min")
        self.pdf.multi_cell(0, 8, f"Description: {dish_data['text']}")
        self.pdf.ln(5)
        self._add_heading("Ingredients:", 12, "B")

        for ingredient in dish_data["ingredients"]:
            formatted = self._format_ingredient(ingredient)
            self._add_line(formatted)
            ingredient_list.append(ingredient)

    def _add_line(self, text):
        self.pdf.cell(0, 8, text, ln=True)

    def _format_ingredient(self, ingredient):
        return f"- {ingredient['name']} — {ingredient['amount']} {ingredient['measurement_unit']}"

    def _generate_ingredient_summary(self, ingredients):
        self.pdf.ln(10)
        self._add_heading("Full grocery list:", 14, "B")
        unique_ingredients = {}

        for item in ingredients:
            key = (item["name"], item["measurement_unit"])
            if key not in unique_ingredients:
                unique_ingredients[key] = item

        for item in unique_ingredients.values():
            self._add_line(self._format_ingredient(item))


class DishManager:
    @staticmethod
    def generate_pdf(request):
        dishes = CartProcessor.handle_dishes(request)
        pdf_generator = DocumentGenerator(dishes)
        return pdf_generator.create()

    @staticmethod
    def verify_relation(user, obj, relation, field="recipe"):
        if not user or not hasattr(user, relation) or user.is_anonymous:
            return False
        manager = getattr(user, relation)
        return manager.filter(**{field: obj}).exists()

    @staticmethod
    def add_link(request, dish_id, serializer_class):
        fetch_obj(DishModel, pk=dish_id)
        serializer = serializer_class(
            data={"recipe": dish_id, "user": request.user.id},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return WebResponse(serializer.data, status=api_status.HTTP_201_CREATED)

    @staticmethod
    def remove_link(request, dish_id, model_class):
        dish = fetch_obj(DishModel, pk=dish_id)
        deleted, _ = model_class.objects.filter(recipe=dish, user=request.user).delete()
        if not deleted:
            return WebResponse(status=api_status.HTTP_400_BAD_REQUEST)
        return WebResponse(status=api_status.HTTP_204_NO_CONTENT)
