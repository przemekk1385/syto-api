from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import AvailabilityHours, AvailabilityPeriod


@api_view(["GET"])
def total_availability_list_view(__):
    hours_a_day = {
        item["day"]: [item["hours_total"]]
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
        hours = item["timedelta_total"].seconds // 3600
        try:
            hours_a_day[item["start__date"]].append(hours)
        except KeyError:
            hours_a_day[item["start__date"]] = [0, hours]

    return Response(
        data={
            "hours": [
                {"day": day.strftime("%Y-%m-%d"), "hours": hours}
                for day, hours in hours_a_day.items()
            ],
            "categories": [_("Cottage hours"), _("Stationary hours")],
        }
    )
