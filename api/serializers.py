"""Сериализаторы для моделей приложения API."""

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import AcademicDifference, Department, Student, Subject

User = get_user_model()


class TelegramStudentCreateSerializer(serializers.Serializer):
    """Сериализатор для бота."""

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(max_length=255)
    telegram_id = serializers.IntegerField()

    def validate_telegram_id(self, value):
        if Student.objects.filter(telegram_id=value).exists():
            raise serializers.ValidationError(
                "Telegram ID уже зарегистрирован"
            )
        return value

    def create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(
                username=validated_data["username"],
                email=validated_data["email"],
                password=validated_data["password"],
                is_staff=False,
                is_superuser=False,
            )

            student = Student.objects.create(
                user=user,
                full_name=validated_data["full_name"],
                email=validated_data["email"],
                telegram_id=validated_data["telegram_id"],
            )

        return student


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
    department = serializers.CharField(
        source="department.name", read_only=True
    )

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
