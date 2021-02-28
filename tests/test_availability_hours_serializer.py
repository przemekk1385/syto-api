import pytest
from django.utils import timezone

from syto_api.serializers import AvailabilityHoursSerializer


@pytest.mark.django_db
def test_valid_data(syto_user):
    data = {
        "day": timezone.datetime(2021, 1, 1, 6, 0, 0).date(),
        "hours": 8,
        "user": syto_user("foo@bar.baz").id,
    }

    serializer = AvailabilityHoursSerializer(data=data)

    assert serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_invalid_data(syto_user):
    data = {
        "day": timezone.datetime(2021, 1, 1, 6, 0, 0).date(),
        "hours": 25,
        "user": syto_user("foo@bar.baz").id,
    }

    serializer = AvailabilityHoursSerializer(data=data)

    assert not serializer.is_valid()
