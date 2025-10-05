"""
Модели Django для API академических расхождений.

Содержит модели для Студента, Кафедры, Предмета и самого Расхождения
в учебном плане.
"""

from django.conf import settings
from django.db import models


class Student(models.Model):
    """Модель, представляющая студента."""

    full_name = models.CharField(
        "ФИО студента",
        max_length=255,
    )
    email = models.EmailField(
        "Email",
    )
    phone = models.CharField(
        "Телефон",
        max_length=20,
    )
    telegram_id = models.BigIntegerField(
        "Telegram User ID",
        unique=True,
        help_text=(
            "Уникальный идентификатор пользователя из Telegram-бота. "
            "Заполняется автоматически."
        ),
    )

    created_at = models.DateTimeField("Дата создания записи", auto_now_add=True)
    updated_at = models.DateTimeField(
        "Дата последнего обновления", auto_now=True
    )

    class Meta:
        """Мета-опции для модели Студента."""

        verbose_name = "Студент"
        verbose_name_plural = "Студенты"
        ordering = ["full_name"]

    def __str__(self):
        """Строковое представление объекта студента."""
        return self.full_name

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student",
        null=True,
        blank=True,
    )


class Department(models.Model):
    """Модель, представляющая кафедру."""

    name = models.CharField(
        "Название кафедры",
        max_length=255,
        unique=True,
    )

    created_at = models.DateTimeField("Дата создания записи", auto_now_add=True)
    updated_at = models.DateTimeField(
        "Дата последнего обновления", auto_now=True
    )

    class Meta:
        """Мета-опции для модели Кафедры."""

        verbose_name = "Кафедра"
        verbose_name_plural = "Кафедры"
        ordering = ["name"]

    def __str__(self):
        """Строковое представление объекта кафедры."""
        return self.name


class Subject(models.Model):
    """Модель, представляющая учебный предмет (дисциплину)."""

    name = models.CharField(
        "Название предмета",
        max_length=255,
        unique=True,
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        verbose_name="Кафедра",
    )

    created_at = models.DateTimeField("Дата создания записи", auto_now_add=True)
    updated_at = models.DateTimeField(
        "Дата последнего обновления", auto_now=True
    )

    class Meta:
        """Мета-опции для модели Предмета."""

        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"
        ordering = ["name"]

    def __str__(self):
        """Строковое представление объекта предмета."""
        return self.name


class AcademicDifference(models.Model):
    """Основная модель, фиксирующая расхождение в учебном плане (РУП)."""

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        verbose_name="Студент",
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        verbose_name="Предмет",
    )

    deadline = models.DateField(
        "Срок сдачи",
    )

    is_closed = models.BooleanField(
        "Ликвидировано",
        default=False,
        help_text="Отметьте, если расхождение устранено",
    )

    created_at = models.DateTimeField("Дата создания записи", auto_now_add=True)
    updated_at = models.DateTimeField(
        "Дата последнего обновления", auto_now=True
    )

    @property
    def department(self):
        """Возвращает кафедру, к которой привязан предмет."""
        return self.subject.department

    class Meta:
        """Мета-опции для модели Расхождения."""

        verbose_name = "Расхождение в учебном плане (РУП)"
        verbose_name_plural = "Расхождения в учебных планах (РУП)"
        ordering = ["-deadline", "student"]

    def __str__(self):
        """Строковое представление расхождения в учебном плане."""
        return (
            f"{self.student.full_name} - {self.subject.name} "
            f'(до {self.deadline.strftime("%d.%m.%Y")})'
        )
