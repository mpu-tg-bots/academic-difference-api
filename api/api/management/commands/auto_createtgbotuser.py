from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from rest_framework.authtoken.models import Token

User = get_user_model()


class Command(BaseCommand):
    help = "Создает или обновляет пользователя-бота и его API токен из переменных окружения."

    def add_arguments(self, parser):
        """Получаем аргументы из командной строки"""
        parser.add_argument(
            "--username", type=str, help="Username for the tgbot user"
        )
        parser.add_argument(
            "--password", type=str, help="Password for the tgbot user"
        )
        parser.add_argument(
            "--token", type=str, help="Token for the tgbot user"
        )

    def handle(self, *args, **options):
        bot_username = options.get("username")
        bot_password = options.get("password")
        bot_token_key = options.get("token")

        if not all([bot_username, bot_password, bot_token_key]):
            raise CommandError(
                "Пожалуйста, установите переменные окружения: "
                "DJANGO_TELEGRAM_BOT_USERNAME, DJANGO_TELEGRAM_BOT_PASSWORD, "
                "и DJANGO_TELEGRAM_BOT_API_TOKEN."
            )

        user, created = User.objects.get_or_create(
            username=bot_username,
            defaults={
                "is_staff": True,
                "is_superuser": False,
            },
        )

        user.set_password(bot_password)
        user.save()

        if created:
            self.stdout.write(f"Пользователь '{bot_username}' успешно создан.")
        else:
            self.stdout.write(
                f"Пользователь '{bot_username}' уже существует. Пароль обновлен."
            )

        _, token_created = Token.objects.update_or_create(
            user=user, defaults={"key": bot_token_key}
        )

        if token_created:
            self.stdout.write(
                f"API токен для пользователя '{bot_username}' успешно создан."
            )
        else:
            self.stdout.write(
                f"API токен для пользователя '{bot_username}' обновлен на значение из .env."
            )

        self.stdout.write("Настройка пользователя-бота завершена.")
