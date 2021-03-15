from django.db import models
from django.db.models import OuterRef, Subquery, Sum
from django.db.models.functions import Coalesce
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import AvailabilityPeriod, Slot


@api_view(["GET"])
def total_availability_list_view(_):
    timedelta = (
        AvailabilityPeriod.objects.filter(slot=OuterRef("day"))
        .with_timedelta()
        .order_by()
        .values("timedelta")
    )
    total_timedelta = timedelta.annotate(
        total_timedelta=Sum("timedelta", output_field=models.IntegerField())
    ).values("total_timedelta")

    qs = Slot.objects.annotate(
        cottage_hours=Coalesce(Sum("availabilityhours__hours"), 0),
        stationary_hours=Coalesce(Subquery(total_timedelta) / 10 ** 6 / 3600, 0),
    ).values("day", "cottage_hours", "stationary_hours")

    return Response(data=qs)
