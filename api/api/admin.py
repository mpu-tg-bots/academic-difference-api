"""Admin panel settings"""

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

import requests

from .models import StudentNotification, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка для кастомной модели User."""

    search_fields = ("username", "first_name", "last_name", "middle_name")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("ФИО", {"fields": ("first_name", "middle_name", "last_name")}),
        (
            "Права",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )

    list_display = (
        "username",
        "first_name",
        "middle_name",
        "last_name",
        "is_staff",
    )


@admin.register(StudentNotification)
class StudentNotificationAdmin(admin.ModelAdmin):
    """Админка для управления рассылками в Telegram."""

    list_display = (
        "id",
        "short_text",
        "recipient_count",
        "status",
        "created_at",
    )
    list_display_links = ("id", "short_text")
    list_filter = ("status", "created_at")
    readonly_fields = ("created_at",)

    fields = ("text", "tg_ids", "status", "created_at")

    @admin.display(description="Текст")
    def short_text(self, obj: StudentNotification):
        return obj.text[:60] + "..." if len(obj.text) > 60 else obj.text

    @admin.display(description="Получателей")
    def recipient_count(self, obj: StudentNotification):
        ids = obj.tg_ids if isinstance(obj.tg_ids, list) else []
        return len(ids)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if obj.status != "sent":
            return

        tg_ids = obj.tg_ids if isinstance(obj.tg_ids, list) else []

        if not tg_ids:
            self.message_user(
                request,
                "Список Telegram ID пуст — рассылка не отправлена.",
                level=messages.WARNING,
            )
            obj.status = "draft"
            obj.save(update_fields=["status"])
            return

        bot_url = f"{settings.BOT_API_BASE_URL}/notify:batchCreate"
        payload = {"tg_ids": tg_ids, "message": obj.text}

        try:
            response = requests.post(bot_url, json=payload, timeout=30)
            if response.status_code == 200:
                self.message_user(
                    request,
                    f"Рассылка передана боту для {len(tg_ids)} получателей.",
                    level=messages.SUCCESS,
                )
            else:
                self.message_user(
                    request,
                    f"Ошибка на стороне бота: HTTP {response.status_code}.",
                    level=messages.ERROR,
                )
        except requests.exceptions.RequestException:
            self.message_user(
                request,
                "Бот недоступен. Проверьте BOT_API_BASE_URL"
                " и состояние контейнера.",
                level=messages.ERROR,
            )
