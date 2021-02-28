from datetime import timedelta

import pytest
from dateutil import tz
from django.conf import settings
from django.utils import timezone

from syto_api.models import AvailabilityPeriod

tz = tz.gettz(settings.TIME_ZONE)
CURRENT_TIME = timezone.datetime(2021, 1, 1, 6, 0, 0, tzinfo=tz)


@pytest.mark.django_db
def test_query_set(syto_user):
    AvailabilityPeriod.objects.create(
        start=CURRENT_TIME,
        end=CURRENT_TIME + timedelta(hours=8),
        user=syto_user("foo@bar.baz"),
    )

    assert (
        AvailabilityPeriod.objects.with_timedelta().first().timedelta.seconds
        == 8 * 3600
    )
