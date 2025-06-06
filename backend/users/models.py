from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models
from foodgram.const import (
    max_len_email,
    max_len_firstname,
    max_len_surname,
    max_len_name,
)


class BlogerUser(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    email = models.EmailField(
        verbose_name="email",
        unique=True,
        max_length=max_len_email,
        help_text="Адрес email",
    )
    username = models.CharField(
        verbose_name="Логин",
        unique=True,
        max_length=max_len_name,
        validators=[username_validator],
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=max_len_surname,
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=max_len_firstname,
    )
    avatar = models.ImageField(
        verbose_name="Ава",
        upload_to=getattr(settings, "UPLOAD_AVATAR", "users/images/"),
        null=True,
        blank=True,
        default=None,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class SubscriptionPlan(models.Model):
    user = models.ForeignKey(
        verbose_name="Пользователь",
        to=BlogerUser,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    author = models.ForeignKey(
        verbose_name="Ваш блогер",
        to=BlogerUser,
        on_delete=models.CASCADE,
        related_name="subscribers",
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=("user", "author"), name="unique_following"),
        )
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def clean(self):
        if self.user == self.author:
            raise ValidationError("Нельзя накручивать самому себе подписчиков.")
        return super().clean()

    def __str__(self):
        return f"{self.user}"
