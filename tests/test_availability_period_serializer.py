from datetime import timedelta

import pytest
from dateutil import tz
from django.conf import settings
from django.utils import timezone

from syto_api.serializers import AvailabilityPeriodSerializer

tz = tz.gettz(settings.TIME_ZONE)
CURRENT_TIME = timezone.datetime(2021, 1, 1, 6, 0, 0, tzinfo=tz)


@pytest.mark.django_db
def test_valid_data(syto_user):
    data = {
        "start": CURRENT_TIME,
        "end": CURRENT_TIME + timedelta(hours=8),
        "user": syto_user("foo@bar.baz").id,
    }

    serializer = AvailabilityPeriodSerializer(data=data)

    assert serializer.is_valid()


@pytest.mark.django_db
def test_invalid_data(syto_user):
    data = {
        "start": CURRENT_TIME,
        "end": CURRENT_TIME + timedelta(hours=24),
        "user": syto_user("foo@bar.baz").id,
    }

    serializer = AvailabilityPeriodSerializer(data=data)

    assert not serializer.is_valid()
