from typing import List

from django.conf import settings
from django.contrib.auth.backends import get_user_model
from django.db import transaction
from django.db.models import Q
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from .models import Slot
from .services import send_cancellation_info

UserModel = get_user_model()


@receiver(post_save, sender=Slot)
@transaction.atomic
def adjust_signed_in_cottage_workers_number(
    sender, instance=None, created=False, **kwargs
):
    day = instance.day

    def _get_affected_emails() -> List[str]:
        return instance.availabilityperiod_set.values_list("user__email", flat=True)

    def _delete() -> None:
        instance.availabilityhours_set.all().delete()

    if (
        not created
        and not instance.is_open_for_cottage_workers
        and instance.availabilityhours_set.exists()
    ):
        emails = _get_affected_emails()
        _delete()
        send_cancellation_info(day, emails)


@receiver(post_save, sender=Slot)
@transaction.atomic
def adjust_signed_in_stationary_workers_number(
    sender, instance=None, created=False, **kwargs
):
    day = instance.day
    limit = instance.stationary_workers_limit

    def _get_affected_emails() -> List[str]:
        return instance.availabilityperiod_set.values_list("user__email", flat=True)[
            limit:
        ]

    def _delete() -> None:
        ids = instance.availabilityperiod_set.values_list("id", flat=True)[limit:]
        instance.availabilityperiod_set.filter(id__in=ids).delete()

    if (
        not created
        and (instance.stationary_workers_limit or 0)
        < instance.availabilityperiod_set.count()
    ):
        emails = _get_affected_emails()
        _delete()
        send_cancellation_info(day, emails)


@receiver(post_delete, sender=Slot)
def handle_slot_deletion(sender, instance=None, **kwargs):
    emails = UserModel.objects.filter(
        Q(availabilityhours__slot=instance) | Q(availabilityperiod__slot=instance)
    ).values_list("email", flat=True)
    send_cancellation_info(instance.day, emails)


# https://www.django-rest-framework.org/api-guide/authentication/#generating-tokens
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
