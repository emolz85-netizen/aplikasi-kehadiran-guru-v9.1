from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("attendance", "0003_v911_device_audit"),
    ]

    operations = [
        migrations.AddField(
            model_name="schoolsettings",
            name="address",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.CreateModel(
            name="SchoolHoliday",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200, verbose_name="Nama hari kelepasan")),
                ("date", models.DateField(unique=True, verbose_name="Tarikh")),
                ("description", models.TextField(blank=True, verbose_name="Catatan")),
                ("is_active", models.BooleanField(default=True, verbose_name="Aktif")),
            ],
            options={
                "verbose_name": "Hari kelepasan",
                "verbose_name_plural": "Hari kelepasan",
                "ordering": ["date"],
            },
        ),
    ]
