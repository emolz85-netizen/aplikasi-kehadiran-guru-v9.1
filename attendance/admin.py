from django.contrib import admin
from django.utils.html import format_html
from .models import TeacherProfile, Attendance, LeaveRequest, OfficialDuty, SchoolSettings, SchoolHoliday, AccountActivity, PasswordRecoveryRequest, SystemAuditLog, PushSubscription, AppNotification, VapidConfiguration, TrustedDevice, LocationSecurityEvent, FaceLoginAttempt


@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Sekolah", {"fields": ("school_name", "school_code", "address", "phone", "email", "logo")}),
        ("GPS", {"fields": ("latitude", "longitude", "radius_meters", "max_gps_accuracy_meters")}),
        ("Isnin hingga Khamis", {"fields": ("weekday_check_in", "weekday_check_out")}),
        ("Pengesahan wajah", {"fields": ("face_verification_enabled", "face_match_threshold", "require_liveness_challenge", "face_login_enabled", "face_login_threshold", "face_login_max_attempts")}),
        ("Anti GPS Spoofing & Device Trust", {"fields": ("device_trust_enabled", "auto_trust_first_device", "block_untrusted_device", "max_location_age_seconds", "max_plausible_speed_kmh", "high_risk_block_threshold")}),
        ("Jumaat", {"fields": ("friday_check_in", "friday_check_out")}),
    )

    def has_add_permission(self, request):
        return not SchoolSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SchoolHoliday)
class SchoolHolidayAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "is_active")
    list_filter = ("is_active", "date")
    search_fields = ("name", "description")
    date_hierarchy = "date"
    ordering = ("date",)


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "staff_id", "position", "role", "phone", "face_login_active", "reference_photo_updated_at", "face_login_last_used_at")
    list_filter = ("role", "face_login_active",)
    search_fields = ("user__username", "user__first_name", "user__last_name", "staff_id")


@admin.register(AccountActivity)
class AccountActivityAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "details", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("user__username", "details")
    readonly_fields = ("user", "action", "details", "created_at")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "check_in", "check_out", "status", "face_in_status", "face_in_score", "check_in_device", "check_in_ip", "distance_in_m", "gps_link", "selfie_preview")
    list_filter = ("date", "status")
    search_fields = ("user__username", "user__first_name", "user__last_name")
    date_hierarchy = "date"
    readonly_fields = ("check_in_device_id", "check_out_device_id", "check_in_risk_score", "check_out_risk_score", "check_in_risk_level", "check_out_risk_level", "check_in_security_flags", "check_out_security_flags", "check_in_ip", "check_out_ip", "check_in_device", "check_out_device", "check_in_user_agent", "check_out_user_agent", "face_in_score", "face_out_score", "face_in_status", "face_out_status", "liveness_in_challenge", "liveness_out_challenge", "selfie_in_hash", "selfie_out_hash")

    @admin.display(description="GPS")
    def gps_link(self, obj):
        if obj.check_in_lat is None or obj.check_in_lng is None:
            return "—"
        url = f"https://www.google.com/maps?q={obj.check_in_lat},{obj.check_in_lng}"
        return format_html('<a href="{}" target="_blank">Lihat peta</a>', url)

    @admin.display(description="Swafoto")
    def selfie_preview(self, obj):
        if not obj.selfie_in:
            return "—"
        return format_html('<a href="{}" target="_blank"><img src="{}" style="height:45px;border-radius:6px"></a>', obj.selfie_in.url, obj.selfie_in.url)


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "leave_type", "start_date", "end_date", "total_days_display", "status", "reviewed_by", "reviewed_at")
    list_filter = ("status", "leave_type", "start_date")
    search_fields = ("user__username", "user__first_name", "user__last_name", "reason", "admin_note")
    readonly_fields = ("created_at", "updated_at", "reviewed_at")
    date_hierarchy = "start_date"

    @admin.display(description="Hari")
    def total_days_display(self, obj):
        return obj.total_days


@admin.register(OfficialDuty)
class OfficialDutyAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "location", "start_date", "end_date", "status")
    list_filter = ("status",)


@admin.register(PasswordRecoveryRequest)
class PasswordRecoveryRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "requested_at", "approved_at", "expires_at", "approved_by")
    list_filter = ("status", "requested_at")
    search_fields = ("user__username", "user__first_name", "user__last_name")
    readonly_fields = ("code_hash", "code_display", "requested_at", "approved_at", "used_at")


@admin.register(SystemAuditLog)
class SystemAuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "username_snapshot", "category", "severity", "action", "ip_address", "status_code")
    list_filter = ("category", "severity", "created_at")
    search_fields = ("username_snapshot", "action", "description", "ip_address", "path")
    readonly_fields = tuple(field.name for field in SystemAuditLog._meta.fields)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "is_active", "updated_at")
    list_filter = ("is_active", "updated_at")
    search_fields = ("user__username", "user__first_name", "user__last_name", "endpoint")
    readonly_fields = ("endpoint", "p256dh", "auth", "user_agent", "created_at", "updated_at")


@admin.register(AppNotification)
class AppNotificationAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "category", "title", "is_read")
    list_filter = ("category", "is_read", "created_at")
    search_fields = ("user__username", "title", "message")
    readonly_fields = ("created_at", "read_at")


@admin.register(VapidConfiguration)
class VapidConfigurationAdmin(admin.ModelAdmin):
    list_display = ("subject", "created_at", "updated_at")
    readonly_fields = ("public_key", "private_key_pem", "created_at", "updated_at")
    def has_add_permission(self, request):
        return not VapidConfiguration.objects.exists()
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TrustedDevice)
class TrustedDeviceAdmin(admin.ModelAdmin):
    list_display = ("user", "device_name", "platform", "browser", "status", "last_ip", "last_seen_at")
    list_filter = ("status", "platform", "last_seen_at")
    search_fields = ("user__username", "user__first_name", "device_name", "device_id", "last_ip")
    readonly_fields = ("device_id", "first_ip", "first_seen_at", "last_seen_at", "user_agent")

@admin.register(LocationSecurityEvent)
class LocationSecurityEventAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "risk_level", "risk_score", "blocked", "accuracy", "device_id")
    list_filter = ("risk_level", "blocked", "event_type", "created_at")
    search_fields = ("user__username", "device_id", "details", "ip_address")
    readonly_fields = tuple(field.name for field in LocationSecurityEvent._meta.fields)
    date_hierarchy = "created_at"
    def has_add_permission(self, request): return False


@admin.register(FaceLoginAttempt)
class FaceLoginAttemptAdmin(admin.ModelAdmin):
    list_display = ("attempted_at", "user", "success", "score", "ip_address", "details")
    list_filter = ("success", "attempted_at")
    search_fields = ("user__username", "details", "ip_address")
    readonly_fields = ("user", "attempted_at", "success", "score", "ip_address", "user_agent", "details")

    def has_add_permission(self, request):
        return False
