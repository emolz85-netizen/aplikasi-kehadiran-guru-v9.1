from .models import SystemAuditLog


def client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "") if request else ""
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR") if request else None


def device_name(user_agent):
    ua = (user_agent or "").lower()
    platform = "Android" if "android" in ua else "iPhone" if "iphone" in ua else "iPad" if "ipad" in ua else "Windows" if "windows" in ua else "macOS" if "macintosh" in ua else "Linux" if "linux" in ua else "Peranti lain"
    browser = "Edge" if "edg/" in ua else "Chrome" if "chrome/" in ua else "Firefox" if "firefox/" in ua else "Safari" if "safari/" in ua else "Pelayar lain"
    return f"{platform} · {browser}"


def write_audit(*, request=None, user=None, category="SISTEM", severity="INFO", action, description="", status_code=None, object_type="", object_id="", metadata=None):
    try:
        actor = user or (request.user if request and getattr(request, "user", None) and request.user.is_authenticated else None)
        ua = request.META.get("HTTP_USER_AGENT", "") if request else ""
        return SystemAuditLog.objects.create(
            user=actor,
            username_snapshot=(actor.username if actor else "Sistem"),
            category=category,
            severity=severity,
            action=action[:120],
            description=description,
            method=(request.method if request else ""),
            path=(request.path[:500] if request else ""),
            ip_address=client_ip(request),
            device=device_name(ua),
            user_agent=ua,
            status_code=status_code,
            object_type=object_type,
            object_id=str(object_id or ""),
            metadata=metadata or {},
        )
    except Exception:
        # Audit logging must never interrupt the core attendance workflow.
        return None
