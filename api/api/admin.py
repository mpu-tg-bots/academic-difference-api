"""Настройки админки на русском"""

from django import forms
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


# ===================== Формы =====================
class UserChangeForm(forms.ModelForm):
    """Форма для изменения пользователя с полем ФИО."""

    full_name = forms.CharField(label="ФИО", required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "full_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["full_name"].initial = (
                f"{self.instance.last_name} {self.instance.first_name} {self.instance.middle_name}"
            )

    def save(self, commit=True):
        user = super().save(commit=False)
        full_name = self.cleaned_data.get("full_name", "")
        parts = full_name.strip().split(maxsplit=2)
        user.last_name = parts[0] if len(parts) > 0 else ""
        user.first_name = parts[1] if len(parts) > 1 else ""
        user.middle_name = parts[2] if len(parts) > 2 else ""
        if commit:
            user.save()
            self.save_m2m()
        return user


# ===================== Inlines =====================
class StudentInline(admin.TabularInline):
    """Inline для отображения студентов в группе."""

    model = Student
    fields = ("full_name", "telegram_id")
    readonly_fields = ("full_name",)

    @admin.display(description="ФИО студента")
    def full_name(self, obj):
        return (
            f"{obj.user.last_name} {obj.user.first_name} {obj.user.middle_name}"
        )


# ===================== Миксин =====================
class AdminMixin(SimpleHistoryAdmin, ImportExportModelAdmin, ExportActionMixin):
    """Миксин для админ-классов с историей и импортом/экспортом."""

    def get_export_formats(self):
        formats = (base_formats.CSV, base_formats.XLS, base_formats.XLSX)
        return [f for f in formats if f().can_export()]

    class Meta:
        abstract = True


# ===================== Пользователь =====================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админ-панель для пользователей."""

    form = UserChangeForm
    search_fields = ("username", "first_name", "last_name", "middle_name")
    fieldsets = (
        ("Учётные данные", {"fields": ("username", "password")}),
        ("Личная информация", {"fields": ("full_name",)}),
        (
            "Разрешения",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )
    list_display = ("username", "full_name_display", "is_staff")
    list_display_links = ("full_name_display",)

    @admin.display(description="ФИО")
    def full_name_display(self, obj):
        return f"{obj.last_name} {obj.first_name} {obj.middle_name}"


# ===================== AcademicGroup =====================
@admin.register(AcademicGroup)
class AcademicGroupAdmin(AdminMixin):
    inlines = (StudentInline,)
    list_display = ("number",)
    list_display_links = ("number",)
    search_fields = ("number",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"


# ===================== Student =====================
class StudentResource(resources.ModelResource):
    user = fields.Field(
        column_name="user",
        attribute="user",
        widget=ForeignKeyWidget(User, "username"),
    )
    group = fields.Field(
        column_name="group",
        attribute="group",
        widget=ForeignKeyWidget(AcademicGroup, "number"),
    )

    class Meta:
        model = Student
        fields = ("user", "group", "telegram_id", "created_at", "updated_at")


@admin.register(Student)
class StudentAdmin(AdminMixin):
    """Админ-панель для студентов."""

    resource_class = StudentResource
    # Убираем raw_id_fields, чтобы появился dropdown
    # raw_id_fields = ("group", "user")

    list_display = ("full_name", "group_number", "telegram_id")
    list_display_links = ("full_name",)
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__username",
        "group__number",
        "telegram_id",
    )
    list_filter = ("group__number",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"

    # Делает поле user dropdown с поиском по ФИО
    autocomplete_fields = ("user", "group")

    @admin.display(description="ФИО студента")
    def full_name(self, obj):
        return (
            f"{obj.user.last_name} {obj.user.first_name} {obj.user.middle_name}"
        )

    @admin.display(description="Номер группы")
    def group_number(self, obj):
        return obj.group.number


# ===================== Department =====================
@admin.register(Department)
class DepartmentAdmin(AdminMixin):
    list_display = ("name",)
    list_display_links = ("name",)
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"


# ===================== Subject =====================
@admin.register(Subject)
class SubjectAdmin(AdminMixin):
    list_display = ("name", "department_name")
    list_display_links = ("name",)
    autocomplete_fields = ("department",)
    search_fields = ("name",)
    list_filter = ("department__name",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"

    @admin.display(description="Факультет")
    def department_name(self, obj):
        return obj.department.name


# ===================== Teacher =====================
@admin.register(Teacher)
class TeacherAdmin(AdminMixin):
    list_display = ("full_name",)
    list_display_links = ("full_name",)
    filter_horizontal = ("subjects",)
    autocomplete_fields = ("user",)
    list_filter = ("subjects__name", "subjects__department__name")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"

    @admin.display(description="ФИО преподавателя")
    def full_name(self, obj):
        return (
            f"{obj.user.last_name} {obj.user.first_name} {obj.user.middle_name}"
        )


# ===================== AcademicDifferenceFile =====================
@admin.register(AcademicDifferenceFile)
class AcademicDifferenceFileAdmin(admin.ModelAdmin):
    list_display = (
        "student_name",
        "state_colored",
        "created_at",
        "download_link",
    )
    list_display_links = ("student_name",)
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

    autocomplete_fields = ("student",)  # <--- dropdown для выбора студента

    @admin.display(description="ФИО студента")
    def student_name(self, obj):
        return f"{obj.student.user.last_name} {obj.student.user.first_name} {obj.student.user.middle_name}"

    @admin.display(description="Статус", ordering="state")
    def state_colored(self, obj):
        color = "orange"
        if obj.state == obj.FileState.PROCESSED:
            color = "green"
        elif obj.state == obj.FileState.ERROR:
            color = "red"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_state_display(),
        )

    @admin.display(description="Ссылка на файл")
    def download_link(self, obj):
        return format_html(
            '<a href="{}" target="_blank">Скачать</a>', obj.file_url
        )
