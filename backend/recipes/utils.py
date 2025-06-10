# recipes/utils.py
import random
from django.conf import settings


def generate_short_token(model_class):
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
        if not model_class.objects.filter(short_url=short_url).exists():
            return short_url
        attempt += 1
    raise ValueError(
        f"Не удалось сгенерировать пользовательский токен после {max_attempts} попыток"
    )
