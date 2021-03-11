from datetime import date, timedelta

import pytest
from dateutil import tz
from django.conf import settings
from django.utils import timezone

from syto_api.serializers import AvailabilityPeriodSerializer

tz = tz.gettz(settings.TIME_ZONE)
TODAY = date.today()
START = timezone.datetime(TODAY.year, TODAY.month, TODAY.day, 6, 0, 0, tzinfo=tz)


@pytest.mark.django_db
def test_valid_data(syto_user, syto_slot):
    start = START
    end = START + timedelta(hours=8)
    data = {
        "slot": syto_slot().day,
        "start": start.time(),
        "end": end.time(),
        "user": syto_user("foo@bar.baz").id,
    }

    serializer = AvailabilityPeriodSerializer(data=data)

    assert serializer.is_valid()


@pytest.mark.django_db
def test_end_before_start(syto_user, syto_slot):
    end = START  # 6:00
    start = end + timedelta(hours=8)  # 14:00
    data = {
        "slot": syto_slot().day,
        "start": start.time(),
        "end": end.time(),
        "user": syto_user("foo@bar.baz").id,
    }

    serializer = AvailabilityPeriodSerializer(data=data)
    serializer.is_valid()

    assert len(serializer.errors) == 1
    assert serializer.errors["non_field_errors"][0] == "End must be after start."


@pytest.mark.django_db
def test_exceeded_maximum_number_of_hours(syto_user, syto_slot):
    start = START  # 6:00
    end = start + timedelta(hours=17)  # 23:00
    data = {
        "slot": syto_slot().day,
        "start": start.time(),
        "end": end.time(),
        "user": syto_user("foo@bar.baz").id,
    }

    serializer = AvailabilityPeriodSerializer(data=data)
    serializer.is_valid()

    assert len(serializer.errors) == 1
    assert (
        serializer.errors["non_field_errors"][0]
        == "Maximum allowed number of hours is 16."
    )


@pytest.mark.django_db
def test_not_full_number_of_hours(syto_user, syto_slot):
    start = START  # 6:00
    end = start + timedelta(minutes=450)  # 13:30; 405 minutes = 7 hours 30 minutes
    data = {
        "slot": syto_slot().day,
        "start": start.time(),
        "end": end.time(),
        "user": syto_user("foo@bar.baz").id,
    }

    serializer = AvailabilityPeriodSerializer(data=data)
    serializer.is_valid()

    assert len(serializer.errors) == 1
    assert (
        serializer.errors["non_field_errors"][0]
        == "Only full number of hours is allowed."
    )
