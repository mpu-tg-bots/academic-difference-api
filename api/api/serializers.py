"""Сериализаторы для моделей приложения API."""

from rest_framework import serializers

from .models import AcademicDifference, Department, Student, Subject


class StudentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Student."""

    class Meta:
        """Мета-опции для StudentSerializer."""

        model = Student
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "telegram_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class DepartmentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Department."""

    class Meta:
        """Мета-опции для DepartmentSerializer."""

        model = Department
        fields = ["id", "name", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class SubjectSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Subject."""

    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source="department", write_only=True
    )

    class Meta:
        """Мета-опции для SubjectSerializer."""

        model = Subject
        fields = [
            "id",
            "name",
            "department",
            "department_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class AcademicDifferenceReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения AcademicDifference с вложенными данными."""

    student = StudentSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    department = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        """Мета-опции для AcademicDifferenceReadSerializer."""

        model = AcademicDifference
        fields = [
            "id",
            "student",
            "subject",
            "department",
            "deadline",
            "is_closed",
            "created_at",
            "updated_at",
        ]


class AcademicDifferenceWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления AcademicDifference."""

    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), source="student", write_only=True
    )
    subject_id = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(), source="subject", write_only=True
    )

    class Meta:
        """Мета-опции для AcademicDifferenceWriteSerializer."""

        model = AcademicDifference
        fields = ["id", "student_id", "subject_id", "deadline", "is_closed"]
