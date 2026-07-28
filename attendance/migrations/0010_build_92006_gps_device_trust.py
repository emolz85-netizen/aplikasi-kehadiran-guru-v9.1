from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [("attendance", "0009_build_92005_face_verification"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.AddField(model_name="schoolsettings", name="device_trust_enabled", field=models.BooleanField(default=True, verbose_name="Aktifkan peranti dipercayai")),
        migrations.AddField(model_name="schoolsettings", name="auto_trust_first_device", field=models.BooleanField(default=True, verbose_name="Percayai peranti pertama secara automatik")),
        migrations.AddField(model_name="schoolsettings", name="block_untrusted_device", field=models.BooleanField(default=False, verbose_name="Sekat peranti belum diluluskan")),
        migrations.AddField(model_name="schoolsettings", name="max_location_age_seconds", field=models.PositiveIntegerField(default=60, verbose_name="Umur maksimum bacaan GPS (saat)")),
        migrations.AddField(model_name="schoolsettings", name="max_plausible_speed_kmh", field=models.PositiveIntegerField(default=180, verbose_name="Kelajuan maksimum munasabah (km/j)")),
        migrations.AddField(model_name="schoolsettings", name="high_risk_block_threshold", field=models.PositiveSmallIntegerField(default=80, verbose_name="Ambang sekatan skor risiko")),
        migrations.AddField(model_name="attendance", name="check_in_device_id", field=models.CharField(blank=True, db_index=True, max_length=64)),
        migrations.AddField(model_name="attendance", name="check_out_device_id", field=models.CharField(blank=True, db_index=True, max_length=64)),
        migrations.AddField(model_name="attendance", name="check_in_risk_score", field=models.PositiveSmallIntegerField(default=0)),
        migrations.AddField(model_name="attendance", name="check_out_risk_score", field=models.PositiveSmallIntegerField(default=0)),
        migrations.AddField(model_name="attendance", name="check_in_risk_level", field=models.CharField(blank=True, default="RENDAH", max_length=20)),
        migrations.AddField(model_name="attendance", name="check_out_risk_level", field=models.CharField(blank=True, default="RENDAH", max_length=20)),
        migrations.AddField(model_name="attendance", name="check_in_security_flags", field=models.JSONField(blank=True, default=list)),
        migrations.AddField(model_name="attendance", name="check_out_security_flags", field=models.JSONField(blank=True, default=list)),
        migrations.CreateModel(name="TrustedDevice", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("device_id", models.CharField(db_index=True, max_length=64)), ("device_name", models.CharField(blank=True, max_length=160)),
            ("platform", models.CharField(blank=True, max_length=100)), ("browser", models.CharField(blank=True, max_length=100)),
            ("user_agent", models.TextField(blank=True)), ("status", models.CharField(choices=[("DIPERCAYAI","Dipercayai"),("MENUNGGU","Menunggu kelulusan"),("DISEKAT","Disekat")], default="MENUNGGU", max_length=20)),
            ("first_ip", models.GenericIPAddressField(blank=True, null=True)), ("last_ip", models.GenericIPAddressField(blank=True, null=True)),
            ("first_seen_at", models.DateTimeField(auto_now_add=True)), ("last_seen_at", models.DateTimeField(auto_now=True)),
            ("notes", models.CharField(blank=True, max_length=255)),
            ("approved_at", models.DateTimeField(blank=True, null=True)),
            ("approved_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="approved_trusted_devices", to=settings.AUTH_USER_MODEL)),
            ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="trusted_devices", to=settings.AUTH_USER_MODEL)),
        ], options={"ordering":["-last_seen_at"],"verbose_name":"Peranti dipercayai","verbose_name_plural":"Peranti dipercayai","unique_together":{("user","device_id")}}),
        migrations.AddIndex(model_name="trusteddevice", index=models.Index(fields=["user","status"], name="device_user_status_idx")),
        migrations.CreateModel(name="LocationSecurityEvent", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("event_type", models.CharField(choices=[("GPS","Integriti GPS"),("PERANTI","Peranti"),("KELAJUAN","Kelajuan"),("RISIKO","Skor risiko")], default="GPS", max_length=20)),
            ("action", models.CharField(blank=True, max_length=20)), ("risk_score", models.PositiveSmallIntegerField(default=0)),
            ("risk_level", models.CharField(default="RENDAH", max_length=20)), ("flags", models.JSONField(blank=True, default=list)),
            ("latitude", models.FloatField(blank=True, null=True)), ("longitude", models.FloatField(blank=True, null=True)), ("accuracy", models.FloatField(blank=True, null=True)),
            ("device_id", models.CharField(blank=True, max_length=64)), ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
            ("blocked", models.BooleanField(default=False)), ("details", models.TextField(blank=True)), ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
            ("attendance", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="security_events", to="attendance.attendance")),
            ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="location_security_events", to=settings.AUTH_USER_MODEL)),
        ], options={"ordering":["-created_at"],"verbose_name":"Peristiwa keselamatan lokasi","verbose_name_plural":"Peristiwa keselamatan lokasi"}),
        migrations.AddIndex(model_name="locationsecurityevent", index=models.Index(fields=["risk_level","created_at"], name="locsec_risk_date_idx")),
    ]
