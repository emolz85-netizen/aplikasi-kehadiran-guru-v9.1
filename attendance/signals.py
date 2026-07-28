from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .audit import write_audit


@receiver(user_logged_in)
def audit_login(sender, request, user, **kwargs):
    write_audit(request=request, user=user, category="AUTH", action="Log masuk berjaya", description="Pengguna berjaya memasuki sistem.", status_code=200)


@receiver(user_logged_out)
def audit_logout(sender, request, user, **kwargs):
    if user:
        write_audit(request=request, user=user, category="AUTH", action="Log keluar", description="Pengguna keluar daripada sistem.", status_code=200)


@receiver(user_login_failed)
def audit_login_failed(sender, credentials, request, **kwargs):
    username = credentials.get("username", "Tidak diketahui")
    write_audit(request=request, category="AUTH", severity="AMARAN", action="Percubaan log masuk gagal", description=f"Nama pengguna: {username}", status_code=401)
