"""Custom permissions для API."""

import logging

from django.conf import settings
from rest_framework import permissions

logger = logging.getLogger(__name__)


class IsBotOrAdminOnly(permissions.BasePermission):
    """Чтение для всех, запись только админам и телеграм-боту."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_staff or user.is_superuser:
            return True

        bot_username = getattr(settings, "TG_BOT_USERNAME", "tgbot")
        if user.username == bot_username:
            return True
        if user.groups.filter(name="system_tgbot").exists():
            return True

        return False
