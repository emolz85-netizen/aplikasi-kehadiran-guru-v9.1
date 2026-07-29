from datetime import time
from django.db import models
from django.contrib.auth.models import User


class SchoolSettings(models.Model):
    school_name = models.CharField(max_length=200, default="SK Ulu Ansuan")
    school_code = models.CharField(max_length=30, blank=True, default="", verbose_name="Kod sekolah")
    address = models.TextField(blank=True, default="")
    phone = models.CharField(max_length=30, blank=True, default="", verbose_name="Telefon sekolah")
    email = models.EmailField(blank=True, default="", verbose_name="Emel sekolah")
    latitude = models.FloatField(default=5.745697)
    longitude = models.FloatField(default=117.173844)
    radius_meters = models.PositiveIntegerField(default=50)
    max_gps_accuracy_meters = models.PositiveIntegerField(default=100)
    weekday_check_in = models.TimeField(default=time(7, 10))
    weekday_check_out = models.TimeField(default=time(13, 0))
    friday_check_in = models.TimeField(default=time(7, 10))
    friday_check_out = models.TimeField(default=time(11, 40))
    face_verification_enabled = models.BooleanField(default=True, verbose_name="Aktifkan pengesahan wajah")
    face_match_threshold = models.PositiveSmallIntegerField(default=62, verbose_name="Ambang padanan visual (%)")
    require_liveness_challenge = models.BooleanField(default=True, verbose_name="Wajib cabaran hidup")
    device_trust_enabled = models.BooleanField(default=True, verbose_name="Aktifkan peranti dipercayai")
    auto_trust_first_device = models.BooleanField(default=True, verbose_name="Percayai peranti pertama secara automatik")
    block_untrusted_device = models.BooleanField(default=False, verbose_name="Sekat peranti belum diluluskan")
    max_location_age_seconds = models.PositiveIntegerField(default=60, verbose_name="Umur maksimum bacaan GPS (saat)")
    max_plausible_speed_kmh = models.PositiveIntegerField(default=180, verbose_name="Kelajuan maksimum munasabah (km/j)")
    high_risk_block_threshold = models.PositiveSmallIntegerField(default=80, verbose_name="Ambang sekatan skor risiko")
    logo = models.ImageField(upload_to="school/", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tetapan sekolah"
        verbose_name_plural = "Tetapan sekolah"

    def __str__(self):
        return self.school_name

    def save(self, *args, **kwargs):
        if not self.pk and SchoolSettings.objects.exists():
            self.pk = SchoolSettings.objects.first().pk
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def times_for_date(self, date_value):
        if date_value.weekday() == 4:
            return self.friday_check_in, self.friday_check_out
        return self.weekday_check_in, self.weekday_check_out


class SchoolHoliday(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nama hari kelepasan")
    date = models.DateField(unique=True, verbose_name="Tarikh")
    description = models.TextField(blank=True, verbose_name="Catatan")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    class Meta:
        ordering = ["date"]
        verbose_name = "Hari kelepasan"
        verbose_name_plural = "Hari kelepasan"

    def __str__(self):
        return f"{self.name} ({self.date:%d/%m/%Y})"


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    staff_id = models.CharField(max_length=30, blank=True)
    position = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    reference_photo = models.ImageField(upload_to="face_reference/", null=True, blank=True, verbose_name="Foto rujukan wajah")
    reference_photo_updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class AccountActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    details = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Aktiviti akaun"
        verbose_name_plural = "Aktiviti akaun"

    def __str__(self):
        return f"{self.user} - {self.action}"


class Attendance(models.Model):
    STATUS_CHOICES = [("HADIR", "Hadir"), ("LEWAT", "Lewat")]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    check_in_lat = models.FloatField(null=True, blank=True)
    check_in_lng = models.FloatField(null=True, blank=True)
    check_in_accuracy = models.FloatField(null=True, blank=True)
    check_out_lat = models.FloatField(null=True, blank=True)
    check_out_lng = models.FloatField(null=True, blank=True)
    check_out_accuracy = models.FloatField(null=True, blank=True)
    distance_in_m = models.FloatField(null=True, blank=True)
    distance_out_m = models.FloatField(null=True, blank=True)
    selfie_in = models.ImageField(upload_to="selfies/", null=True, blank=True)
    selfie_out = models.ImageField(upload_to="selfies/", null=True, blank=True)
    check_in_ip = models.GenericIPAddressField(null=True, blank=True)
    check_out_ip = models.GenericIPAddressField(null=True, blank=True)
    check_in_device = models.CharField(max_length=255, blank=True)
    check_out_device = models.CharField(max_length=255, blank=True)
    check_in_user_agent = models.TextField(blank=True)
    check_out_user_agent = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="HADIR")
    face_in_score = models.FloatField(null=True, blank=True)
    face_out_score = models.FloatField(null=True, blank=True)
    face_in_status = models.CharField(max_length=20, blank=True, default="")
    face_out_status = models.CharField(max_length=20, blank=True, default="")
    liveness_in_challenge = models.CharField(max_length=120, blank=True)
    liveness_out_challenge = models.CharField(max_length=120, blank=True)
    selfie_in_hash = models.CharField(max_length=64, blank=True, db_index=True)
    selfie_out_hash = models.CharField(max_length=64, blank=True, db_index=True)
    check_in_device_id = models.CharField(max_length=64, blank=True, db_index=True)
    check_out_device_id = models.CharField(max_length=64, blank=True, db_index=True)
    check_in_risk_score = models.PositiveSmallIntegerField(default=0)
    check_out_risk_score = models.PositiveSmallIntegerField(default=0)
    check_in_risk_level = models.CharField(max_length=20, blank=True, default="RENDAH")
    check_out_risk_level = models.CharField(max_length=20, blank=True, default="RENDAH")
    check_in_security_flags = models.JSONField(default=list, blank=True)
    check_out_security_flags = models.JSONField(default=list, blank=True)

    class Meta:
        unique_together = ("user", "date")
        ordering = ["-date"]


class LeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ("CRK", "Cuti Rehat Khas (CRK)"),
        ("SAKIT", "Cuti Sakit"),
        ("TANPA_REKOD", "Cuti Tanpa Rekod"),
        ("TANPA_GAJI", "Cuti Tanpa Gaji"),
        ("KECEMASAN", "Cuti Kecemasan"),
        ("BERSALIN", "Cuti Bersalin"),
        ("ISTERI_BERSALIN", "Cuti Isteri Bersalin"),
        ("LAIN", "Lain-lain"),
    ]
    STATUS_CHOICES = [
        ("MENUNGGU", "Menunggu"),
        ("DILULUSKAN", "Diluluskan"),
        ("DITOLAK", "Ditolak"),
        ("DIBATALKAN", "Dibatalkan"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=30, choices=LEAVE_TYPE_CHOICES, default="CRK")
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    attachment = models.FileField(upload_to="leave_documents/%Y/%m/", null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="MENUNGGU")
    admin_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="reviewed_leave_requests")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.get_leave_type_display()} ({self.start_date} hingga {self.end_date})"

    @property
    def total_days(self):
        return (self.end_date - self.start_date).days + 1


