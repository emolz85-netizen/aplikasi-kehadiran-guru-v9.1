from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("attendance", "0006_build_92000_leave_management"),
    ]

    operations = [
        migrations.CreateModel(
            name="SystemAuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("username_snapshot", models.CharField(blank=True, max_length=150)),
                ("category", models.CharField(choices=[("AUTH", "Log masuk & keselamatan"), ("KEHADIRAN", "Kehadiran"), ("CUTI", "Cuti"), ("TUGAS", "Tugas rasmi"), ("LAPORAN", "Laporan"), ("PENTADBIRAN", "Pentadbiran"), ("SISTEM", "Sistem")], default="SISTEM", max_length=20)),
                ("severity", models.CharField(choices=[("INFO", "Maklumat"), ("AMARAN", "Amaran"), ("KRITIKAL", "Kritikal")], default="INFO", max_length=10)),
                ("action", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True)),
                ("method", models.CharField(blank=True, max_length=10)),
                ("path", models.CharField(blank=True, max_length=500)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("device", models.CharField(blank=True, max_length=255)),
                ("user_agent", models.TextField(blank=True)),
                ("status_code", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("object_type", models.CharField(blank=True, max_length=100)),
                ("object_id", models.CharField(blank=True, max_length=100)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="system_audit_logs", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "Log audit sistem", "verbose_name_plural": "Log audit sistem", "ordering": ["-created_at"]},
        ),
        migrations.AddIndex(model_name="systemauditlog", index=models.Index(fields=["category", "created_at"], name="audit_category_date_idx")),
        migrations.AddIndex(model_name="systemauditlog", index=models.Index(fields=["user", "created_at"], name="audit_user_date_idx")),
        migrations.AddIndex(model_name="systemauditlog", index=models.Index(fields=["severity", "created_at"], name="audit_severity_date_idx")),
    ]
