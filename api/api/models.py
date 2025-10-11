"""Academic difference models file"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models import JSONField

from simple_history.models import HistoricalRecords


class CustomUserManager(BaseUserManager):
    """
    Кастомный менеджер для модели User, где не используется email.
    """

    def _create_user(self, username, password, **extra_fields):
        """
        Создает и сохраняет пользователя с данным username и паролем.
        Это основная функция, которую нужно переопределить.
        """
        if not username:
            raise ValueError("The given username must be set")

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password=None, **extra_fields):
        """
        Создает и сохраняет суперпользователя.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, password, **extra_fields)


class User(AbstractUser):
    email = None
    middle_name = models.CharField("middle name", blank=True)

    USERNAME_FIELD = "username"

    objects = CustomUserManager()

    def __str__(self):
        return self.username


class Common(models.Model):
    """Common model for common fields"""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords(inherit=True)

    class Meta:
        """Common model Meta class."""

        abstract = True


class AcademicGroup(Common):
    """University Academic Group model"""

    number = models.CharField(
        max_length=255, unique=True, verbose_name="Academic Group Number"
    )

    class Meta:
        """Academic Group Meta class."""

        verbose_name = "academic group"
        verbose_name_plural = "academic groups"

    def __str__(self):
        return f"{self.number}"


class Student(Common):
    """University Student model"""

    user = models.OneToOneField(
        User, on_delete=models.PROTECT, verbose_name="Related user"
    )

    group = models.ForeignKey(
        AcademicGroup, on_delete=models.PROTECT, verbose_name="Related group"
    )

    telegram_id = models.BigIntegerField(
        unique=True, verbose_name="Telegram ID"
    )

    settings = JSONField(default=dict, blank=True, verbose_name="User Settings")

    class Meta:
        """Student Meta class."""

        verbose_name = "student"
        verbose_name_plural = "students"

    def __str__(self):
        return (
            f"{self.user.last_name} {self.user.first_name} {self.group.number}"
        )


class Department(Common):
    """University Department model"""

    name = models.CharField(
        max_length=255, unique=True, verbose_name="Department Name"
    )

    class Meta:
        """Department Meta class."""

        verbose_name = "department"
        verbose_name_plural = "departments"

    def __str__(self):
        return self.name


class Subject(Common):
    """University Subject model"""

    name = models.CharField(
        max_length=255, unique=True, verbose_name="Subject Name"
    )

    department = models.ForeignKey(Department, on_delete=models.PROTECT)

    class Meta:
        """Department Meta class."""

        verbose_name = "subject"
        verbose_name_plural = "subjects"

    def __str__(self):
        return self.name


class Teacher(Common):
    """University Teacher model"""

    user = models.OneToOneField(User, on_delete=models.PROTECT)

    subjects = models.ManyToManyField(
        Subject, verbose_name="Teacher To Subject"
    )

    class Meta:
        """Teacher Meta class."""

        verbose_name = "teacher"
        verbose_name_plural = "teachers"

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name}"


class AcademicDifference(Common):
    """Academic Difference model"""

    student = models.ForeignKey(Student, on_delete=models.PROTECT)

    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)

    deadline = models.DateField()

    is_closed = models.BooleanField(default=False)

    class Meta:
        """Academic Difference Meta class."""

        verbose_name = "academic difference"
        verbose_name_plural = "academic differences"


class AcademicDifferenceFile(Common):
    """
    Хранит информацию о файле с расхождениями, присланном и обработанном ботом.
    """

    class FileState(models.TextChoices):
        PENDING = "PENDING", "Ожидает обработки"
        PROCESSED = "PROCESSED", "Обработан"
        ERROR = "ERROR", "Ошибка обработки"

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="difference_files",
        verbose_name="Студент",
    )

    file_id = models.CharField(
        max_length=255, unique=True, verbose_name="Telegram File ID"
    )

    file_url = models.URLField(max_length=1024, verbose_name="Ссылка на файл")

    state = models.CharField(
        max_length=20,
        choices=FileState.choices,
        default=FileState.PENDING,
        db_index=True,
        verbose_name="Статус",
    )

    class Meta:
        verbose_name = "файл с расхождениями"
        verbose_name_plural = "файлы с расхождениями"
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Файл от {self.student.user.username} ({self.get_state_display()})"
        )
