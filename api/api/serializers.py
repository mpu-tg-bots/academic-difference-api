"""Сериализаторы для REST API"""

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import (
    AcademicDifference,
    AcademicDifferenceFile,
    AcademicGroup,
    Department,
    Student,
    Subject,
    Teacher,
)


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для User.
    Умеет создавать пользователя с хэшированием пароля.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "middle_name",
            "is_staff",
            "password",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class AcademicGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicGroup
        fields = "__all__"


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class StudentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для Student.
    При `GET` запросе показывает полную информацию о `user` и `group`.
    При `POST`/`PUT` запросе принимает `user_id` и `group_id`.
    """

    user = UserSerializer(read_only=True)
    group = AcademicGroupSerializer(read_only=True)

    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="user", write_only=True
    )
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicGroup.objects.all(), source="group", write_only=True
    )

    class Meta:
        model = Student
        fields = [
            "id",
            "user",
            "group",
            "user_id",
            "group_id",
            "telegram_id",
            "settings",
        ]

    def validate_settings(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Settings must be a valid JSON object (dict)."
            )

        if "notifications" not in value:
            raise serializers.ValidationError(
                "'notifications' field is required in settings."
            )

        if not isinstance(value.get("notifications"), bool):
            raise serializers.ValidationError(
                "'notifications' must be a boolean (true/false)."
            )

        return value


class TeacherSerializer(serializers.ModelSerializer):
    """
    Сериализатор для Teacher.
    При `GET` показывает полную информацию о `user` и `subjects`.
    При `POST`/`PUT` принимает `user_id` и список `subject_ids`.
    """

    user = UserSerializer(read_only=True)

    subjects = SubjectSerializer(many=True, read_only=True)

    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="user", write_only=True
    )

    subject_ids = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        source="subjects",
        many=True,
        write_only=True,
    )

    class Meta:
        model = Teacher
        fields = ["id", "user", "subjects", "user_id", "subject_ids"]


class AcademicDifferenceSerializer(serializers.ModelSerializer):
    """
    Сериализатор для AcademicDifference.
    При `GET` показывает детали студента и предмета.
    При `POST`/`PUT` принимает `student_id` и `subject_id`.
    """

    student = StudentSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)

    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), source="student", write_only=True
    )
    subject_id = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(), source="subject", write_only=True
    )

    class Meta:
        model = AcademicDifference
        fields = [
            "id",
            "student",
            "subject",
            "student_id",
            "subject_id",
            "deadline",
            "is_closed",
        ]


class AcademicDifferenceFileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели AcademicDifferenceFile.
    Позволяет создавать, обновлять и отображать записи.
    """

    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), source="student", write_only=True
    )

    student = serializers.StringRelatedField(read_only=True)

    safe_download_url = serializers.SerializerMethodField()

    class Meta:
        model = AcademicDifferenceFile
        fields = [
            "id",
            "student",
            "student_id",
            "file_id",
            "safe_download_url",
            "state",
            "created_at",
        ]

        read_only_fields = ("student", "created_at")

    def get_safe_download_url(self, obj):

        return f"{settings.BOT_API_BASE_URL}/files/{obj.file_id}/"


class RegisterStudentSerializer(serializers.Serializer):
    """
    Сериализатор для приема данных при полной регистрации нового студента
    с файлом расхождений.
    """

    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    middle_name = serializers.CharField(
        max_length=150, required=False, allow_blank=True, default=""
    )

    telegram_id = serializers.IntegerField()
    group_number = serializers.CharField(max_length=255)

    file_id = serializers.CharField(max_length=255)

    def validate_telegram_id(self, value):
        """
        Проверяем, что студент с таким telegram_id еще не зарегистрирован.
        """
        if Student.objects.filter(telegram_id=value).exists():
            raise serializers.ValidationError(
                f"Студент с Telegram ID {value} уже существует."
            )
        return value
