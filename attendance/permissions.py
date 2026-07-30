from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .models import TeacherProfile

MANAGEMENT_ROLES = {"GURU_BESAR", "GPK", "KERANI", "ADMIN", "SUPER_ADMIN"}
APPROVAL_ROLES = {"GURU_BESAR", "GPK", "ADMIN", "SUPER_ADMIN"}
REPORT_ALL_ROLES = MANAGEMENT_ROLES
AUDIT_VIEW_ROLES = MANAGEMENT_ROLES
SYSTEM_ADMIN_ROLES = {"ADMIN", "SUPER_ADMIN"}
ATTENDANCE_ROLES = {"GURU", "GPK", "GURU_BESAR", "KERANI"}


def get_user_role(user):
    if not user or not user.is_authenticated:
        return "PUBLIC"
    try:
        profile, _ = TeacherProfile.objects.get_or_create(user=user)
        return profile.effective_role
    except Exception:
        if user.is_superuser:
            return "SUPER_ADMIN"
        if user.is_staff:
            return "ADMIN"
        return "GURU"


def role_required(*allowed_roles, message="Anda tidak mempunyai kebenaran untuk membuka halaman ini."):
    allowed = set(allowed_roles)

    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if get_user_role(request.user) not in allowed:
                messages.error(request, message)
                return redirect("dashboard")
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator
