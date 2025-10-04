"""Интеграционные тесты для API эндпоинтов."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Student
from .factories import (
    AcademicDifferenceFactory,
    DepartmentFactory,
    StudentFactory,
    SubjectFactory,
    UserFactory,
)

User = get_user_model()


class StudentAPITests(APITestCase):
    """Тесты для API эндпоинта /students/"""

    def setUp(self):
        self.user, _ = User.objects.get_or_create(
            username=settings.TG_BOT_USERNAME,
            defaults={"email": "bot@example.com", "password": "test123"},
        )
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse("student-list")

    def test_list_students(self):
        """GET /students/ -> 200 OK"""
        StudentFactory.create_batch(3)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 3)

    def test_create_student(self):
        """POST /students/ -> 201 Created"""
        payload = {
            "full_name": "Новый Студент",
            "email": "new@student.com",
            "phone": "12345",
            "telegram_id": 123456789,
        }
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Student.objects.filter(telegram_id=123456789).exists())


class SubjectAPITests(APITestCase):
    """Тесты для API эндпоинта /subjects/"""

    def setUp(self):
        self.user, _ = User.objects.get_or_create(
            username=settings.TG_BOT_USERNAME,
            defaults={"email": "bot@example.com", "password": "test123"},
        )
        self.client.force_authenticate(user=self.user)
        self.department = DepartmentFactory()
        self.list_url = reverse("subject-list")

    def test_create_subject(self):
        """POST /subjects/ -> 201 Created"""
        payload = {"name": "Новый Предмет", "department_id": self.department.id}
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Новый Предмет")


class AcademicDifferenceAPITests(APITestCase):
    """Тесты для API эндпоинта /academic-differences/"""

    def setUp(self):
        self.user, _ = User.objects.get_or_create(
            username=settings.TG_BOT_USERNAME,
            defaults={"email": "bot@example.com", "password": "test123"},
        )
        self.client.force_authenticate(user=self.user)

        self.difference = AcademicDifferenceFactory()
        self.list_url = reverse("academicdifference-list")
        self.detail_url = reverse(
            "academicdifference-detail", kwargs={"pk": self.difference.pk}
        )

    def test_list_differences(self):
        """GET /academic-differences/ -> 200 OK (использует ReadSerializer)"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 1)
        self.assertEqual(
            response.data["results"][0]["student"]["id"],
            self.difference.student.id,
        )

    def test_create_difference(self):
        """POST /academic-differences/ -> 201 Created (использует WriteSerializer)"""
        student = StudentFactory()
        subject = SubjectFactory()
        payload = {
            "student_id": student.id,
            "subject_id": subject.id,
            "deadline": "2025-01-01",
        }
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_difference(self):
        """PUT /academic-differences/{id}/ -> 200 OK (использует WriteSerializer)"""
        student = StudentFactory()
        subject = SubjectFactory()
        payload = {
            "student_id": student.id,
            "subject_id": subject.id,
            "deadline": "2026-02-02",
            "is_closed": True,
        }
        response = self.client.put(self.detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.difference.refresh_from_db()
        self.assertTrue(self.difference.is_closed)
        self.assertEqual(self.difference.student, student)

    def test_partial_update_difference(self):
        """PATCH /academic-differences/{id}/ -> 200 OK (использует WriteSerializer)"""
        payload = {"is_closed": True}
        response = self.client.patch(self.detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.difference.refresh_from_db()
        self.assertTrue(self.difference.is_closed)
