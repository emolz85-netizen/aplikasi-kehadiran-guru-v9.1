from django.db import migrations, models


def assign_roles(apps, schema_editor):
    TeacherProfile = apps.get_model("attendance", "TeacherProfile")
    for profile in TeacherProfile.objects.select_related("user").all():
        user = profile.user
        position = (profile.position or "").lower()
        if user.is_superuser:
            role = "SUPER_ADMIN"
        elif user.is_staff:
            role = "ADMIN"
        elif "guru besar" in position or "headmaster" in position:
            role = "GURU_BESAR"
        elif "gpk" in position or "penolong kanan" in position:
            role = "GPK"
        elif "kerani" in position or "pembantu tadbir" in position or "setiausaha" in position:
            role = "KERANI"
        else:
            role = "GURU"
        profile.role = role
        profile.save(update_fields=["role"])


class Migration(migrations.Migration):
    dependencies = [("attendance", "0016_v1036_official_report_settings")]
    operations = [
        migrations.AddField(
            model_name="teacherprofile",
            name="role",
            field=models.CharField(choices=[("GURU", "Guru"), ("GURU_BESAR", "Guru Besar"), ("GPK", "Guru Penolong Kanan"), ("KERANI", "Setiausaha / Kerani"), ("ADMIN", "Administrator"), ("SUPER_ADMIN", "Super Admin")], db_index=True, default="GURU", max_length=20, verbose_name="Peranan sistem"),
        ),
        migrations.RunPython(assign_roles, migrations.RunPython.noop),
    ]
