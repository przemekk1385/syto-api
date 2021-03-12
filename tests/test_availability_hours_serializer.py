import pytest

from syto_api.models import AvailabilityHours
from syto_api.serializers import AvailabilityHoursSerializer


@pytest.mark.django_db
def test_valid_data(rf, syto_user, syto_slot):
    request = rf.post("foo")
    request.user = syto_user()

    data = {
        "slot": syto_slot(is_open_for_cottage_workers=True).day,
        "hours": 8,
    }

    serializer = AvailabilityHoursSerializer(data=data, context={"request": request})

    assert serializer.is_valid()


@pytest.mark.django_db
def test_exceeded_maximum_number_of_hours(rf, syto_user, syto_slot):
    request = rf.post("foo")
    request.user = syto_user()

    data = {
        "slot": syto_slot(is_open_for_cottage_workers=True).day,
        "hours": 17,
    }

    serializer = AvailabilityHoursSerializer(data=data, context={"request": request})
    serializer.is_valid()

    assert len(serializer.errors) == 1
    assert serializer.errors["hours"][0] == "Maximum allowed number of hours is 16."


@pytest.mark.django_db
def test_non_open_day(rf, syto_user, syto_slot):
    request = rf.post("foo")
    request.user = syto_user()

    data = {
        "slot": syto_slot().day,
        "hours": 8,
    }

    serializer = AvailabilityHoursSerializer(data=data, context={"request": request})
    serializer.is_valid()

    assert len(serializer.errors) == 1
    assert serializer.errors["slot"][0] == "Cannot sign up for a non-open day."


@pytest.mark.django_db
def test_sign_up_only_once(rf, syto_user, syto_slot):
    slot = syto_slot(is_open_for_cottage_workers=True)
    user = syto_user()
    AvailabilityHours.objects.create(slot=slot, hours=8, user=user)

    request = rf.post("foo")
    request.user = user

    data = {
        "slot": slot.day,
        "hours": 8,
    }

    serializer = AvailabilityHoursSerializer(data=data, context={"request": request})
    serializer.is_valid()

    assert len(serializer.errors) == 1
    assert serializer.errors["user"][0] == "Worker can sign up only once for a day."
