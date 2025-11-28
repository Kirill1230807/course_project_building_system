from django.core.management.base import BaseCommand
from accounts.models import CustomUser

class Command(BaseCommand):
    help = "Створює авторизованого користувача за замовчуванням"

    def handle(self, *args, **kwargs):
        if not CustomUser.objects.filter(role="authorized").exists():
            user = CustomUser(username="user", role="authorized")
            user.set_password("user123")
            user.save()
            self.stdout.write(self.style.SUCCESS("Користувача створено: user / user123"))
        else:
            self.stdout.write("Користувач вже існує")
