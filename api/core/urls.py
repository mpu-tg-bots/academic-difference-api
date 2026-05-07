"""Основной файл URL-маршрутизации проекта."""

from django.contrib import admin
from django.urls import path

from .views import health_check

urlpatterns = [
    path("health/", health_check, name="health_check"),
    path("admin/", admin.site.urls),
]
