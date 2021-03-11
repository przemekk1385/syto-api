import json
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
def test_create_ok(api_client, syto_user, syto_slot):
    payload = {
        "slot": syto_slot().day,
        "hours": 8,
        "user": syto_user("foo@bar.baz").id,
    }

    response = api_client.post(reverse("syto_api:availability-hours-list"), payload)

    assert response.status_code == 201
    assert not set(payload.keys()).difference(response.data.keys())


@pytest.mark.django_db
def test_retrieve_ok(api_client, syto_user, syto_slot):
    availability = AvailabilityHours.objects.create(
        slot=syto_slot(), hours=8, user=syto_user("foo@bar.baz")
    )

    response = api_client.get(
        reverse("syto_api:availability-hours-detail", args=[availability.id])
    )

    assert response.status_code == 200
    assert response.data["hours"] == 8


@pytest.mark.django_db
def test_update_ok(api_client, syto_user, syto_slot):
    availability = AvailabilityHours.objects.create(
        slot=syto_slot(), hours=8, user=syto_user("foo@bar.baz")
    )

    response = api_client.patch(
        reverse("syto_api:availability-hours-detail", args=[availability.id]),
        data=json.dumps({"hours": 10}),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.data["hours"] == 10
