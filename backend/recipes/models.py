from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
import random
from foodgram.const import max_len_recipe, max_len_url
from ingredients.models import IngredientModel
from django.contrib.auth import get_user_model

User = get_user_model()


class Dish(models.Model):
    name = models.CharField(
        verbose_name="Название вашего шедевра",
        max_length=max_len_recipe,
        db_index=True,
    )
    text = models.TextField(verbose_name="Описание")
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время готовки (мин)",
        validators=[
            MinValueValidator(
                limit_value=1, message="Вы не флеш готовка не может быть меньше 1 мин!"
            ),
            MaxValueValidator(
                limit_value=14400,
                message=(
                    "Макс значение",
                    "вы не улитка готовьте меньше 10 дней (14 400 минут)!",
                ),
            ),
        ],
        help_text="Введите число большее или равное 1",
    )
    image = models.ImageField(
        verbose_name="Фото",
        upload_to=getattr(settings, "UPLOAD_RECIPES", "recipes/images/"),
    )
    ingredients = models.ManyToManyField(
        to=IngredientModel,
        verbose_name="Ингредиенты",
        through="ComponentRecipe",
    )
    author = models.ForeignKey(
        verbose_name="Имя повара",
        to=User,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(verbose_name="Добавлено", auto_now_add=True)

    class Meta:
        default_related_name = "recipes"
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-created_at",)

    def __str__(self):
        return self.name


class ComponentRecipe(models.Model):
    recipe = models.ForeignKey(verbose_name="Рецепт", to=Dish, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        verbose_name="Ингредиент", to=IngredientModel, on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Кол-во",
        validators=[
            MinValueValidator(
                limit_value=1,
                message="Количество ингредиентов не может быть меньше 1!",
            ),
            MaxValueValidator(
                limit_value=10000,
                message="Количество ингредиентов не может быть больше 10000!",
            ),
        ],
    )

    class Meta:
        default_related_name = "ingredient_recipes"
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"

    def __str__(self):
        return f"{self.ingredient}"


class FavoriteDish(models.Model):
    recipe = models.ForeignKey(verbose_name="Рецепт", to=Dish, on_delete=models.CASCADE)
    user = models.ForeignKey(
        verbose_name="Пользователь",
        to=User,
        on_delete=models.CASCADE,
    )

    class Meta:
        default_related_name = "favorites"
        verbose_name = "Любимый рецепт"
        verbose_name_plural = "Любимые рецепты"

    def __str__(self):
        return str(self.recipe)


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(verbose_name="Рецепт", to=Dish, on_delete=models.CASCADE)
    user = models.ForeignKey(
        verbose_name="Кулинар",
        to=User,
        on_delete=models.CASCADE,
    )

    class Meta:
        default_related_name = "shopping_cart"
        verbose_name = "Рецепт в корзине"
        verbose_name_plural = "Рецепты в корзине"

    def __str__(self):
        return str(self.recipe)


class ShortUrl(models.Model):
    origin_url = models.URLField(
        verbose_name="Исходная ссылка", primary_key=True, max_length=200
    )
    short_url = models.SlugField(
        verbose_name="Короткая ссылка",
        max_length=max_len_url,
        unique=True,
        db_index=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Короткая ссылка"
        verbose_name_plural = "Короткие ссылки"

    def __str__(self):
        return self.short_url

    def save(self, *args, **kwargs):
        if not self.short_url:
            self.short_url = self.generate_short_token()
        super().save(*args, **kwargs)

    @classmethod
    def generate_short_token(cls):
        max_attempts = 100
        attempt = 0
        while attempt < max_attempts:
            token = "".join(
                random.choices(
                    settings.CHARACTERS_SHORT_URL,
                    k=settings.TOKEN_LENGTH_SHORT_URL,
                )
            )
            short_url = f"/s/{token}/"
            if not cls.objects.filter(short_url=short_url).exists():
                return short_url
            attempt += 1
        raise ValueError(
            f"Не удалось сгенерировать пользовательский токен после {max_attempts} попыток"
        )
