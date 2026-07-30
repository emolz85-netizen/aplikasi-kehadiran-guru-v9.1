from django.conf import settings
from .models import SchoolSettings, AppNotification
from .version import (
    APP_VERSION, APP_VERSION_LABEL, APP_RELEASE_CHANNEL, APP_BUILD_NUMBER,
    APP_RELEASE_DATE, APP_DEVELOPER, APP_COMPANY, APP_PRODUCT, APP_COPYRIGHT,
)
from .permissions import APPROVAL_ROLES, AUDIT_VIEW_ROLES, SYSTEM_ADMIN_ROLES, MANAGEMENT_ROLES


def school_context(request):
    try:
        school = SchoolSettings.load()
        role_code = "PUBLIC"
        role_label = "Tetamu"
        has_management_dashboard = False
        if request.user.is_authenticated:
            profile, _ = request.user.teacherprofile, False
            role_code = profile.effective_role
            role_label = profile.role_label
            has_management_dashboard = profile.has_management_dashboard
        return {
            "USER_ROLE": role_code,
            "USER_ROLE_LABEL": role_label,
            "HAS_MANAGEMENT_DASHBOARD": has_management_dashboard,
            "CAN_APPROVE": role_code in APPROVAL_ROLES,
            "CAN_VIEW_AUDIT": role_code in AUDIT_VIEW_ROLES,
            "CAN_MANAGE_SYSTEM": role_code in SYSTEM_ADMIN_ROLES,
            "CAN_VIEW_MAP": role_code in MANAGEMENT_ROLES,
            "SCHOOL": school,
            "SCHOOL_NAME": school.school_name,
            "SCHOOL_LATITUDE": school.latitude,
            "SCHOOL_LONGITUDE": school.longitude,
            "SCHOOL_RADIUS_METERS": school.radius_meters,
            "APP_VERSION": APP_VERSION,
            "APP_VERSION_LABEL": APP_VERSION_LABEL,
            "APP_RELEASE_CHANNEL": APP_RELEASE_CHANNEL,
            "APP_BUILD_NUMBER": APP_BUILD_NUMBER,
            "APP_RELEASE_DATE": APP_RELEASE_DATE,
            "APP_DEVELOPER": APP_DEVELOPER,
            "APP_COMPANY": APP_COMPANY,
            "APP_PRODUCT": APP_PRODUCT,
            "APP_COPYRIGHT": APP_COPYRIGHT,
            "NOTIFICATION_UNREAD_COUNT": AppNotification.objects.filter(user=request.user, is_read=False).count() if request.user.is_authenticated else 0,
        }
    except Exception:
        role_code = "PUBLIC"
        role_label = "Tetamu"
        has_management_dashboard = False
        if request.user.is_authenticated:
            try:
                profile = request.user.teacherprofile
                role_code = profile.effective_role
                role_label = profile.role_label
                has_management_dashboard = profile.has_management_dashboard
            except Exception:
                role_code = "SUPER_ADMIN" if request.user.is_superuser else ("ADMIN" if request.user.is_staff else "GURU")
                role_label = "Super Admin" if request.user.is_superuser else ("Administrator" if request.user.is_staff else "Guru")
                has_management_dashboard = request.user.is_staff
        return {
            "USER_ROLE": role_code,
            "USER_ROLE_LABEL": role_label,
            "HAS_MANAGEMENT_DASHBOARD": has_management_dashboard,
            "CAN_APPROVE": role_code in APPROVAL_ROLES,
            "CAN_VIEW_AUDIT": role_code in AUDIT_VIEW_ROLES,
            "CAN_MANAGE_SYSTEM": role_code in SYSTEM_ADMIN_ROLES,
            "CAN_VIEW_MAP": role_code in MANAGEMENT_ROLES,
            "SCHOOL": None,
            "SCHOOL_NAME": settings.SCHOOL_NAME,
            "SCHOOL_LATITUDE": settings.SCHOOL_LATITUDE,
            "SCHOOL_LONGITUDE": settings.SCHOOL_LONGITUDE,
            "SCHOOL_RADIUS_METERS": settings.SCHOOL_RADIUS_METERS,
            "APP_VERSION": APP_VERSION,
            "APP_VERSION_LABEL": APP_VERSION_LABEL,
            "APP_RELEASE_CHANNEL": APP_RELEASE_CHANNEL,
            "APP_BUILD_NUMBER": APP_BUILD_NUMBER,
            "APP_RELEASE_DATE": APP_RELEASE_DATE,
            "APP_DEVELOPER": APP_DEVELOPER,
            "APP_COMPANY": APP_COMPANY,
            "APP_PRODUCT": APP_PRODUCT,
            "APP_COPYRIGHT": APP_COPYRIGHT,
            "NOTIFICATION_UNREAD_COUNT": AppNotification.objects.filter(user=request.user, is_read=False).count() if request.user.is_authenticated else 0,
        }
