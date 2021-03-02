from datetime import date, timedelta

import pytest
from dateutil import tz
from django.conf import settings
from django.shortcuts import reverse
from django.utils import timezone

from syto_api.models import AvailabilityHours, AvailabilityPeriod
from syto_api.views import total_availability_list_view

tz = tz.gettz(settings.TIME_ZONE)
TODAY = date.today()
START = timezone.datetime(TODAY.year, TODAY.month, TODAY.day, 6, 0, 0, tzinfo=tz)


@pytest.mark.django_db
def test_get(rf, syto_user):
    users = [syto_user("foo1@bar.baz"), syto_user("foo2@bar.baz")]
    for i in range(10):
        AvailabilityHours.objects.create(
            day=TODAY - timedelta(days=i), hours=8, user=users[0]
        )
        AvailabilityHours.objects.create(
            day=TODAY - timedelta(days=i), hours=8, user=users[1]
        )

        start = START - timedelta(days=i)
        end = start + timedelta(hours=8)

        AvailabilityPeriod.objects.create(start=start, end=end, user=users[0])
        AvailabilityPeriod.objects.create(start=start, end=end, user=users[1])

    request = rf.get(reverse("syto_api:total-availability-list"))

    response = total_availability_list_view(request)

    assert response.status_code == 200
    assert set(response.data.keys()) == {"hours", "categories"}


def test_post(rf):
    payload = {
        "foo": "foo",
        "bar": "bar",
    }

    request = rf.post(reverse("syto_api:total-availability-list"), payload)

    response = total_availability_list_view(request)

    assert response.status_code == 405
