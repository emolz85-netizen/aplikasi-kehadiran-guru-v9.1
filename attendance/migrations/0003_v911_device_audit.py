from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("attendance", "0002_v91_schoolsettings_accountactivity_accuracy")]

    operations = [
        migrations.AddField(model_name="attendance", name="check_in_ip", field=models.GenericIPAddressField(blank=True, null=True)),
        migrations.AddField(model_name="attendance", name="check_out_ip", field=models.GenericIPAddressField(blank=True, null=True)),
        migrations.AddField(model_name="attendance", name="check_in_device", field=models.CharField(blank=True, max_length=255)),
        migrations.AddField(model_name="attendance", name="check_out_device", field=models.CharField(blank=True, max_length=255)),
        migrations.AddField(model_name="attendance", name="check_in_user_agent", field=models.TextField(blank=True)),
        migrations.AddField(model_name="attendance", name="check_out_user_agent", field=models.TextField(blank=True)),
    ]
