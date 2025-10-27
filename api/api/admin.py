"""Admin panel settings"""

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from import_export import fields, resources
from import_export.admin import ExportActionMixin, ImportExportModelAdmin
from import_export.formats import base_formats
from import_export.widgets import ForeignKeyWidget
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    AcademicDifference,
    AcademicDifferenceFile,
    AcademicGroup,
    Department,
    Student,
    Subject,
    Teacher,
    User,
)

settings.configure()


class StudentInline(admin.TabularInline):
    """Inline admin field for student model"""

    model = Student


class AdminMixin(SimpleHistoryAdmin, ImportExportModelAdmin, ExportActionMixin):
    """Admin panel common settings."""

    def get_export_formats(self):
        formats = (
            base_formats.CSV,
            base_formats.XLS,
            base_formats.XLSX,
        )

        return [f for f in formats if f().can_export()]

    class Meta:
        """Admin panel common settings meta."""

        abstract = True


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Класс админки для кастомной модели User.
    Наследуемся от BaseUserAdmin, чтобы получить все стандартные фичи.
    """

    search_fields = ("username", "first_name", "last_name", "middle_name")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "middle_name", "last_name")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    list_display = (
        "username",
        "first_name",
        "middle_name",
        "last_name",
        "is_staff",
    )


@admin.register(AcademicGroup)
class AcademicGroupAdmin(AdminMixin):
    """Admin panel for AcademicGroup model"""

    inlines = (StudentInline,)

    list_display = ("number",)
    search_fields = ("number",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"


class StudentResource(resources.ModelResource):
    """StudentResource for exporting Student model"""

    # pylint: disable=invalid-name
    User = fields.Field(
        column_name="user",
        attribute="user",
        widget=ForeignKeyWidget(User, "username"),
    )

    # pylint: disable=invalid-name
    Group = fields.Field(
        column_name="group",
        attribute="group",
        widget=ForeignKeyWidget(AcademicGroup, "number"),
    )

    class Meta:
        """Meta options for StudentResource"""

        model = Student
        fields = (
            "id",
            "User",
            "Group",
            "telegram_id",
            "settings",
            "created_at",
            "updated_at",
        )


@admin.register(Student)
class StudentAdmin(AdminMixin):
    """Admin panel for Student model"""

    resource_class = StudentResource

    raw_id_fields = ("group",)

    list_display = ("user", "group__number", "telegram_id")
    autocomplete_fields = ("user", "group")
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__username",
        "user__email",
        "group__number",
        "telegram_id",
    )
    list_filter = ("group__number",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"


@admin.register(Department)
class DepartmentAdmin(AdminMixin):
    """Admin panel for Department model"""

    list_display = ("name",)
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"


@admin.register(Subject)
class SubjectAdmin(AdminMixin):
    """Admin panel for Subject model"""

    list_display = ("name", "department")
    autocomplete_fields = ("department",)
    search_fields = ("name",)
    list_filter = ("department__name",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"


@admin.register(Teacher)
class TeacherAdmin(AdminMixin):
    """Admin panel for Teacher model"""

    list_display = ("user",)
    filter_horizontal = ("subjects",)
    autocomplete_fields = ("user",)
    list_filter = ("subjects__name", "subjects__department__name")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"


@admin.register(AcademicDifference)
class AcademicDifferenceAdmin(AdminMixin):
    """Admin panel for AcademicDifference model"""

    def get_export_queryset(self, request):
        return AcademicDifference.objects.filter(is_closed=False)

    list_display = (
        "student",
        "subject",
        "view_department",
        "deadline",
        "is_closed",
    )
    list_display_links = ("student",)
    list_filter = (
        "is_closed",
        "deadline",
        "subject__department__name",
    )
    search_fields = (
        "student__user__first_name",
        "student__user__last_name",
        "student__user__username",
        "student__user__email",
        "student__group__number",
        "subject__name",
    )
    autocomplete_fields = ("student", "subject")
    list_editable = ("is_closed",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "deadline"

    @admin.display()
    def view_department(self, obj):
        return obj.subject.department

    view_department.short_description = "Department"


@admin.register(AcademicDifferenceFile)
class AcademicDifferenceFileAdmin(admin.ModelAdmin):
    """
    Интерфейс администрирования для модели файлов с расхождениями.
    """

    list_display = (
        "id",
        "student",
        "state_colored",
        "created_at",
        "download_link",
    )

    list_filter = ("state", "created_at", "student__group__number")

    search_fields = (
        "student__user__username",
        "student__user__last_name",
        "file_id",
    )

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Основная информация", {"fields": ("student", "file_id", "file_url")}),
        ("Статус обработки", {"fields": ("state",)}),
        ("Даты", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Статус", ordering="state")
    def state_colored(self, obj: AcademicDifferenceFile):
        """Отображает статус в виде цветной метки."""
        if obj.state == obj.FileState.PROCESSED:
            color = "green"
        elif obj.state == obj.FileState.ERROR:
            color = "red"
        else:
            color = "orange"

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_state_display(),
        )

    @admin.display(description="Ссылка на файл")
    def download_link(self, obj: AcademicDifferenceFile):
        """Отображает кликабельную ссылку на файл."""

        safe_url = f"{settings.BOT_API_BASE_URL}/files/{obj.file_id}/"
        return format_html(
            '<a href="{}" target="_blank">Скачать</a>',
            safe_url,
        )
