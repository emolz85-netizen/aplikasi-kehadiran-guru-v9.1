import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from attendance.models import TeacherProfile

class Command(BaseCommand):
    help = "Cipta akaun awal admin dan guru jika belum wujud."

    def handle(self, *args, **kwargs):
        User = get_user_model()

        admin_username = os.getenv("ADMIN_USERNAME", "").strip()
        admin_password = os.getenv("ADMIN_PASSWORD", "").strip()
        admin_email = os.getenv("ADMIN_EMAIL", "").strip()

        if not admin_username or not admin_password:
            raise CommandError("ADMIN_USERNAME dan ADMIN_PASSWORD wajib diisi.")

        admin, created = User.objects.get_or_create(username=admin_username)
        if created:
            admin.email = admin_email
            admin.is_staff = True
            admin.is_superuser = True
            admin.set_password(admin_password)
            admin.save()
            TeacherProfile.objects.get_or_create(user=admin, defaults={"staff_id": "ADMIN001"})
            self.stdout.write(self.style.SUCCESS("Akaun admin berjaya dicipta."))
        else:
            self.stdout.write("Akaun admin sudah wujud.")

        teacher_username = os.getenv("TEACHER_USERNAME", "").strip()
        teacher_password = os.getenv("TEACHER_PASSWORD", "").strip()
        teacher_email = os.getenv("TEACHER_EMAIL", "").strip()

        if teacher_username and teacher_password:
            teacher, created = User.objects.get_or_create(username=teacher_username)
            if created:
                teacher.email = teacher_email
                teacher.set_password(teacher_password)
                teacher.save()
                TeacherProfile.objects.get_or_create(user=teacher, defaults={"staff_id": "GURU001"})
                self.stdout.write(self.style.SUCCESS("Akaun guru berjaya dicipta."))
            else:
                self.stdout.write("Akaun guru sudah wujud.")
