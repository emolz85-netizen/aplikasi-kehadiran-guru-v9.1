import base64
import json
import logging
from django.utils import timezone
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from pywebpush import webpush, WebPushException
from .models import AppNotification, PushSubscription, VapidConfiguration

logger = logging.getLogger(__name__)


def get_vapid_configuration():
    config = VapidConfiguration.objects.first()
    if config:
        return config
    private_key = ec.generate_private_key(ec.SECP256R1())
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    point = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint,
    )
    public_key = base64.urlsafe_b64encode(point).rstrip(b"=").decode("ascii")
    return VapidConfiguration.objects.create(public_key=public_key, private_key_pem=private_pem)


def send_notification(user, title, message, category="SISTEM", url="/"):
    notification = AppNotification.objects.create(
        user=user, title=title, message=message, category=category, url=url or "/"
    )
    config = get_vapid_configuration()
    payload = json.dumps({
        "title": title,
        "body": message,
        "url": url or "/",
        "notification_id": notification.pk,
        "category": category,
    })
    for subscription in PushSubscription.objects.filter(user=user, is_active=True):
        info = {
            "endpoint": subscription.endpoint,
            "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth},
        }
        try:
            webpush(
                subscription_info=info,
                data=payload,
                vapid_private_key=config.private_key_pem,
                vapid_claims={"sub": config.subject},
                ttl=3600,
            )
        except WebPushException as exc:
            status = getattr(getattr(exc, "response", None), "status_code", None)
            if status in (404, 410):
                subscription.is_active = False
                subscription.save(update_fields=["is_active", "updated_at"])
            logger.warning("Web push gagal untuk langganan %s: %s", subscription.pk, exc)
        except Exception:
            logger.exception("Ralat menghantar web push")
    return notification


def mark_notification_read(notification):
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=["is_read", "read_at"])
