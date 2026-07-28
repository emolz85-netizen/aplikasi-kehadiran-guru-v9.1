from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="TeacherProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("staff_id", models.CharField(blank=True, max_length=30)),
                ("position", models.CharField(blank=True, max_length=100)),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="LeaveRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("reason", models.TextField()),
                ("status", models.CharField(choices=[("MENUNGGU", "Menunggu"), ("DILULUSKAN", "Diluluskan"), ("DITOLAK", "Ditolak")], default="MENUNGGU", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="OfficialDuty",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("location", models.CharField(max_length=200)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("description", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("MENUNGGU", "Menunggu"), ("DILULUSKAN", "Diluluskan"), ("DITOLAK", "Ditolak")], default="MENUNGGU", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Attendance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("check_in", models.DateTimeField(blank=True, null=True)),
                ("check_out", models.DateTimeField(blank=True, null=True)),
                ("check_in_lat", models.FloatField(blank=True, null=True)),
                ("check_in_lng", models.FloatField(blank=True, null=True)),
                ("check_out_lat", models.FloatField(blank=True, null=True)),
                ("check_out_lng", models.FloatField(blank=True, null=True)),
                ("distance_in_m", models.FloatField(blank=True, null=True)),
                ("distance_out_m", models.FloatField(blank=True, null=True)),
                ("selfie_in", models.ImageField(blank=True, null=True, upload_to="selfies/")),
                ("selfie_out", models.ImageField(blank=True, null=True, upload_to="selfies/")),
                ("status", models.CharField(choices=[("HADIR", "Hadir"), ("LEWAT", "Lewat")], default="HADIR", max_length=10)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-date"], "unique_together": {("user", "date")}},
        ),
    ]
