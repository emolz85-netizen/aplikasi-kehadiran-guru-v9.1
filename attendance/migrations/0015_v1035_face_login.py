from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("attendance", "0014_v1034_stability_radius_media"),
    ]

    operations = [
        migrations.AddField(model_name="schoolsettings", name="face_login_enabled", field=models.BooleanField(default=True, verbose_name="Benarkan Face Login")),
        migrations.AddField(model_name="schoolsettings", name="face_login_threshold", field=models.PositiveSmallIntegerField(default=45, verbose_name="Ambang Face Login (%)")),
        migrations.AddField(model_name="schoolsettings", name="face_login_max_attempts", field=models.PositiveSmallIntegerField(default=5, verbose_name="Percubaan maksimum Face Login")),
        migrations.AddField(model_name="teacherprofile", name="face_login_active", field=models.BooleanField(default=False, verbose_name="Face Login aktif")),
        migrations.AddField(model_name="teacherprofile", name="face_login_activated_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name="teacherprofile", name="face_login_last_used_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name="teacherprofile", name="face_login_failed_attempts", field=models.PositiveSmallIntegerField(default=0)),
        migrations.CreateModel(
            name="FaceLoginAttempt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("attempted_at", models.DateTimeField(auto_now_add=True)),
                ("success", models.BooleanField(default=False)),
                ("score", models.FloatField(blank=True, null=True)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                ("details", models.CharField(blank=True, max_length=255)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="auth.user")),
            ],
            options={"verbose_name": "Percubaan Face Login", "verbose_name_plural": "Percubaan Face Login", "ordering": ["-attempted_at"]},
        ),
    ]
