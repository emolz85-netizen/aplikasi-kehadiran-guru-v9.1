from datetime import time
from django.db import models
from django.contrib.auth.models import User


class SchoolSettings(models.Model):
    school_name = models.CharField(max_length=200, default="SK Ulu Ansuan")
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
    STATUS_CHOICES = [("MENUNGGU", "Menunggu"), ("DILULUSKAN", "Diluluskan"), ("DITOLAK", "Ditolak")]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="MENUNGGU")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


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
