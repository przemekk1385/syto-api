from django.db import models
from django.db.models import Count, OuterRef, Subquery, Sum
from django.db.models.functions import Coalesce
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import AvailabilityPeriod, Slot
from .serializers import AvailabilityOverviewBaseSerializer


@api_view(["GET"])
def availability_overview_list(_):
    timedelta = (
        AvailabilityPeriod.objects.filter(slot=OuterRef("day"))
        .with_timedelta()
        .order_by()
        .values("slot")
    )
    total_timedelta = timedelta.annotate(
        total_timedelta=Sum("timedelta", output_field=models.IntegerField())
    ).values("total_timedelta")

    stationary_workers = (
        Slot.objects.filter(day=OuterRef("day"))
        .annotate(stationary_workers=Count("availabilityperiod"))
        .values("stationary_workers")
    )

    qs = Slot.objects.annotate(
        cottage_hours=Coalesce(Sum("availabilityhours__hours"), 0),
        cottage_workers=Count("availabilityhours"),
        stationary_hours=Coalesce(Subquery(total_timedelta), 0),
        stationary_workers=Subquery(stationary_workers),
    ).order_by("-day")

    serializer = AvailabilityOverviewBaseSerializer(qs, many=True)

    return Response(data=serializer.data)
