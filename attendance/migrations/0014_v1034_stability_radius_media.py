from django.db import migrations, models


def apply_stability_settings(apps, schema_editor):
    SchoolSettings = apps.get_model('attendance', 'SchoolSettings')
    SchoolSettings.objects.all().update(radius_meters=150)

    # Salin media sedia ada ke pangkalan data apabila fail masih tersedia.
    for school in SchoolSettings.objects.all():
        if school.logo and not school.logo_bytes:
            try:
                with school.logo.open('rb') as fh:
                    school.logo_bytes = fh.read()
                school.logo_mime_type = 'image/png' if str(school.logo.name).lower().endswith('.png') else 'image/jpeg'
                school.save(update_fields=['logo_bytes', 'logo_mime_type'])
            except Exception:
                pass

    TeacherProfile = apps.get_model('attendance', 'TeacherProfile')
    for profile in TeacherProfile.objects.all():
        if profile.reference_photo and not profile.reference_photo_bytes:
            try:
                with profile.reference_photo.open('rb') as fh:
                    profile.reference_photo_bytes = fh.read()
                profile.reference_photo_mime_type = 'image/png' if str(profile.reference_photo.name).lower().endswith('.png') else 'image/jpeg'
                profile.save(update_fields=['reference_photo_bytes', 'reference_photo_mime_type'])
            except Exception:
                pass


def reverse_radius(apps, schema_editor):
    SchoolSettings = apps.get_model('attendance', 'SchoolSettings')
    SchoolSettings.objects.filter(radius_meters=150).update(radius_meters=50)


class Migration(migrations.Migration):
    dependencies = [('attendance', '0013_v1033_face_threshold_35')]
    operations = [
        migrations.AlterField(
            model_name='schoolsettings',
            name='radius_meters',
            field=models.PositiveIntegerField(default=150, verbose_name='Radius geofence (meter)'),
        ),
        migrations.AddField(model_name='schoolsettings', name='logo_bytes', field=models.BinaryField(blank=True, editable=False, null=True)),
        migrations.AddField(model_name='schoolsettings', name='logo_mime_type', field=models.CharField(blank=True, default='image/jpeg', editable=False, max_length=100)),
        migrations.AddField(model_name='teacherprofile', name='reference_photo_bytes', field=models.BinaryField(blank=True, editable=False, null=True)),
        migrations.AddField(model_name='teacherprofile', name='reference_photo_mime_type', field=models.CharField(blank=True, default='image/jpeg', editable=False, max_length=100)),
        migrations.RunPython(apply_stability_settings, reverse_radius),
    ]
