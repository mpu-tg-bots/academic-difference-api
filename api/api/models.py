"""Academic difference models file"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """Кастомный менеджер для модели User без поля email."""

    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError("The given username must be set")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, password, **extra_fields)


class User(AbstractUser):
    """Кастомная модель пользователя с отчеством."""

    email = None
    middle_name = models.CharField("Отчество", blank=True)

    USERNAME_FIELD = "username"

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"


class StudentNotification(models.Model):
    """Модель рассылки сообщений в Telegram."""

    text = models.TextField(verbose_name="Текст сообщения")

    tg_ids = models.JSONField(
        default=list,
        verbose_name="Telegram IDs получателей",
        help_text=(
            "Список Telegram ID получателей в формате"
            " JSON-массива, например: [123456789, 987654321]"
        ),
    )

    status = models.CharField(
        max_length=20,
        choices=[("draft", "Черновик"), ("sent", "Отправлено")],
        default="draft",
        verbose_name="Статус",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def __str__(self):
        time = self.created_at.strftime("%d.%m.%Y %H:%M")
        return f"Рассылка от {time} — {self.get_status_display()}"
