"""URL-маршрутизация для приложения API."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

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
]
