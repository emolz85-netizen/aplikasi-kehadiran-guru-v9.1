from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("attendance", "0005_passwordrecoveryrequest"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(model_name="leaverequest", name="leave_type", field=models.CharField(choices=[("CRK", "Cuti Rehat Khas (CRK)"), ("SAKIT", "Cuti Sakit"), ("TANPA_REKOD", "Cuti Tanpa Rekod"), ("TANPA_GAJI", "Cuti Tanpa Gaji"), ("KECEMASAN", "Cuti Kecemasan"), ("BERSALIN", "Cuti Bersalin"), ("ISTERI_BERSALIN", "Cuti Isteri Bersalin"), ("LAIN", "Lain-lain")], default="CRK", max_length=30)),
        migrations.AddField(model_name="leaverequest", name="attachment", field=models.FileField(blank=True, null=True, upload_to="leave_documents/%Y/%m/")),
        migrations.AddField(model_name="leaverequest", name="admin_note", field=models.TextField(blank=True)),
        migrations.AddField(model_name="leaverequest", name="reviewed_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name="leaverequest", name="reviewed_by", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reviewed_leave_requests", to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name="leaverequest", name="updated_at", field=models.DateTimeField(auto_now=True)),
        migrations.AlterField(model_name="leaverequest", name="status", field=models.CharField(choices=[("MENUNGGU", "Menunggu"), ("DILULUSKAN", "Diluluskan"), ("DITOLAK", "Ditolak"), ("DIBATALKAN", "Dibatalkan")], default="MENUNGGU", max_length=20)),
    ]
