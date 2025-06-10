import random
import string
from django.conf import settings
from foodgram.const import max_len_url


def generate_short_token():
    """Генерирует случайный короткий токен для URL"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(max_len_url))