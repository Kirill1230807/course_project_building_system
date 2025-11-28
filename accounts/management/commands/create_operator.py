from django.core.management.base import BaseCommand
from accounts.models import CustomUser

class Command(BaseCommand):
    help = "Створює оператора за замовчуванням"

    def handle(self, *args, **kwargs):
        if not CustomUser.objects.filter(role="operator").exists():
            operator = CustomUser(username="operator", role="operator")
            operator.set_password("operator123")
            operator.save()
            self.stdout.write(self.style.SUCCESS("Оператора створено: operator / operator123"))
        else:
            self.stdout.write("Оператор вже існує")