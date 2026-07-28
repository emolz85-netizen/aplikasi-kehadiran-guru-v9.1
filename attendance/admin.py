from django.contrib import admin
from django.utils.html import format_html
from .models import TeacherProfile, Attendance, LeaveRequest, OfficialDuty, SchoolSettings, SchoolHoliday, AccountActivity


@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Sekolah", {"fields": ("school_name", "address", "logo")}),
        ("GPS", {"fields": ("latitude", "longitude", "radius_meters", "max_gps_accuracy_meters")}),
        ("Isnin hingga Khamis", {"fields": ("weekday_check_in", "weekday_check_out")}),
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
    list_display = ("user", "staff_id", "position", "phone")
    search_fields = ("user__username", "user__first_name", "user__last_name", "staff_id")


@admin.register(AccountActivity)
class AccountActivityAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "details", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("user__username", "details")
    readonly_fields = ("user", "action", "details", "created_at")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "check_in", "check_out", "status", "check_in_device", "check_in_ip", "distance_in_m", "gps_link", "selfie_preview")
    list_filter = ("date", "status")
    search_fields = ("user__username", "user__first_name", "user__last_name")
    date_hierarchy = "date"
    readonly_fields = ("check_in_ip", "check_out_ip", "check_in_device", "check_out_device", "check_in_user_agent", "check_out_user_agent")

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
    list_display = ("user", "start_date", "end_date", "status")
    list_filter = ("status",)


@admin.register(OfficialDuty)
class OfficialDutyAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "location", "start_date", "end_date", "status")
    list_filter = ("status",)
