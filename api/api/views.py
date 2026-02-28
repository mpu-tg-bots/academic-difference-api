"""Views для REST API"""

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import Http404, HttpResponseServerError, StreamingHttpResponse
from django.utils.crypto import get_random_string
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

import requests
from django_filters import rest_framework as filters

from api.models import (
    AcademicDifference,
    AcademicDifferenceFile,
    AcademicGroup,
    Department,
    Student,
    Subject,
    Teacher,
)
from api.serializers import (
    AcademicDifferenceFileSerializer,
    AcademicDifferenceSerializer,
    AcademicGroupSerializer,
    DepartmentSerializer,
    RegisterStudentSerializer,
    StudentSerializer,
    SubjectSerializer,
    TeacherSerializer,
    UserSerializer,
)

User = get_user_model()


class UserFilter(filters.FilterSet):
    """Фильтры для модели User."""

    class Meta:
        model = User
        fields = {
            "username": ["exact", "icontains"],
            "first_name": ["exact", "icontains"],
            "last_name": ["exact", "icontains"],
            "middle_name": ["exact", "icontains"],
            "is_staff": ["exact"],
        }


class AcademicGroupFilter(filters.FilterSet):
    """Фильтры для модели AcademicGroup."""

    class Meta:
        model = AcademicGroup
        fields = {
            "number": ["exact", "icontains"],
        }


class StudentFilter(filters.FilterSet):
    """Фильтры для модели Student."""

    class Meta:
        model = Student
        fields = {
            "user__username": ["exact", "icontains"],
            "user__last_name": ["exact", "icontains"],
            "group__number": ["exact", "icontains"],
            "telegram_id": ["exact"],
        }


class DepartmentFilter(filters.FilterSet):
    """Фильтры для модели Department."""

    class Meta:
        model = Department
        fields = {
            "name": ["exact", "icontains"],
        }


class SubjectFilter(filters.FilterSet):
    """Фильтры для модели Subject."""

    class Meta:
        model = Subject
        fields = {
            "name": ["exact", "icontains"],
            "department__name": ["exact", "icontains"],
        }


class TeacherFilter(filters.FilterSet):
    """Фильтры для модели Teacher."""

    class Meta:
        model = Teacher
        fields = {
            "user__username": ["exact", "icontains"],
            "user__last_name": ["exact", "icontains"],
            "subjects__name": [
                "exact",
                "icontains",
            ],
        }


class AcademicDifferenceFilter(filters.FilterSet):
    """Фильтры для модели AcademicDifference."""

    class Meta:
        model = AcademicDifference
        fields = {
            "student__user__username": ["exact", "icontains"],
            "student__user__last_name": ["exact", "icontains"],
            "subject__name": ["exact", "icontains"],
            "deadline": [
                "exact",
                "gte",
                "lte",
                "gt",
                "lt",
            ],
            "is_closed": ["exact"],
        }


class AcademicDifferenceFileFilter(filters.FilterSet):
    """
    Фильтр для модели AcademicDifferenceFile.
    Позволяет фильтровать по id студента, статусу и дате создания.
    """

    created_at = filters.DateFromToRangeFilter()

    class Meta:
        model = AcademicDifferenceFile
        fields = {
            "student__id": ["exact"],
            "state": ["exact", "in"],
        }


class UserViewSet(viewsets.ModelViewSet):
    """API для создания, редактирования и просмотра Пользователей."""

    queryset = User.objects.all().order_by("username")
    serializer_class = UserSerializer
    filterset_class = UserFilter
    search_fields = ["username", "first_name", "last_name", "middle_name"]
    ordering_fields = ["username", "last_name", "first_name"]


class AcademicGroupViewSet(viewsets.ModelViewSet):
    """API для Академических Групп."""

    queryset = AcademicGroup.objects.all().order_by("number")
    serializer_class = AcademicGroupSerializer
    filterset_class = AcademicGroupFilter
    search_fields = ["number"]
    ordering_fields = ["number"]


