import pytest

from syto_api.models import AvailabilityPeriod
from syto_api.serializers import AvailabilityPeriodSerializer


@pytest.mark.django_db
def test_valid_data(syto_user, syto_slot):
    data = {
        "slot": syto_slot(stationary_workers_limit=1).day,
        "start": "6:00",
        "end": "14:00",
        "user": syto_user().id,
    }

    serializer = AvailabilityPeriodSerializer(data=data)

    assert serializer.is_valid()


@pytest.mark.parametrize(
    ("start", "end", "error_message"),
    [
        ("14:00", "6:00", "End must be after start."),
        ("6:00", "23:00", "Maximum allowed number of hours is 16."),
        ("6:00", "13:30", "Only full number of hours is allowed."),
    ],
)
@pytest.mark.django_db
def test_non_field_errors(start, end, error_message, syto_user, syto_slot):
    data = {
        "slot": syto_slot(stationary_workers_limit=1).day,
        "start": start,
        "end": end,
        "user": syto_user().id,
    }

    serializer = AvailabilityPeriodSerializer(data=data)
    serializer.is_valid()

    assert len(serializer.errors.get("non_field_errors")) == 1
    assert serializer.errors.get("slot") is None
    assert serializer.errors.get("user") is None
    assert serializer.errors["non_field_errors"][0] == error_message


@pytest.mark.django_db
def test_non_open_day(syto_user, syto_slot):
    data = {
        "slot": syto_slot().day,
        "start": "6:00",
        "end": "14:00",
        "user": syto_user().id,
    }

    serializer = AvailabilityPeriodSerializer(data=data)
    serializer.is_valid()

    assert serializer.errors.get("non_field_errors") is None
    assert len(serializer.errors.get("slot")) == 1
    assert serializer.errors.get("user") is None
    assert serializer.errors["slot"][0] == "Cannot sign up for a non-open day."


@pytest.mark.django_db
def test_workers_limit_reached(syto_user, syto_slot):
    slot = syto_slot(stationary_workers_limit=1)
    user1 = syto_user("foo1@bar.baz")
    user2 = syto_user("foo2@bar.baz")
    AvailabilityPeriod.objects.create(slot=slot, start="6:00", end="14:00", user=user1)

    data = {
        "slot": slot.day,
        "start": "6:00",
        "end": "14:00",
        "user": user2.id,
    }

    serializer = AvailabilityPeriodSerializer(data=data)
    serializer.is_valid()

    assert serializer.errors.get("non_field_errors") is None
    assert len(serializer.errors.get("slot")) == 1
    assert serializer.errors.get("user") is None
    assert serializer.errors["slot"][0] == "Limit of signed up workers reached."


@pytest.mark.django_db
def test_sign_up_only_once(syto_user, syto_slot):
    slot = syto_slot(stationary_workers_limit=99)
    user = syto_user()
    AvailabilityPeriod.objects.create(slot=slot, start="14:00", end="22:00", user=user)

    data = {
        "slot": slot.day,
        "start": "6:00",
        "end": "14:00",
        "user": user.id,
    }

    serializer = AvailabilityPeriodSerializer(data=data)
    serializer.is_valid()

    assert serializer.errors.get("non_field_errors") is None
    assert serializer.errors.get("slot") is None
    assert len(serializer.errors.get("user")) == 1
    assert serializer.errors["user"][0] == "Worker can sign up only once for a day."
