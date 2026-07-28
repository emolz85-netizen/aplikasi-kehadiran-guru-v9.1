from .audit import write_audit


class ProfessionalAuditMiddleware:
    """Records authenticated data-changing requests without storing passwords or form contents."""
    EXCLUDED_PREFIXES = ("/static/", "/media/", "/health/", "/service-worker.js", "/manifest.json", "/offline/", "/pwa/pasang/")

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method in {"POST", "PUT", "PATCH", "DELETE"} and not request.path.startswith(self.EXCLUDED_PREFIXES):
            user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
            if user:
                category = self._category(request.path)
                severity = "AMARAN" if response.status_code >= 400 else "INFO"
                write_audit(
                    request=request,
                    user=user,
                    category=category,
                    severity=severity,
                    action=self._action(request),
                    description=f"Permintaan {request.method} diproses dengan status HTTP {response.status_code}.",
                    status_code=response.status_code,
                )
        return response

    @staticmethod
    def _category(path):
        if "cuti" in path:
            return "CUTI"
        if "rekod" in path or "kehadiran" in path:
            return "KEHADIRAN"
        if "tugas" in path:
            return "TUGAS"
        if "laporan" in path:
            return "LAPORAN"
        if "kata-laluan" in path or "login" in path or "logout" in path or "profil" in path:
            return "AUTH"
        if "admin" in path or "import" in path:
            return "PENTADBIRAN"
        return "SISTEM"

    @staticmethod
    def _action(request):
        match = getattr(request, "resolver_match", None)
        name = match.url_name if match else ""
        labels = {
            "record_attendance": "Rekod kehadiran dikemas kini",
            "leave_cancel": "Permohonan cuti dibatalkan",
            "leave_review": "Permohonan cuti disemak",
            "password_recovery_approve": "QR reset diluluskan",
            "password_recovery_reject": "Permintaan reset ditolak",
            "import_teachers": "Import guru diproses",
            "profile_page": "Profil pengguna dikemas kini",
        }
        return labels.get(name, f"Tindakan sistem: {name or request.path}")
