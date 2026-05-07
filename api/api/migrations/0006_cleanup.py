"""Remove unused models; replace StudentNotification.target_students with tg_ids."""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0005_historicalstudentnotification_studentnotification"),
    ]

    operations = [
        # --- Remove all historical (simple_history) tables ---
        migrations.DeleteModel(name="HistoricalAcademicDifference"),
        migrations.DeleteModel(name="HistoricalAcademicDifferenceFile"),
        migrations.DeleteModel(name="HistoricalAcademicGroup"),
        migrations.DeleteModel(name="HistoricalDepartment"),
        migrations.DeleteModel(name="HistoricalStudent"),
        migrations.DeleteModel(name="HistoricalStudentNotification"),
        migrations.DeleteModel(name="HistoricalSubject"),
        migrations.DeleteModel(name="HistoricalTeacher"),
        # --- Detach StudentNotification from Student before deleting Student ---
        migrations.RemoveField(
            model_name="studentnotification",
            name="target_students",
        ),
        # --- Remove models in dependency order (dependents first) ---
        migrations.DeleteModel(name="AcademicDifferenceFile"),
        migrations.DeleteModel(name="AcademicDifference"),
        migrations.RemoveField(model_name="teacher", name="subjects"),
        migrations.DeleteModel(name="Teacher"),
        migrations.DeleteModel(name="Student"),
        migrations.DeleteModel(name="Subject"),
        migrations.DeleteModel(name="Department"),
        migrations.DeleteModel(name="AcademicGroup"),
        # --- Update StudentNotification ---
        migrations.RemoveField(
            model_name="studentnotification",
            name="updated_at",
        ),
        migrations.AddField(
            model_name="studentnotification",
            name="tg_ids",
            field=models.JSONField(
                default=list,
                help_text="Список Telegram ID получателей в формате JSON-массива, например: [123456789, 987654321]",
                verbose_name="Telegram IDs получателей",
            ),
        ),
        migrations.AlterModelOptions(
            name="studentnotification",
            options={
                "verbose_name": "Рассылка",
                "verbose_name_plural": "Рассылки",
            },
        ),
    ]
