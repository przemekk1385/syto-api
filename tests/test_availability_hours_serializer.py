from datetime import date

import pytest

from syto_api.serializers import AvailabilityHoursSerializer

TODAY = date.today()


@pytest.mark.django_db
def test_valid_data(syto_user):
    data = {
        "day": TODAY,
        "hours": 8,
        "user": syto_user("foo@bar.baz").id,
    }

    serializer = AvailabilityHoursSerializer(data=data)

    assert serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_exceeded_maximum_number_of_hours(syto_user):
    data = {
        "day": TODAY,
        "hours": 17,
        "user": syto_user("foo@bar.baz").id,
    }

    serializer = AvailabilityHoursSerializer(data=data)
    serializer.is_valid()

    assert len(serializer.errors) == 1
    assert serializer.errors["hours"][0] == "Maximum allowed number of hours is 16."
