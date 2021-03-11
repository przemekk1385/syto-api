from datetime import date, timedelta

import pytest
from dateutil import tz
from django.conf import settings
from django.utils import timezone

from syto_api.models import AvailabilityPeriod
from syto_api.serializers import AvailabilityPeriodSerializer

tz = tz.gettz(settings.TIME_ZONE)
TODAY = date.today()
START = timezone.datetime(TODAY.year, TODAY.month, TODAY.day, 6, 0, 0, tzinfo=tz)


@pytest.mark.django_db
def test_valid_data(syto_user, syto_slot):
    start = START
    end = START + timedelta(hours=8)
    data = {
        "slot": syto_slot(stationary_workers_limit=1).day,
        "start": start.time(),
        "end": end.time(),
        "user": syto_user().id,
    }

    serializer = AvailabilityPeriodSerializer(data=data)

    assert serializer.is_valid()


@pytest.mark.django_db
def test_end_before_start(syto_user, syto_slot):
    end = START  # 6:00
    start = end + timedelta(hours=8)  # 14:00
    data = {
        "slot": syto_slot(stationary_workers_limit=1).day,
        "start": start.time(),
        "end": end.time(),
        "user": syto_user().id,
    }

    serializer = AvailabilityPeriodSerializer(data=data)
    serializer.is_valid()

    assert len(serializer.errors.get("non_field_errors")) == 1
    assert serializer.errors.get("slot") is None
    assert serializer.errors["non_field_errors"][0] == "End must be after start."


@pytest.mark.django_db
def test_exceeded_maximum_number_of_hours(syto_user, syto_slot):
    start = START  # 6:00
    end = start + timedelta(hours=17)  # 23:00
    data = {
        "slot": syto_slot(stationary_workers_limit=1).day,
        "start": start.time(),
        "end": end.time(),
        "user": syto_user().id,
    }

    serializer = AvailabilityPeriodSerializer(data=data)
    serializer.is_valid()

    assert len(serializer.errors.get("non_field_errors")) == 1
    assert serializer.errors.get("slot") is None
    assert (
        serializer.errors["non_field_errors"][0]
        == "Maximum allowed number of hours is 16."
    )


@pytest.mark.django_db
def test_not_full_number_of_hours(syto_user, syto_slot):
    start = START  # 6:00
    end = start + timedelta(minutes=450)  # 13:30; 405 minutes = 7 hours 30 minutes
    data = {
        "slot": syto_slot(stationary_workers_limit=1).day,
        "start": start.time(),
        "end": end.time(),
        "user": syto_user().id,
    }

    serializer = AvailabilityPeriodSerializer(data=data)
    serializer.is_valid()

    assert len(serializer.errors.get("non_field_errors")) == 1
    assert serializer.errors.get("slot") is None
    assert (
        serializer.errors["non_field_errors"][0]
        == "Only full number of hours is allowed."
    )


@pytest.mark.django_db
def test_non_open_day(syto_user, syto_slot):
    start = START
    end = START + timedelta(hours=8)
    data = {
        "slot": syto_slot().day,
        "start": start.time(),
        "end": end.time(),
        "user": syto_user().id,
    }

    serializer = AvailabilityPeriodSerializer(data=data)
    serializer.is_valid()

    assert not serializer.errors.get("non_field_errors")
    assert len(serializer.errors.get("slot")) == 1
    assert serializer.errors["slot"][0] == "Cannot sign up for a non-open day."


@pytest.mark.django_db
def test_sign_up_only_once(syto_user, syto_slot):
    start = START
    end = START + timedelta(hours=8)

    slot = syto_slot(stationary_workers_limit=99)
    user = syto_user()
    AvailabilityPeriod.objects.create(slot=slot, start=start, end=end, user=user)

    data = {
        "slot": slot.day,
        "start": start.time(),
        "end": end.time(),
        "user": user.id,
    }

    serializer = AvailabilityPeriodSerializer(data=data)
    serializer.is_valid()

    assert serializer.errors.get("non_field_errors") is None
    assert len(serializer.errors.get("slot")) == 1
    assert serializer.errors["slot"][0] == "Worker can sign up only once for a day."


@pytest.mark.django_db
def test_workers_limit_reached(syto_user, syto_slot):
    start = START
    end = START + timedelta(hours=8)

    slot = syto_slot(stationary_workers_limit=1)
    AvailabilityPeriod.objects.create(
        slot=slot, start=start, end=end, user=syto_user("foo1@bar.baz")
    )

    data = {
        "slot": slot.day,
        "start": start.time(),
        "end": end.time(),
        "user": syto_user("foo2@bar.baz").id,
    }

    serializer = AvailabilityPeriodSerializer(data=data)
    serializer.is_valid()

    assert serializer.errors.get("non_field_errors") is None
    assert len(serializer.errors.get("slot")) == 1
    assert serializer.errors["slot"][0] == "Limit of signed up workers reached."
