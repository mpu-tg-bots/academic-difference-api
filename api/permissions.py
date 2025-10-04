from rest_framework import permissions
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class IsBotOnly(permissions.BasePermission):
    """Разрешает запись только телеграм-боту или его группе."""

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        bot_username = getattr(settings, "TG_BOT_USERNAME", "tgbot")

        if user.username == bot_username:
            return True

        if user.groups.filter(name="system_tgbot").exists():
            return True

        return False
