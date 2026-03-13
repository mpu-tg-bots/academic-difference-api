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
    middle_name = models.CharField("Отчество", blank=True)

    USERNAME_FIELD = "username"

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"


class Common(models.Model):
    """Common model for common fields"""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")
    history = HistoricalRecords(inherit=True)

    class Meta:
        """Common model Meta class."""

        abstract = True


class AcademicGroup(Common):
    """University Academic Group model"""

    number = models.CharField(
        max_length=255, unique=True, verbose_name="Номер группы"
    )

    class Meta:
        """Academic Group Meta class."""

        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return f"{self.number}"


class Student(Common):
    """University Student model"""

    user = models.OneToOneField(
        User, on_delete=models.PROTECT, verbose_name="Связанный пользователь"
    )

    group = models.ForeignKey(
        AcademicGroup, on_delete=models.PROTECT, verbose_name="Связанная группа"
    )

    telegram_id = models.BigIntegerField(
        unique=True, verbose_name="Telegram ID"
    )

    settings = JSONField(default=dict, blank=True, verbose_name="Настройки")

    class Meta:
        """Student Meta class."""

        verbose_name = "Студент"
        verbose_name_plural = "Студенты"

    def __str__(self):
        return (
            f"{self.user.last_name} {self.user.first_name} {self.group.number}"
        )


class Department(Common):
    """University Department model"""

    name = models.CharField(
        max_length=255, unique=True, verbose_name="Название"
    )

    class Meta:
        """Department Meta class."""

        verbose_name = "Кафедра"
        verbose_name_plural = "Кафедры"

    def __str__(self):
        return self.name


class Subject(Common):
    """University Subject model"""

    name = models.CharField(
        max_length=255, unique=True, verbose_name="Название"
    )

    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, verbose_name="Кафедра"
    )

    class Meta:
        """Department Meta class."""

        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"

    def __str__(self):
        return self.name


class Teacher(Common):
    """University Teacher model"""

    user = models.OneToOneField(
        User, on_delete=models.PROTECT, verbose_name="Пользователь"
    )

    subjects = models.ManyToManyField(
        Subject, verbose_name="Предмет преподавателя"
    )

    class Meta:
        """Teacher Meta class."""

        verbose_name = "Преподаватель"
        verbose_name_plural = "Преподаватели"

    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name}"


class AcademicDifference(Common):
    """Academic Difference model"""

    student = models.ForeignKey(
        Student, on_delete=models.PROTECT, verbose_name="Студент"
    )

    subject = models.ForeignKey(
        Subject, on_delete=models.PROTECT, verbose_name="Предмет"
    )

    deadline = models.DateField(verbose_name="Дедлайн")

    is_closed = models.BooleanField(default=False, verbose_name="Сдано")

    class Meta:
        """Academic Difference Meta class."""

        verbose_name = "РУП"
        verbose_name_plural = "РУПы"


class AcademicDifferenceFile(Common):
    """
    Хранит информацию о файле с расхождениями, присланном и обработанном ботом.
    """

    class FileState(models.TextChoices):
        APPROVED = "APPROVED", "Подтверждён"
        NOT_ACCEPTED = (
            "NOT_ACCEPTED",
            "Не принят",
        )
        REVIEW = "REVIEW", "Рассмотрение"

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="difference_files",
        verbose_name="Студент",
    )

    name = models.CharField(
        max_length=255, verbose_name="Название файла", default="Не указано"
    )

    file_id = models.CharField(
        max_length=255, unique=True, verbose_name="Telegram File ID"
    )

    file_url = models.URLField(max_length=1024, verbose_name="Ссылка на файл")

    state = models.CharField(
        max_length=20,
        choices=FileState.choices,
        default=FileState.REVIEW,
        db_index=True,
        verbose_name="Статус",
    )

    class Meta:
        verbose_name = "Файл с РУП"
        verbose_name_plural = "Файлы с РУПами"
        ordering = ["-created_at"]

    def __str__(self):
        u = self.student.user.username
        n = self.name
        s = self.get_state_display()
        return f"Файл от {u} {n} ({s})"


class StudentNotification(Common):
    """
    Student telegram notifications
    """

    text = models.TextField(verbose_name="Текст сообщения")

    target_students = models.ManyToManyField(
        Student, blank=True, verbose_name="Или выбрать конкретных студентов"
    )

    status = models.CharField(
        max_length=20,
        choices=[("draft", "Черновик"), ("sent", "Отправлено")],
        default="draft",
        verbose_name="Статус",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ручная рассылка"
        verbose_name_plural = "Ручные рассылки"

    def __str__(self):
        time = self.created_at.strftime("%d.%m.%Y")
        return f"Рассылка от {time} - {self.status}"
