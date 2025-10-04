"""ViewSet'ы для API академических расхождений."""

from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import IsBotOnly
from api.serializers import TelegramStudentCreateSerializer

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
    permission_classes = [IsBotOnly]


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint для кафедр.
    """

    queryset = Department.objects.all().order_by("name")
    serializer_class = DepartmentSerializer
    permission_classes = [IsBotOnly]


class SubjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint для учебных предметов.
    """

    queryset = (
        Subject.objects.select_related("department").all().order_by("name")
    )
    serializer_class = SubjectSerializer
    permission_classes = [IsBotOnly]
    filterset_fields = ["department"]


class AcademicDifferenceViewSet(viewsets.ModelViewSet):
    """
    API endpoint для академических расхождений.
    - Фильтрация: `?is_closed=true`, `?student=<id>`, `?subject=<id>`.
    """

    queryset = AcademicDifference.objects.select_related(
        "student", "subject", "subject__department"
    ).all()
    permission_classes = [IsBotOnly]

    filterset_fields = ["student", "subject", "is_closed"]

    def get_serializer_class(self):
        """Возвращает класс сериализатора в зависимости от действия."""
        if self.action in ["create", "update", "partial_update"]:
            return AcademicDifferenceWriteSerializer
        return AcademicDifferenceReadSerializer


class TelegramStudentCreateView(APIView):
    """
    Ручка для регистрации студента через телеграм-бота.
    """

    def post(self, request):
        serializer = TelegramStudentCreateSerializer(data=request.data)
        if serializer.is_valid():
            student = serializer.save()
            return Response(
                {
                    "id": student.id,
                    "full_name": student.full_name,
                    "telegram_id": student.telegram_id,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
