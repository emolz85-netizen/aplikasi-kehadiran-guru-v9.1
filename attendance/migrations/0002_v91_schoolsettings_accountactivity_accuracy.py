from datetime import time
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("attendance", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="SchoolSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("school_name", models.CharField(default="SK Ulu Ansuan", max_length=200)),
                ("latitude", models.FloatField(default=5.745697)),
                ("longitude", models.FloatField(default=117.173844)),
                ("radius_meters", models.PositiveIntegerField(default=50)),
                ("max_gps_accuracy_meters", models.PositiveIntegerField(default=50)),
                ("weekday_check_in", models.TimeField(default=time(7, 10))),
                ("weekday_check_out", models.TimeField(default=time(13, 0))),
                ("friday_check_in", models.TimeField(default=time(7, 10))),
                ("friday_check_out", models.TimeField(default=time(11, 40))),
                ("logo", models.ImageField(blank=True, null=True, upload_to="school/")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name": "Tetapan sekolah", "verbose_name_plural": "Tetapan sekolah"},
        ),
        migrations.CreateModel(
            name="AccountActivity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(max_length=100)),
                ("details", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="auth.user")),
            ],
            options={"verbose_name": "Aktiviti akaun", "verbose_name_plural": "Aktiviti akaun", "ordering": ["-created_at"]},
        ),
        migrations.AddField(model_name="attendance", name="check_in_accuracy", field=models.FloatField(blank=True, null=True)),
        migrations.AddField(model_name="attendance", name="check_out_accuracy", field=models.FloatField(blank=True, null=True)),
    ]
