"""HTTP email backends for platforms that block outbound SMTP ports.

Build 9.1.006.1 adds Brevo Transactional Email API support. Render Free
blocks outbound SMTP ports 25, 465 and 587, but HTTPS API requests remain
available.
"""

from __future__ import annotations

import json
from email.utils import getaddresses, parseaddr
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address
from django.core.exceptions import ImproperlyConfigured


class BrevoAPIEmailBackend(BaseEmailBackend):
    """Send Django EmailMessage objects through Brevo's HTTPS API."""

    api_url = "https://api.brevo.com/v3/smtp/email"

    def __init__(self, api_key=None, timeout=None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key or getattr(settings, "BREVO_API_KEY", "")
        self.timeout = timeout or getattr(settings, "EMAIL_TIMEOUT", 15)

    @staticmethod
    def _address(value: str) -> dict[str, str]:
        name, email = parseaddr(value)
        result = {"email": email or value}
        if name:
            result["name"] = name
        return result

    @staticmethod
    def _addresses(values) -> list[dict[str, str]]:
        parsed = getaddresses(values or [])
        result = []
        for name, email in parsed:
            if not email:
                continue
            item = {"email": email}
            if name:
                item["name"] = name
            result.append(item)
        return result

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        if not self.api_key:
            raise ImproperlyConfigured(
                "BREVO_API_KEY belum ditetapkan. Render Free tidak membenarkan SMTP; "
                "gunakan Brevo Transactional Email API melalui HTTPS."
            )

        sent = 0
        for message in email_messages:
            if self._send(message):
                sent += 1
        return sent

    def _send(self, message):
        if not message.recipients():
            return False

        sender = self._address(message.from_email or settings.DEFAULT_FROM_EMAIL)
        payload = {
            "sender": sender,
            "to": self._addresses(message.to),
            "subject": message.subject,
            "textContent": message.body or "",
        }
        cc = self._addresses(message.cc)
        bcc = self._addresses(message.bcc)
        reply_to = self._addresses(message.reply_to)
        if cc:
            payload["cc"] = cc
        if bcc:
            payload["bcc"] = bcc
        if reply_to:
            payload["replyTo"] = reply_to[0]

        # Prefer an HTML alternative if one exists.
        for alternative in getattr(message, "alternatives", []):
            content = getattr(alternative, "content", alternative[0])
            mimetype = getattr(alternative, "mimetype", alternative[1])
            if mimetype == "text/html":
                payload["htmlContent"] = content
                break

        request = Request(
            self.api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "accept": "application/json",
                "api-key": self.api_key,
                "content-type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                return 200 <= response.status < 300
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            if self.fail_silently:
                return False
            raise RuntimeError(
                f"Brevo API menolak e-mel (HTTP {exc.code}): {detail}"
            ) from exc
        except (URLError, TimeoutError, OSError) as exc:
            if self.fail_silently:
                return False
            raise RuntimeError(f"Tidak dapat menghubungi Brevo API: {exc}") from exc
