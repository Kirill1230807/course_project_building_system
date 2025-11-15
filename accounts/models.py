from django.db import models
import hashlib

class CustomUser(models.Model):
    ROLE_CHOICES = (
        ("admin", "Адміністратор СД"),
        ("operator", "Оператор СД"),
        ("authorized", "Авторизований"),
        ("guest", "Гість"),
    )

    class Meta:
        db_table = "Keys"

    username = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="guest")
    created_at = models.DateTimeField(auto_now_add=True)
    reset_code = models.CharField(max_length=10, null=True, blank=True)

    def set_password(self, raw_password: str):
        self.password_hash = hashlib.sha256(raw_password.encode()).hexdigest()

    def check_password(self, raw_password: str):
        return self.password_hash == hashlib.sha256(raw_password.encode()).hexdigest()

    def __str__(self):
        return f"{self.username} ({self.role})"

class GuestRequest(models.Model):
    STATUS_CHOICES = (
        ("new", "Нова"),
        ("approved", "Схвалена"),
        ("rejected", "Відхилена"),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заявка {self.user.username} - {self.status}"