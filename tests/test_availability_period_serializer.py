from functools import partial

import pytest

from syto_api.models import AvailabilityPeriod
from syto_api.serializers import AvailabilityPeriodSerializer


@pytest.mark.parametrize(
    ("start", "end"),
    [
        ("2021-01-01 6:00", "2021-01-01 14:00"),
        ("2021-01-01 22:00", "2021-01-02 6:00"),
    ],
)
@pytest.mark.django_db
def test_valid_data(start, end, rf, syto_user, syto_slot):
    request = rf.post("foo")
    request.user = syto_user()

    data = {
        "slot": syto_slot(stationary_workers_limit=1).day,
        "start": start,
        "end": end,
    }

    serializer = AvailabilityPeriodSerializer(data=data, context={"request": request})

    assert serializer.is_valid()


@pytest.mark.parametrize(
    ("start", "end", "error_message"),
    [
        (
            "2021-01-01 6:00",
            "2021-01-01 23:00",
            "Maximum allowed number of hours is 16.",
        ),
        (
            "2021-01-01 18:00",
            "2021-01-02 11:00",
            "Maximum allowed number of hours is 16.",
        ),
        (
            "2021-01-01 6:00",
            "2021-01-01 13:30",
            "Only full number of hours is allowed.",
        ),
    ],
)
@pytest.mark.django_db
def test_non_field_errors(rf, start, end, error_message, syto_user, syto_slot):
    request = rf.post("foo")
    request.user = syto_user()

    data = {
        "slot": syto_slot(stationary_workers_limit=1).day,
        "start": start,
        "end": end,
    }

    serializer = AvailabilityPeriodSerializer(data=data, context={"request": request})
    serializer.is_valid()

    assert len(serializer.errors.get("non_field_errors")) == 1
    assert serializer.errors.get("slot") is None
    assert serializer.errors.get("user") is None
    assert serializer.errors["non_field_errors"][0] == error_message


@pytest.mark.django_db
def test_non_open_day(rf, syto_user, syto_slot):
    request = rf.post("foo")
    request.user = syto_user()

    data = {
        "slot": syto_slot().day,
        "start": "2021-01-01 6:00",
        "end": "2021-01-01 14:00",
    }

    serializer = AvailabilityPeriodSerializer(data=data, context={"request": request})
    serializer.is_valid()

    assert serializer.errors.get("non_field_errors") is None
    assert len(serializer.errors.get("slot")) == 1
    assert serializer.errors.get("user") is None
    assert serializer.errors["slot"][0] == "Cannot sign up for a non-open day."


@pytest.mark.django_db
def test_workers_limit_reached(rf, syto_datetime, syto_user, syto_slot):
    dt = partial(syto_datetime, **{"year": 2020, "month": 1, "day": 1})
    slot = syto_slot(day=dt().date(), stationary_workers_limit=1)
    user1 = syto_user("foo1@bar.baz")
    user2 = syto_user("foo2@bar.baz")

    AvailabilityPeriod.objects.create(
        slot=slot, start=dt(hour=6), end=dt(hour=14), user=user1
    )

    request = rf.post("foo")
    request.user = user2

    data = {
        "slot": slot.day,
        "start": "2021-01-01 6:00",
        "end": "2021-01-01 14:00",
    }

    serializer = AvailabilityPeriodSerializer(data=data, context={"request": request})
    serializer.is_valid()

    assert serializer.errors.get("non_field_errors") is None
    assert len(serializer.errors.get("slot")) == 1
    assert serializer.errors.get("user") is None
    assert serializer.errors["slot"][0] == "Limit of signed up workers reached."


@pytest.mark.django_db
def test_sign_up_only_once(rf, syto_datetime, syto_user, syto_slot):
    dt = partial(syto_datetime, **{"year": 2021, "month": 1, "day": 1})
    slot = syto_slot(day=dt().date(), stationary_workers_limit=99)
    user = syto_user()

    AvailabilityPeriod.objects.create(
        slot=slot, start=dt(hour=14), end=dt(hour=22), user=user
    )

    request = rf.post("foo")
    request.user = user

    data = {
        "slot": slot.day,
        "start": "2021-01-01 06:00",
        "end": "2021-01-01 14:00",
    }

    serializer = AvailabilityPeriodSerializer(data=data, context={"request": request})
    serializer.is_valid()

    assert serializer.errors.get("non_field_errors") is None
    assert serializer.errors.get("slot") is None
    assert len(serializer.errors.get("user")) == 1
    assert serializer.errors["user"][0] == "Worker can sign up only once for a day."
