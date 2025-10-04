"""URL-маршрутизация для приложения API."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import TelegramStudentCreateView

from .views import (
    AcademicDifferenceViewSet,
    DepartmentViewSet,
    StudentViewSet,
    SubjectViewSet,
)

router = DefaultRouter()
router.register(r"students", StudentViewSet)
router.register(r"departments", DepartmentViewSet)
router.register(r"subjects", SubjectViewSet)
router.register(r"academic-differences", AcademicDifferenceViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "telegram/register/",
        TelegramStudentCreateView.as_view(),
        name="telegram-register",
    ),
]
