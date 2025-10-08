"""Настройки админ-панели для моделей приложения API."""

from django.contrib import admin

from .models import AcademicDifference, Department, Student, Subject


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Админ-панель для модели Student."""

    list_display = ("full_name", "email", "phone", "telegram_id")
    search_fields = ("full_name", "email", "telegram_id")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Админ-панель для модели Department."""

    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Админ-панель для модели Subject."""

    list_display = ("name", "department")
    search_fields = ("name",)
    list_filter = ("department",)
    autocomplete_fields = ("department",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(AcademicDifference)
class AcademicDifferenceAdmin(admin.ModelAdmin):
    """Админ-панель для модели AcademicDifference."""

    list_display = (
        "student",
        "subject",
        "get_department_name",
        "deadline",
        "is_closed",
    )
    list_filter = ("is_closed", "deadline", "subject__department")
    search_fields = ("student__full_name", "subject__name")
    autocomplete_fields = ("student", "subject")
    list_editable = ("is_closed",)
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Кафедра", ordering="subject__department__name")
    def get_department_name(self, obj):
        """Возвращает название кафедры для отображения в списке."""
        return obj.department
