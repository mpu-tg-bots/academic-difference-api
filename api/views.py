"""ViewSet'ы для API академических расхождений."""

from rest_framework import permissions, viewsets

from .models import AcademicDifference, Department, Student, Subject
from .serializers import (
    AcademicDifferenceReadSerializer,
    AcademicDifferenceWriteSerializer,
    DepartmentSerializer,
    StudentSerializer,
    SubjectSerializer,
)


class StudentViewSet(viewsets.ModelViewSet):
    """
    API endpoint, позволяющий просматривать и редактировать студентов.
    """

    queryset = Student.objects.all().order_by("full_name")
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint для кафедр.
    """

    queryset = Department.objects.all().order_by("name")
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class SubjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint для учебных предметов.
    """

    queryset = (
        Subject.objects.select_related("department").all().order_by("name")
    )
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["department"]


class AcademicDifferenceViewSet(viewsets.ModelViewSet):
    """
    API endpoint для академических расхождений.
    - Фильтрация: `?is_closed=true`, `?student=<id>`, `?subject=<id>`.
    """

    queryset = AcademicDifference.objects.select_related(
        "student", "subject", "subject__department"
    ).all()
    permission_classes = [permissions.IsAuthenticated]

    filterset_fields = ["student", "subject", "is_closed"]

    def get_serializer_class(self):
        """Возвращает класс сериализатора в зависимости от действия."""
        if self.action in ["create", "update", "partial_update"]:
            return AcademicDifferenceWriteSerializer
        return AcademicDifferenceReadSerializer
