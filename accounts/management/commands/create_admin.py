from django.core.management.base import BaseCommand
from accounts.models import CustomUser

class Command(BaseCommand):
    help = "Створює адміністратора за замовчуванням"

    def handle(self, *args, **kwargs):
        if not CustomUser.objects.filter(role="admin").exists():
            admin = CustomUser(username="admin", role="admin")
            admin.set_password("admin123")
            admin.save()
            self.stdout.write(self.style.SUCCESS("Адміністратор створений: admin / admin123"))
        else:
            self.stdout.write("Адміністратор вже існує")