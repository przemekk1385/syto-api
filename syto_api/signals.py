from django.db import transaction
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Slot


@receiver(pre_save, sender=Slot)
def adjust_signed_in_workers_count(sender, **kwargs):
    instance, created = kwargs.get("instance"), kwargs.get("created")

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
