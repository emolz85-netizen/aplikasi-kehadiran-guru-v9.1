from django.conf import settings
from .models import SchoolSettings, AppNotification
from .version import APP_VERSION, APP_VERSION_LABEL, APP_RELEASE_CHANNEL


def school_context(request):
    try:
        school = SchoolSettings.load()
        return {
            "SCHOOL": school,
            "SCHOOL_NAME": school.school_name,
            "SCHOOL_LATITUDE": school.latitude,
            "SCHOOL_LONGITUDE": school.longitude,
            "SCHOOL_RADIUS_METERS": school.radius_meters,
            "APP_VERSION": APP_VERSION,
            "APP_VERSION_LABEL": APP_VERSION_LABEL,
            "APP_RELEASE_CHANNEL": APP_RELEASE_CHANNEL,
            "NOTIFICATION_UNREAD_COUNT": AppNotification.objects.filter(user=request.user, is_read=False).count() if request.user.is_authenticated else 0,
        }
    except Exception:
        return {
            "SCHOOL": None,
            "SCHOOL_NAME": settings.SCHOOL_NAME,
            "SCHOOL_LATITUDE": settings.SCHOOL_LATITUDE,
            "SCHOOL_LONGITUDE": settings.SCHOOL_LONGITUDE,
            "SCHOOL_RADIUS_METERS": settings.SCHOOL_RADIUS_METERS,
            "APP_VERSION": APP_VERSION,
            "APP_VERSION_LABEL": APP_VERSION_LABEL,
            "APP_RELEASE_CHANNEL": APP_RELEASE_CHANNEL,
            "NOTIFICATION_UNREAD_COUNT": AppNotification.objects.filter(user=request.user, is_read=False).count() if request.user.is_authenticated else 0,
        }
