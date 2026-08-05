from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = "Create admin user"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        username = os.environ.get("ADMIN_USERNAME", "furquankafil")
        email = os.environ.get("ADMIN_EMAIL", "furquankafil7291@gmail.com")
        password = os.environ.get("ADMIN_PASSWORD", "changepasword")

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write("Admin created")
        else:
            self.stdout.write("Admin already exists")