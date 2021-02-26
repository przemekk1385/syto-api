import pendulum
import pytest
from django.utils import timezone

from syto_api.serializers import AvailabilityPeriodSerializer

CURRENT_TIME = pendulum.instance(timezone.now())


@pytest.mark.django_db
def test_valid_data(syto_user):
    data = {
        "start": CURRENT_TIME,
        "end": CURRENT_TIME.add(hours=8),
        "user": syto_user("foo@bar.baz").id,
    }

    serializer = AvailabilityPeriodSerializer(data=data)

    assert serializer.is_valid()


@pytest.mark.django_db
def test_invalid_data(syto_user):
    data = {
        "start": CURRENT_TIME,
        "end": CURRENT_TIME.add(hours=24),
        "user": syto_user("foo@bar.baz").id,
    }

    serializer = AvailabilityPeriodSerializer(data=data)

    assert not serializer.is_valid()
