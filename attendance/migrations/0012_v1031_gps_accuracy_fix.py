from django.db import migrations, models


def raise_gps_accuracy_limit(apps, schema_editor):
    SchoolSettings = apps.get_model("attendance", "SchoolSettings")
    SchoolSettings.objects.filter(max_gps_accuracy_meters__lt=100).update(max_gps_accuracy_meters=100)


class Migration(migrations.Migration):
    dependencies = [("attendance", "0011_build_920071_role_branding")]
    operations = [
        migrations.AlterField(
            model_name="schoolsettings",
            name="max_gps_accuracy_meters",
            field=models.PositiveIntegerField(default=100),
        ),
        migrations.RunPython(raise_gps_accuracy_limit, migrations.RunPython.noop),
    ]
