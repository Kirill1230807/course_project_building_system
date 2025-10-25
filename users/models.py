from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Розширена модель користувача.
    Ми успадковуємо AbstractUser, щоб отримати всі стандартні поля Django
    (username, email, password, first_name, last_name і т.д.)
    і просто додаємо наше поле 'role'.
    """
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Адміністратор"
        OPERATOR = "OPERATOR", "Оператор"
        GUEST = "GUEST", "Гість"

    # Додаємо поле 'role' до нашої моделі
    role = models.CharField(
        max_length=50,
        choices=Role.choices,
        default=Role.GUEST  # Кожен новий користувач за замовчуванням буде "Гостем"
    )