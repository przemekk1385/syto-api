from datetime import date

import pytest
from dateutil import tz
from django.conf import settings
from django.shortcuts import reverse
from django.utils import timezone

from syto_api.models import AvailabilityHours

tz = tz.gettz(settings.TIME_ZONE)
TODAY = date.today()
START = timezone.datetime(TODAY.year, TODAY.month, TODAY.day, 6, 0, 0, tzinfo=tz)


@pytest.mark.django_db
def test_create_ok(client, syto_user):
    payload = {
        "day": TODAY,
        "hours": 8,
        "user": syto_user("foo@bar.baz").id,
    }

    response = client.post(reverse("syto_api:availability-hours-list"), payload)

    assert response.status_code == 201
    assert not set(payload.keys()).difference(response.data.keys())


@pytest.mark.django_db
def test_retrieve_ok(client, syto_user):
    availability = AvailabilityHours.objects.create(
        day=TODAY, hours=8, user=syto_user("foo@bar.baz")
    )

    response = client.get(
        reverse("syto_api:availability-hours-detail", args=[availability.id])
    )

    assert response.status_code == 200
    assert response.data["hours"] == 8
