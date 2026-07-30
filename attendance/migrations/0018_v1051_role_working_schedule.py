from datetime import time
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("attendance", "0017_v104_role_based_dashboard")]
    operations = [
        migrations.AddField(
            model_name="schoolsettings",
            name="office_check_in",
            field=models.TimeField(default=time(8, 0), verbose_name="Waktu masuk Guru Besar / Kerani"),
        ),
        migrations.AddField(
            model_name="schoolsettings",
            name="office_check_out",
            field=models.TimeField(default=time(16, 0), verbose_name="Waktu keluar Guru Besar / Kerani"),
        ),
    ]
