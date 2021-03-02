from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AvailabilityHours, AvailabilityPeriod
from .serializers import AvailabilityHoursSerializer, AvailabilityPeriodSerializer


class AvailabilityView(APIView):
    @staticmethod
    def get_serializer_class(payload_fields):
        serializer_class = {
            ("day", "hours", "user"): AvailabilityHoursSerializer,
            ("end", "start", "user"): AvailabilityPeriodSerializer,
        }.get(payload_fields)

        if not serializer_class:
            raise ParseError("Unhandled payload.")

        return serializer_class

    def get(self, __):
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

    def post(self, request):
        serializer = self.get_serializer_class(tuple(sorted(request.POST.keys())))(
            data=request.POST
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
