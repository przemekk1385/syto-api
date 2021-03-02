from copy import copy

from django.db.models import Sum
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import AvailabilityHours, AvailabilityPeriod


@api_view(["GET"])
def total_availability_list_view(__):
    default_hours = {}
    default_hours.setdefault("cottage_hours", 0)
    default_hours.setdefault("stationary_hours", 0)

    def make_hours(**kwargs):
        hours = copy(default_hours)
        hours.update(**kwargs)
        return hours

    hours_a_day = {
        item["day"]: make_hours(cottage_hours=item["hours_total"])
        for item in AvailabilityHours.objects.values("day")
        .annotate(hours_total=Sum("hours"))
        .order_by("day")
        .values("day", "hours_total")
    }

    for item in (
        AvailabilityPeriod.objects.with_timedelta()
        .values("start__date")
        .annotate(timedelta_total=Sum("timedelta"))
        .order_by("start__date")
        .values("start__date", "timedelta_total")
    ):
        hours_total = item["timedelta_total"].seconds // 3600
        try:
            hours_a_day[item["start__date"]]["stationary_hours"] = hours_total
        except KeyError:
            hours_a_day[item["start__date"]] = make_hours(stationary_hours=hours_total)

    return Response(
        data=[
            {
                "day": day.strftime("%Y-%m-%d"),
                **hours,
            }
            for day, hours in hours_a_day.items()
        ]
    )
