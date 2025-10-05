"""Это команда, которая позволяет создавать пользователя
для телеграмм бота автоматически при деплое проекта"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    """Create system user for Telegram bot"""

    def add_arguments(self, parser):
        parser.add_argument(
            "--username", type=str, default=settings.TG_BOT_USERNAME
        )
        parser.add_argument("--email", type=str, default=settings.TG_BOT_EMAIL)
        parser.add_argument(
            "--password", type=str, default=settings.TG_BOT_PASSWORD
        )
        parser.add_argument(
            "--permission",
            action="store_true",
            dest="give_permissions",
            default=settings.TG_BOT_GIVE_PERMS,
        )
        parser.add_argument(
            "--target-apps", type=str, default=settings.TG_BOT_TARGET_APPS
        )

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        password = options["password"]
        give_perms = options["give_permissions"]
        target_apps_raw = options["target_apps"] or ""
        target_apps = [
            a.strip() for a in target_apps_raw.split(",") if a.strip()
        ]

        if not password:
            self.stdout.write(
                self.style.ERROR(
                    "Username, email, and password must be provided."
                )
            )
            return

        with transaction.atomic():
            user, created = User.objects.get_or_create(
                username=username, defaults={"email": email}
            )

            if created:
                user.set_password(password)
                user.is_staff = False
                user.is_superuser = False
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f"Created user {username}")
                )
            else:
                updated = False
                if user.email != email:
                    user.email = email
                    updated = True
                user.set_password(password)
                updated = True
                if updated:
                    user.save()
                    self.stdout.write(
                        self.style.SUCCESS(f"Updated user {username}")
                    )

            if give_perms:
                group, _ = Group.objects.get_or_create(name="system_tgbot")
                if target_apps:
                    perms = Permission.objects.filter(
                        content_type__app_label__in=target_apps
                    )
                else:
                    perms = Permission.objects.all()
                group.permissions.set(perms)
                group.user_set.add(user)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Assigned {perms.count()} permissions to group"
                    )
                )
