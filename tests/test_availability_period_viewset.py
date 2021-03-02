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
def test_create_ok(api_client, syto_user):
    start = START  # 6:00
    end = start + timedelta(hours=8)  # 14:00
    payload = {
        "start": start,
        "end": end,
        "user": syto_user("foo@bar.baz").id,
    }

    response = api_client.post(reverse("syto_api:availability-period-list"), payload)

    assert response.status_code == 201
    assert not set(payload.keys()).difference(response.data.keys())


@pytest.mark.django_db
def test_retrieve_ok(api_client, syto_user):
    start = START  # 6:00
    end = start + timedelta(hours=8)  # 14:00
    availability = AvailabilityPeriod.objects.create(
        start=start, end=end, user=syto_user("foo@bar.baz")
    )

    response = api_client.get(
        reverse("syto_api:availability-period-detail", args=[availability.id])
    )

    assert response.status_code == 200
    assert response.data["start"] == start.strftime(
        settings.REST_FRAMEWORK["DATETIME_FORMAT"]
    )
    assert response.data["end"] == end.strftime(
        settings.REST_FRAMEWORK["DATETIME_FORMAT"]
    )


@pytest.mark.django_db
def test_update_ok(api_client, syto_user):
    start = START  # 6:00
    end = start + timedelta(hours=8)  # 14:00
    availability = AvailabilityPeriod.objects.create(
        start=start, end=end, user=syto_user("foo@bar.baz")
    )

    end = end + timedelta(hours=2)  # 16:00
    response = api_client.patch(
        reverse("syto_api:availability-period-detail", args=[availability.id]),
        data=json.dumps({"end": str(end)}),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.data["start"] == start.strftime(
        settings.REST_FRAMEWORK["DATETIME_FORMAT"]
    )


@pytest.mark.django_db
def test_update_start_and_end_not_at_the_same_day(api_client, syto_user):
    start = START + timedelta(hours=8)  # 14:00
    end = start + timedelta(hours=8)  # 22:00

    availability = AvailabilityPeriod.objects.create(
        start=start, end=end, user=syto_user("foo@bar.baz")
    )

    end = end + timedelta(hours=16)  # 6:00, next day

    response = api_client.patch(
        reverse("syto_api:availability-period-detail", args=[availability.id]),
        data=json.dumps({"end": str(end)}),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert len(response.data["non_field_errors"]) == 1
    assert (
        response.data["non_field_errors"][0] == "Start and end must be at the same day."
    )


@pytest.mark.django_db
def test_end_before_start(api_client, syto_user):
    start = START  # 6:00
    end = start + timedelta(hours=8)  # 14:00

    availability = AvailabilityPeriod.objects.create(
        start=start, end=end, user=syto_user("foo@bar.baz")
    )

    end = start - timedelta(hours=2)  # 4:00

    response = api_client.patch(
        reverse("syto_api:availability-period-detail", args=[availability.id]),
        data=json.dumps({"end": str(end)}),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert len(response.data["non_field_errors"]) == 1
    assert response.data["non_field_errors"][0] == "End must be after start."


@pytest.mark.django_db
def test_update_exceeded_maximum_number_of_hours(api_client, syto_user):
    start = START  # 6:00
    end = start + timedelta(hours=8)  # 14:00

    availability = AvailabilityPeriod.objects.create(
        start=start, end=end, user=syto_user("foo@bar.baz")
    )

    end = start + timedelta(hours=17)  # 23:00

    response = api_client.patch(
        reverse("syto_api:availability-period-detail", args=[availability.id]),
        data=json.dumps({"end": str(end)}),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert len(response.data["non_field_errors"]) == 1
    assert (
        response.data["non_field_errors"][0] == "Maximum allowed number of hours is 16."
    )


@pytest.mark.django_db
def test_update_not_full_number_of_hours(api_client, syto_user):
    start = START  # 6:00
    end = start + timedelta(hours=8)  # 14:00

    availability = AvailabilityPeriod.objects.create(
        start=start, end=end, user=syto_user("foo@bar.baz")
    )

    end = start + timedelta(minutes=450)  # 13:30; 405 minutes = 7 hours 30 minutes

    response = api_client.patch(
        reverse("syto_api:availability-period-detail", args=[availability.id]),
        data=json.dumps({"end": str(end)}),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert len(response.data["non_field_errors"]) == 1
    assert (
        response.data["non_field_errors"][0] == "Only full number of hours is allowed."
    )
