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
def test_valid_data(syto_user):
    start = START
    end = START + timedelta(hours=8)
    data = {
        "start": start,
        "end": end,
        "user": syto_user("foo@bar.baz").id,
    }

    serializer = AvailabilityPeriodSerializer(data=data)

    assert serializer.is_valid()


@pytest.mark.django_db
def test_start_and_end_not_at_the_same_day(syto_user):
    start = START + timedelta(hours=16)  # today at 22:00
    end = start + timedelta(hours=8)  # tomorrow at 6:00
    data = {
        "start": start,
        "end": end,
        "user": syto_user("foo@bar.baz").id,
    }

    serializer = AvailabilityPeriodSerializer(data=data)
    serializer.is_valid()

    assert len(serializer.errors) == 1
    assert (
        serializer.errors["non_field_errors"][0]
        == "Start and end must be at the same day."
    )


@pytest.mark.django_db
def test_exceeded_maximum_number_of_hours(syto_user):
    start = START
    end = start + timedelta(hours=17)
    data = {
        "start": start,
        "end": end,
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
def test_not_full_number_of_hours(syto_user):
    start = START
    end = start + timedelta(minutes=450)  # 7 hours 30 minutes
    data = {
        "start": start,
        "end": end,
        "user": syto_user("foo@bar.baz").id,
    }

    serializer = AvailabilityPeriodSerializer(data=data)
    serializer.is_valid()

    assert len(serializer.errors) == 1
    assert (
        serializer.errors["non_field_errors"][0]
        == "Only full number of hours is allowed."
    )
