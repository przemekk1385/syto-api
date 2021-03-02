from datetime import date, timedelta

import pytest
from dateutil import tz
from django.conf import settings
from django.shortcuts import reverse
from django.utils import timezone

from syto_api.models import AvailabilityPeriod

tz = tz.gettz(settings.TIME_ZONE)
TODAY = date.today()
START = timezone.datetime(TODAY.year, TODAY.month, TODAY.day, 6, 0, 0, tzinfo=tz)


@pytest.mark.django_db
def test_create_ok(client, syto_user):
    start = START
    end = start + timedelta(hours=8)
    payload = {
        "start": start,
        "end": end,
        "user": syto_user("foo@bar.baz").id,
    }

    response = client.post(reverse("syto_api:availability-period-list"), payload)

    assert response.status_code == 201
    assert not set(payload.keys()).difference(response.data.keys())


@pytest.mark.django_db
def test_retrieve_ok(client, syto_user):
    start = START
    end = start + timedelta(hours=8)
    availability = AvailabilityPeriod.objects.create(
        start=start, end=end, user=syto_user("foo@bar.baz")
    )

    response = client.get(
        reverse("syto_api:availability-period-detail", args=[availability.id])
    )

    assert response.status_code == 200
    assert response.data["start"] == start.strftime(
        settings.REST_FRAMEWORK["DATETIME_FORMAT"]
    )
    assert response.data["end"] == end.strftime(
        settings.REST_FRAMEWORK["DATETIME_FORMAT"]
    )