class OfficialDuty(models.Model):
    STATUS_CHOICES = [("MENUNGGU", "Menunggu"), ("DILULUSKAN", "Diluluskan"), ("DITOLAK", "Ditolak")]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="MENUNGGU")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class PasswordRecoveryRequest(models.Model):
    STATUS_CHOICES = [("MENUNGGU", "Menunggu"), ("DILULUSKAN", "Diluluskan"), ("SELESAI", "Selesai"), ("DITOLAK", "Ditolak")]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_recovery_requests")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="MENUNGGU")
    code_hash = models.CharField(max_length=128, blank=True)
    code_display = models.CharField(max_length=6, blank=True, help_text="Dipaparkan kepada admin sahaja")
    expires_at = models.DateTimeField(null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="approved_password_recoveries")
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-requested_at"]
        verbose_name = "Permintaan pemulihan kata laluan"
        verbose_name_plural = "Permintaan pemulihan kata laluan"

    def __str__(self):
        return f"{self.user.username} - {self.get_status_display()}"

class SystemAuditLog(models.Model):
    CATEGORY_CHOICES = [
        ("AUTH", "Log masuk & keselamatan"),
        ("KEHADIRAN", "Kehadiran"),
        ("CUTI", "Cuti"),
        ("TUGAS", "Tugas rasmi"),
        ("LAPORAN", "Laporan"),
        ("PENTADBIRAN", "Pentadbiran"),
        ("SISTEM", "Sistem"),
    ]
    SEVERITY_CHOICES = [
        ("INFO", "Maklumat"),
        ("AMARAN", "Amaran"),
        ("KRITIKAL", "Kritikal"),
    ]

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="system_audit_logs")
    username_snapshot = models.CharField(max_length=150, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="SISTEM")
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default="INFO")
    action = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    method = models.CharField(max_length=10, blank=True)
    path = models.CharField(max_length=500, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device = models.CharField(max_length=255, blank=True)
    user_agent = models.TextField(blank=True)
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)
    object_type = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category", "created_at"], name="audit_category_date_idx"),
            models.Index(fields=["user", "created_at"], name="audit_user_date_idx"),
            models.Index(fields=["severity", "created_at"], name="audit_severity_date_idx"),
        ]
        verbose_name = "Log audit sistem"
        verbose_name_plural = "Log audit sistem"

    def __str__(self):
        return f"{self.created_at:%d/%m/%Y %H:%M} - {self.username_snapshot or 'Sistem'} - {self.action}"

class PushSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="push_subscriptions")
    endpoint = models.TextField(unique=True)
    p256dh = models.TextField()
    auth = models.TextField()
    user_agent = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Langganan push"
        verbose_name_plural = "Langganan push"

    def __str__(self):
        return f"{self.user} - {self.endpoint[:45]}"


class AppNotification(models.Model):
    CATEGORY_CHOICES = [
        ("KEHADIRAN", "Kehadiran"),
        ("CUTI", "Cuti"),
        ("KESELAMATAN", "Keselamatan"),
        ("SISTEM", "Sistem"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="app_notifications")
    title = models.CharField(max_length=160)
    message = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="SISTEM")
    url = models.CharField(max_length=500, blank=True, default="/")
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "is_read", "created_at"], name="notif_user_read_idx")]
        verbose_name = "Notifikasi aplikasi"
        verbose_name_plural = "Notifikasi aplikasi"

    def __str__(self):
        return f"{self.user} - {self.title}"


class VapidConfiguration(models.Model):
    public_key = models.TextField()
    private_key_pem = models.TextField()
    subject = models.CharField(max_length=255, default="mailto:admin@skuluansuan.local")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Konfigurasi VAPID"
        verbose_name_plural = "Konfigurasi VAPID"

    def save(self, *args, **kwargs):
        if not self.pk and VapidConfiguration.objects.exists():
            self.pk = VapidConfiguration.objects.first().pk
        super().save(*args, **kwargs)

    def __str__(self):
        return "Kunci Web Push VAPID"


class TrustedDevice(models.Model):
    STATUS_CHOICES = [("DIPERCAYAI", "Dipercayai"), ("MENUNGGU", "Menunggu kelulusan"), ("DISEKAT", "Disekat")]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trusted_devices")
    device_id = models.CharField(max_length=64, db_index=True)
    device_name = models.CharField(max_length=160, blank=True)
    platform = models.CharField(max_length=100, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    user_agent = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="MENUNGGU")
    first_ip = models.GenericIPAddressField(null=True, blank=True)
    last_ip = models.GenericIPAddressField(null=True, blank=True)
    first_seen_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="approved_trusted_devices")
    approved_at = models.DateTimeField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("user", "device_id")
        ordering = ["-last_seen_at"]
        indexes = [models.Index(fields=["user", "status"], name="device_user_status_idx")]
        verbose_name = "Peranti dipercayai"
        verbose_name_plural = "Peranti dipercayai"

    def __str__(self):
        return f"{self.user} - {self.device_name or self.device_id[:12]} ({self.get_status_display()})"


class LocationSecurityEvent(models.Model):
    EVENT_CHOICES = [("GPS", "Integriti GPS"), ("PERANTI", "Peranti"), ("KELAJUAN", "Kelajuan"), ("RISIKO", "Skor risiko")]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="location_security_events")
    attendance = models.ForeignKey(Attendance, null=True, blank=True, on_delete=models.SET_NULL, related_name="security_events")
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES, default="GPS")
    action = models.CharField(max_length=20, blank=True)
    risk_score = models.PositiveSmallIntegerField(default=0)
    risk_level = models.CharField(max_length=20, default="RENDAH")
    flags = models.JSONField(default=list, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    device_id = models.CharField(max_length=64, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    blocked = models.BooleanField(default=False)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["risk_level", "created_at"], name="locsec_risk_date_idx")]
        verbose_name = "Peristiwa keselamatan lokasi"
        verbose_name_plural = "Peristiwa keselamatan lokasi"

    def __str__(self):
        return f"{self.user} - {self.risk_level} ({self.risk_score})"