class StudentViewSet(viewsets.ModelViewSet):
    """API для Студентов."""

    queryset = Student.objects.select_related("user", "group").order_by(
        "user__last_name"
    )
    serializer_class = StudentSerializer
    filterset_class = StudentFilter
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "group__number",
    ]
    ordering_fields = ["user__last_name", "user__first_name", "group__number"]

    def get_serializer_class(self):
        """Используем разные сериализаторы для разных действий."""
        if self.action == "register":
            return RegisterStudentSerializer
        return StudentSerializer

    @action(detail=False, methods=["post"], url_path="register")
    @transaction.atomic
    def register(self, request, *args, **kwargs):
        Serializer = self.get_serializer_class()
        serializer = Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        group, _ = AcademicGroup.objects.get_or_create(
            number=validated_data["group_number"],
            defaults={"number": validated_data["group_number"]},
        )

        user = User.objects.create_user(
            username="tguser-" + str(validated_data["telegram_id"]),
            password=get_random_string(10),
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            middle_name=validated_data.get("middle_name", ""),
        )

        student = Student.objects.create(
            user=user, group=group, telegram_id=validated_data["telegram_id"]
        )

        output_serializer = StudentSerializer(student)

        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class DepartmentViewSet(viewsets.ModelViewSet):
    """API для Кафедр."""

    queryset = Department.objects.all().order_by("name")
    serializer_class = DepartmentSerializer
    filterset_class = DepartmentFilter
    search_fields = ["name"]
    ordering_fields = ["name"]


class SubjectViewSet(viewsets.ModelViewSet):
    """API для Предметов."""

    queryset = Subject.objects.select_related("department").order_by("name")
    serializer_class = SubjectSerializer
    filterset_class = SubjectFilter
    search_fields = ["name", "department__name"]
    ordering_fields = ["name", "department__name"]


class TeacherViewSet(viewsets.ModelViewSet):
    """API для Преподавателей."""

    queryset = (
        Teacher.objects.select_related("user")
        .prefetch_related("subjects")
        .order_by("user__last_name")
    )
    serializer_class = TeacherSerializer
    filterset_class = TeacherFilter
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "subjects__name",
    ]
    ordering_fields = ["user__last_name", "user__first_name"]


class AcademicDifferenceViewSet(viewsets.ModelViewSet):
    """API для Академических Задолженностей."""

    queryset = AcademicDifference.objects.select_related(
        "student__user", "subject"
    ).order_by("-deadline")
    serializer_class = AcademicDifferenceSerializer
    filterset_class = AcademicDifferenceFilter
    search_fields = [
        "student__user__username",
        "student__user__last_name",
        "subject__name",
    ]
    ordering_fields = [
        "deadline",
        "student__user__last_name",
        "subject__name",
        "is_closed",
    ]


@staff_member_required
def proxy_telegram_file(request, file_id):
    nodejs_url = f"{settings.BOT_API_BASE_URL}/files/{file_id}/"

    try:
        response = requests.get(nodejs_url, stream=True, timeout=30)

        if response.status_code == 404:
            raise Http404("Файл не найден в Telegram")

        response.raise_for_status()

        proxy_response = StreamingHttpResponse(
            response.iter_content(chunk_size=8192),
            content_type=response.headers.get(
                "Content-Type", "application/octet-stream"
            ),
        )

        if "Content-Disposition" in response.headers:
            proxy_response["Content-Disposition"] = response.headers[
                "Content-Disposition"
            ]

        return proxy_response

    except requests.exceptions.RequestException as e:
        return HttpResponseServerError(f"Ошибка при загрузке файла: {str(e)}")


class AcademicDifferenceFileViewSet(viewsets.ModelViewSet):
    """
    API эндпоинт для управления файлами с расхождениями.
    Предоставляет полный CRUD-функционал.
    """

    queryset = AcademicDifferenceFile.objects.select_related(
        "student__user"
    ).all()

    serializer_class = AcademicDifferenceFileSerializer

    filterset_class = AcademicDifferenceFileFilter

    search_fields = [
        "student__user__username",
        "student__user__last_name",
        "file_id",
    ]

    ordering_fields = ["created_at", "state", "student__user__last_name"]
