import pytest

from syto_api.serializers import AvailabilityHoursSerializer


@pytest.mark.django_db
def test_valid_data(syto_user, syto_slot):
    data = {
        "slot": syto_slot().day,
        "hours": 8,
        "user": syto_user().id,
    }

    serializer = AvailabilityHoursSerializer(data=data)

    assert serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_exceeded_maximum_number_of_hours(syto_user, syto_slot):
    data = {
        "slot": syto_slot().day,
        "hours": 17,
        "user": syto_user().id,
    }

    serializer = AvailabilityHoursSerializer(data=data)
    serializer.is_valid()

    assert len(serializer.errors) == 1
    assert serializer.errors["hours"][0] == "Maximum allowed number of hours is 16."
