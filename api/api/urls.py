"""Routes for api views"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AcademicDifferenceFileViewSet,
    AcademicDifferenceViewSet,
    AcademicGroupViewSet,
    DepartmentViewSet,
    StudentViewSet,
    SubjectViewSet,
    TeacherViewSet, proxy_telegram_file,
)

router = DefaultRouter()
router.register(r"students", StudentViewSet)
router.register(r"groups", AcademicGroupViewSet)
router.register(r"departments", DepartmentViewSet)
router.register(r"subjects", SubjectViewSet)
router.register(r"teachers", TeacherViewSet)
router.register(r"academic-differences", AcademicDifferenceViewSet)
router.register(r"academic-difference-file", AcademicDifferenceFileViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path('admin/download-file/<str:file_id>/', proxy_telegram_file, name='admin_download_file'),
]
