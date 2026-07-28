from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("attendance", "0007_build_92003_professional_audit"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="VapidConfiguration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_key", models.TextField()),
                ("private_key_pem", models.TextField()),
                ("subject", models.CharField(default="mailto:admin@skuluansuan.local", max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name": "Konfigurasi VAPID", "verbose_name_plural": "Konfigurasi VAPID"},
        ),
        migrations.CreateModel(
            name="PushSubscription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("endpoint", models.TextField(unique=True)),
                ("p256dh", models.TextField()),
                ("auth", models.TextField()),
                ("user_agent", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="push_subscriptions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "Langganan push", "verbose_name_plural": "Langganan push", "ordering": ["-updated_at"]},
        ),
        migrations.CreateModel(
            name="AppNotification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=160)),
                ("message", models.TextField()),
                ("category", models.CharField(choices=[("KEHADIRAN", "Kehadiran"), ("CUTI", "Cuti"), ("KESELAMATAN", "Keselamatan"), ("SISTEM", "Sistem")], default="SISTEM", max_length=20)),
                ("url", models.CharField(blank=True, default="/", max_length=500)),
                ("is_read", models.BooleanField(db_index=True, default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="app_notifications", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "Notifikasi aplikasi", "verbose_name_plural": "Notifikasi aplikasi", "ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="appnotification",
            index=models.Index(fields=["user", "is_read", "created_at"], name="notif_user_read_idx"),
        ),
    ]
