from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response

from .models import AvailabilityHours, AvailabilityPeriod


def availability_list_view(__):
    # TODO: filtering for given users

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
            "hours": hours_a_day,
            "categories": [_("Cottage hours"), _("Stationary hours")],
        }
    )
