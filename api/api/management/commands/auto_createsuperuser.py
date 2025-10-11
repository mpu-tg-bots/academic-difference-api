"""
Это команда, которая позволяет создавать суперпользователя автоматически
при деплое проекта
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    """Реализация команды"""

    help = "Create a superuser with predefined credentials"

    def add_arguments(self, parser):
        """Получаем аргументы из командной строки"""
        parser.add_argument(
            "--username", type=str, help="Username for the superuser"
        )
        parser.add_argument(
            "--password", type=str, help="Password for the superuser"
        )

    def handle(self, *args, **options):
        username = options.get("username")
        password = options.get("password")

        if not User.objects.filter(username=username).exists():
            self.stdout.write(f"Creating account for {username}")

            User.objects.create_superuser(username=username, password=password)

            self.stdout.write("Superuser created successfully!")
        else:
            self.stdout.write("Superuser already exists. Skipping.")
