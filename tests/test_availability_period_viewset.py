import json
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
def test_create_ok(api_client, syto_user, syto_slot):
    start = START  # 6:00
    end = start + timedelta(hours=8)  # 14:00
    payload = {
        "slot": syto_slot().day,
        "start": start.time(),
        "end": end.time(),
        "user": syto_user("foo@bar.baz").id,
    }

    response = api_client.post(reverse("syto_api:availability-period-list"), payload)

    assert response.status_code == 201
    assert not set(payload.keys()).difference(response.data.keys())


@pytest.mark.django_db
def test_retrieve_ok(api_client, syto_user, syto_slot):
    start = START  # 6:00
    end = start + timedelta(hours=8)  # 14:00
    availability = AvailabilityPeriod.objects.create(
        slot=syto_slot(),
        start=start.time(),
        end=end.time(),
        user=syto_user("foo@bar.baz"),
    )

    response = api_client.get(
        reverse("syto_api:availability-period-detail", args=[availability.id])
    )

    assert response.status_code == 200
    assert response.data["start"] == start.strftime(
        settings.REST_FRAMEWORK["TIME_FORMAT"]
    )
    assert response.data["end"] == end.strftime(settings.REST_FRAMEWORK["TIME_FORMAT"])


@pytest.mark.django_db
def test_update_ok(api_client, syto_user, syto_slot):
    start = START  # 6:00
    end = start + timedelta(hours=8)  # 14:00
    availability = AvailabilityPeriod.objects.create(
        slot=syto_slot(),
        start=start.time(),
        end=end.time(),
        user=syto_user("foo@bar.baz"),
    )

    end = end + timedelta(hours=2)  # 16:00
    response = api_client.patch(
        reverse("syto_api:availability-period-detail", args=[availability.id]),
        data=json.dumps({"end": str(end.time())}),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.data["start"] == start.strftime(
        settings.REST_FRAMEWORK["TIME_FORMAT"]
    )


@pytest.mark.django_db
def test_end_before_start(api_client, syto_user, syto_slot):
    start = START  # 6:00
    end = start + timedelta(hours=8)  # 14:00

    availability = AvailabilityPeriod.objects.create(
        slot=syto_slot(),
        start=start.time(),
        end=end.time(),
        user=syto_user("foo@bar.baz"),
    )

    end = start - timedelta(hours=2)  # 4:00

    response = api_client.patch(
        reverse("syto_api:availability-period-detail", args=[availability.id]),
        data=json.dumps({"end": str(end.time())}),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert len(response.data["non_field_errors"]) == 1
    assert response.data["non_field_errors"][0] == "End must be after start."


@pytest.mark.django_db
def test_update_exceeded_maximum_number_of_hours(api_client, syto_user, syto_slot):
    start = START  # 6:00
    end = start + timedelta(hours=8)  # 14:00

    availability = AvailabilityPeriod.objects.create(
        slot=syto_slot(),
        start=start.time(),
        end=end.time(),
        user=syto_user("foo@bar.baz"),
    )

    end = start + timedelta(hours=17)  # 23:00

    response = api_client.patch(
        reverse("syto_api:availability-period-detail", args=[availability.id]),
        data=json.dumps({"end": str(end.time())}),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert len(response.data["non_field_errors"]) == 1
    assert (
        response.data["non_field_errors"][0] == "Maximum allowed number of hours is 16."
    )


@pytest.mark.django_db
def test_update_not_full_number_of_hours(api_client, syto_user, syto_slot):
    start = START  # 6:00
    end = start + timedelta(hours=8)  # 14:00

    availability = AvailabilityPeriod.objects.create(
        slot=syto_slot(),
        start=start.time(),
        end=end.time(),
        user=syto_user("foo@bar.baz"),
    )

    end = start + timedelta(minutes=450)  # 13:30; 405 minutes = 7 hours 30 minutes

    response = api_client.patch(
        reverse("syto_api:availability-period-detail", args=[availability.id]),
        data=json.dumps({"end": str(end.time())}),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert len(response.data["non_field_errors"]) == 1
    assert (
        response.data["non_field_errors"][0] == "Only full number of hours is allowed."
    )
