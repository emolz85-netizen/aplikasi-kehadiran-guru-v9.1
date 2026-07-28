import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class StrongPasswordValidator:
    """Pastikan kata laluan mempunyai gabungan aksara yang munasabah."""

    def validate(self, password, user=None):
        missing = []
        if not re.search(r"[A-Z]", password):
            missing.append(_("sekurang-kurangnya satu huruf besar"))
        if not re.search(r"[a-z]", password):
            missing.append(_("sekurang-kurangnya satu huruf kecil"))
        if not re.search(r"\d", password):
            missing.append(_("sekurang-kurangnya satu nombor"))
        if not re.search(r"[^A-Za-z0-9]", password):
            missing.append(_("sekurang-kurangnya satu simbol"))
        if missing:
            raise ValidationError(
                _("Kata laluan mesti mengandungi %(requirements)s."),
                code="password_not_strong",
                params={"requirements": ", ".join(missing)},
            )

    def get_help_text(self):
        return _(
            "Kata laluan mesti mempunyai sekurang-kurangnya 8 aksara, "
            "huruf besar, huruf kecil, nombor dan simbol."
        )
