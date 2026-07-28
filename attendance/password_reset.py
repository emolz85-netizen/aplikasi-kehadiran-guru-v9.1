"""Password reset views with a friendly delivery-error page."""

from __future__ import annotations

import logging

from django.contrib.auth.views import PasswordResetView
from django.shortcuts import render

logger = logging.getLogger(__name__)


class SafePasswordResetView(PasswordResetView):
    """Avoid a blank 500 page when the email provider is misconfigured."""

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as exc:  # Email provider/network errors are surfaced here.
            logger.exception("Password reset email delivery failed: %s", exc)
            return render(
                self.request,
                "registration/password_reset_delivery_error.html",
                {"delivery_error": str(exc)},
                status=503,
            )
