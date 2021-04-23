from datetime import date
from typing import Iterable

from django.conf import settings
from django.core.mail import send_mass_mail
from django.utils.translation import gettext_lazy as _


def send_cancellation_info(day: date, emails: Iterable[str]) -> None:
    if settings.EMAIL_HOST != "localhost":
        send_mass_mail(
            (
                (
                    _("[SYTOPanel] Rejestracja anulowana."),
                    _(
                        "W związku z mniejszym zapotrzebowaniem na pracowników w dniu"
                        f" {day} Twoja rejestracja została anulowana."
                    ),
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                )
                for email in emails
            ),
            fail_silently=False,
        )
