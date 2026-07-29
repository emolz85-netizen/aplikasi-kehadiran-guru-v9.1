from django.db import migrations, models


def set_official_school_details(apps, schema_editor):
    SchoolSettings = apps.get_model("attendance", "SchoolSettings")
    obj, _ = SchoolSettings.objects.get_or_create(pk=1)
    obj.school_name = "SK Ulu Ansuan"
    obj.school_code = "XBA2247"
    obj.address = "Peti Surat 08, 89320 Telupid, Sabah"
    obj.save(update_fields=["school_name", "school_code", "address"])


class Migration(migrations.Migration):
    dependencies = [("attendance", "0015_v1035_face_login")]
    operations = [
        migrations.AddField(
            model_name="schoolsettings",
            name="report_signatory_name",
            field=models.CharField(blank=True, default="", max_length=150, verbose_name="Nama pentadbir laporan"),
        ),
        migrations.AddField(
            model_name="schoolsettings",
            name="report_signatory_position",
            field=models.CharField(blank=True, default="", max_length=150, verbose_name="Jawatan pentadbir laporan"),
        ),
        migrations.RunPython(set_official_school_details, migrations.RunPython.noop),
    ]
