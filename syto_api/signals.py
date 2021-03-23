from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from .models import Slot


@receiver(post_save, sender=Slot)
def adjust_signed_in_workers_count(sender, instance=None, created=False, **kwargs):
    @transaction.atomic
    def _delete() -> None:
        limit = instance.stationary_workers_limit
        ids = instance.availabilityperiod_set.values_list("id", flat=True)[limit:]
        instance.availabilityperiod_set.filter(id__in=ids).delete()

    if (
        not created
        and (instance.stationary_workers_limit or 0)
        < instance.availabilityperiod_set.count()
    ):
        _delete()


# https://www.django-rest-framework.org/api-guide/authentication/#generating-tokens
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
