from datetime import time
from django.db import models
from django.contrib.auth.models import User


class SchoolSettings(models.Model):
    school_name = models.CharField(max_length=200, default="SK Ulu Ansuan")
    address = models.TextField(blank=True, default="")
    latitude = models.FloatField(default=5.745697)
    longitude = models.FloatField(default=117.173844)
    radius_meters = models.PositiveIntegerField(default=50)
    max_gps_accuracy_meters = models.PositiveIntegerField(default=50)
    weekday_check_in = models.TimeField(default=time(7, 10))
    weekday_check_out = models.TimeField(default=time(13, 0))
    friday_check_in = models.TimeField(default=time(7, 10))
    friday_check_out = models.TimeField(default=time(11, 40))
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
