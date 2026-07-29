from django.db import migrations, models


def set_face_threshold_35(apps, schema_editor):
    SchoolSettings = apps.get_model("attendance", "SchoolSettings")
    SchoolSettings.objects.all().update(face_match_threshold=35)


def restore_face_threshold_62(apps, schema_editor):
    SchoolSettings = apps.get_model("attendance", "SchoolSettings")
    SchoolSettings.objects.filter(face_match_threshold=35).update(face_match_threshold=62)


class Migration(migrations.Migration):
    dependencies = [("attendance", "0012_v1031_gps_accuracy_fix")]

    operations = [
        migrations.AlterField(
            model_name="schoolsettings",
            name="face_match_threshold",
            field=models.PositiveSmallIntegerField(default=35, verbose_name="Ambang padanan visual (%)"),
        ),
        migrations.RunPython(set_face_threshold_35, restore_face_threshold_62),
    ]
