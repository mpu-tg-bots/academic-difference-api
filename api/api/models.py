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
        if not username:
            raise ValueError("Необходимо указать username")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Суперпользователь должен иметь is_superuser=True."
            )
        return self._create_user(username, password, **extra_fields)


class User(AbstractUser):
    """Модель пользователя без email."""

    middle_name = models.CharField("Отчество", max_length=150, blank=True)
    email = None  # отключаем поле email

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"


class Common(models.Model):
    """Базовая модель с общими полями (created_at, updated_at, history)."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True


class AcademicGroup(Common):
    """Группа университета"""

    number = models.CharField(
        max_length=255, unique=True, verbose_name="Номер группы"
    )

    class Meta:
        verbose_name = "группа"
        verbose_name_plural = "группы"

    def __str__(self):
        return self.number


class Student(Common):
    """Студент"""

    user = models.OneToOneField(
        User, on_delete=models.PROTECT, verbose_name="Пользователь"
    )
    group = models.ForeignKey(
        AcademicGroup, on_delete=models.PROTECT, verbose_name="Группа"
    )
    telegram_id = models.BigIntegerField(
        unique=True, verbose_name="Telegram ID"
    )
    settings = JSONField(
        default=dict, blank=True, verbose_name="Настройки пользователя"
    )

    class Meta:
        verbose_name = "студент"
        verbose_name_plural = "студенты"

    def __str__(self):
        name = f"{self.user.last_name} {self.user.first_name}"
        return f"{name} ({self.group.number})"


class Department(Common):
    """Факультет"""

    name = models.CharField(
        max_length=255, unique=True, verbose_name="Название факультета"
    )

    class Meta:
        verbose_name = "факультет"
        verbose_name_plural = "факультеты"

    def __str__(self):
        return self.name


class Subject(Common):
    """Предмет"""

    name = models.CharField(
        max_length=255, unique=True, verbose_name="Название предмета"
    )
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, verbose_name="Факультет"
    )

    class Meta:
        verbose_name = "предмет"
        verbose_name_plural = "предметы"

    def __str__(self):
        return self.name


class Teacher(Common):
    """Преподаватель"""

    user = models.OneToOneField(
        User, on_delete=models.PROTECT, verbose_name="Пользователь"
    )
    subjects = models.ManyToManyField(
        Subject, verbose_name="Преподаваемые предметы"
    )

    class Meta:
        verbose_name = "преподаватель"
        verbose_name_plural = "преподаватели"

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name}"


class AcademicDifference(Common):
    """Учебное расхождение"""

    student = models.ForeignKey(
        Student, on_delete=models.PROTECT, verbose_name="Студент"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.PROTECT, verbose_name="Предмет"
    )
    deadline = models.DateField(verbose_name="Срок")
    is_closed = models.BooleanField(default=False, verbose_name="Закрыто")

    class Meta:
        verbose_name = "расхождение в учебе"
        verbose_name_plural = "расхождения в учебе"

    def __str__(self):
        return f"{self.student} - {self.subject}"


class AcademicDifferenceFile(Common):
    """Файл с расхождениями"""

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
        max_length=255, unique=True, verbose_name="ID файла Telegram"
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
