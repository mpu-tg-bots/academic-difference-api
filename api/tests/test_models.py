"""Модульные тесты для моделей и кода админ-панели."""

from django.test import TestCase

from ..admin import AcademicDifferenceAdmin
from ..models import AcademicDifference
from .factories import (
    AcademicDifferenceFactory,
    DepartmentFactory,
    StudentFactory,
    SubjectFactory,
)


class ModelTests(TestCase):
    """Тесты для моделей Django."""

    def test_department_str(self):
        """Тест строкового представления модели Department."""
        department = DepartmentFactory(name="Кафедра высшей математики")
        self.assertEqual(str(department), "Кафедра высшей математики")

    def test_student_str(self):
        """Тест строкового представления модели Student."""
        student = StudentFactory(full_name="Иванов Иван Иванович")
        self.assertEqual(str(student), "Иванов Иван Иванович")

    def test_subject_str(self):
        """Тест строкового представления модели Subject."""
        subject = SubjectFactory(name="Теория принятия решений")
        self.assertEqual(str(subject), "Теория принятия решений")

    def test_academic_difference_methods(self):
        """Тест методов и свойств модели AcademicDifference."""
        diff = AcademicDifferenceFactory()

        # Тестируем свойство @property def department
        self.assertIsNotNone(diff.department)
        self.assertEqual(diff.department, diff.subject.department)

        # Тестируем метод __str__
        expected_str = (
            f"{diff.student.full_name} - {diff.subject.name} "
            f'(до {diff.deadline.strftime("%d.%m.%Y")})'
        )
        self.assertEqual(str(diff), expected_str)


class AdminTests(TestCase):
    """Тесты для кастомного кода в админ-панели."""

    def test_academic_difference_admin_get_department(self):
        """Тест метода get_department в AcademicDifferenceAdmin."""
        admin_instance = AcademicDifferenceAdmin(AcademicDifference, None)
        difference_obj = AcademicDifferenceFactory()

        # Вызываем метод, который используется для отображения колонки
        department_from_admin = admin_instance.get_department_name(
            difference_obj
        )

        self.assertEqual(department_from_admin, difference_obj.department)
