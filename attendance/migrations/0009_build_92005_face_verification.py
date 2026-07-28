from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("attendance", "0008_build_92004_push_notifications")]
    operations = [
        migrations.AddField(model_name="schoolsettings", name="face_verification_enabled", field=models.BooleanField(default=True, verbose_name="Aktifkan pengesahan wajah")),
        migrations.AddField(model_name="schoolsettings", name="face_match_threshold", field=models.PositiveSmallIntegerField(default=62, verbose_name="Ambang padanan visual (%)")),
        migrations.AddField(model_name="schoolsettings", name="require_liveness_challenge", field=models.BooleanField(default=True, verbose_name="Wajib cabaran hidup")),
        migrations.AddField(model_name="teacherprofile", name="reference_photo", field=models.ImageField(blank=True, null=True, upload_to="face_reference/", verbose_name="Foto rujukan wajah")),
        migrations.AddField(model_name="teacherprofile", name="reference_photo_updated_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name="attendance", name="face_in_score", field=models.FloatField(blank=True, null=True)),
        migrations.AddField(model_name="attendance", name="face_out_score", field=models.FloatField(blank=True, null=True)),
        migrations.AddField(model_name="attendance", name="face_in_status", field=models.CharField(blank=True, default="", max_length=20)),
        migrations.AddField(model_name="attendance", name="face_out_status", field=models.CharField(blank=True, default="", max_length=20)),
        migrations.AddField(model_name="attendance", name="liveness_in_challenge", field=models.CharField(blank=True, max_length=120)),
        migrations.AddField(model_name="attendance", name="liveness_out_challenge", field=models.CharField(blank=True, max_length=120)),
        migrations.AddField(model_name="attendance", name="selfie_in_hash", field=models.CharField(blank=True, db_index=True, max_length=64)),
        migrations.AddField(model_name="attendance", name="selfie_out_hash", field=models.CharField(blank=True, db_index=True, max_length=64)),
    ]
