"""Фабрики для создания тестовых данных (factory-boy)."""

from django.contrib.auth import get_user_model

import factory
from factory.django import DjangoModelFactory

from ..models import AcademicDifference, Department, Student, Subject

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Фабрика для модели User."""

    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = factory.Faker("user_name")
    email = factory.Faker("email")


class DepartmentFactory(DjangoModelFactory):
    """Фабрика для модели Department."""

    class Meta:
        model = Department
        django_get_or_create = ("name",)

    name = factory.Faker("bs")


class StudentFactory(DjangoModelFactory):
    """Фабрика для модели Student."""

    class Meta:
        model = Student
        django_get_or_create = ("telegram_id",)

    full_name = factory.Faker("name", locale="ru_RU")
    email = factory.Faker("email")
    phone = factory.Faker("phone_number", locale="ru_RU")
    telegram_id = factory.Sequence(lambda n: 100000000 + n)


class SubjectFactory(DjangoModelFactory):
    """Фабрика для модели Subject."""

    class Meta:
        model = Subject
        django_get_or_create = ("name",)

    name = factory.Faker("catch_phrase", locale="ru_RU")
    department = factory.SubFactory(DepartmentFactory)


class AcademicDifferenceFactory(DjangoModelFactory):
    """Фабрика для модели AcademicDifference."""

    class Meta:
        model = AcademicDifference

    student = factory.SubFactory(StudentFactory)
    subject = factory.SubFactory(SubjectFactory)
    deadline = factory.Faker("future_date")
    is_closed = False
