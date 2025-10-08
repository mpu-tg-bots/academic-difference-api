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
        parser.add_argument("--email", type=str, help="Email for the superuser")
        parser.add_argument(
            "--password", type=str, help="Password for the superuser"
        )

    def handle(self, *args, **options):
        """Создаём суперпользователя"""

        username = options["username"]
        email = options["email"]
        password = options["password"]

        if not all([username, email, password]):
            self.stdout.write(
                self.style.ERROR(
                    "Username, email, and password must be provided."
                )
            )
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Superuser "{username}" already exists.')
            )
        else:
            User.objects.create_superuser(
                username=username, email=email, password=password
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Superuser "{username}" created successfully.'
                )
            )
