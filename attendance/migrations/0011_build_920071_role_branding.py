from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("attendance", "0010_build_92006_gps_device_trust")]
    operations = [
        migrations.AddField(model_name="schoolsettings", name="school_code", field=models.CharField(blank=True, default="", max_length=30, verbose_name="Kod sekolah")),
        migrations.AddField(model_name="schoolsettings", name="phone", field=models.CharField(blank=True, default="", max_length=30, verbose_name="Telefon sekolah")),
        migrations.AddField(model_name="schoolsettings", name="email", field=models.EmailField(blank=True, default="", max_length=254, verbose_name="Emel sekolah")),
    ]
