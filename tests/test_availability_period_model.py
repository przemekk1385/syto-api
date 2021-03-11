from datetime import date, timedelta

import pytest
from dateutil import tz
from django.conf import settings
from django.utils import timezone

from syto_api.models import AvailabilityPeriod

tz = tz.gettz(settings.TIME_ZONE)
TODAY = date.today()
START = timezone.datetime(TODAY.year, TODAY.month, TODAY.day, 6, 0, 0, tzinfo=tz)


@pytest.mark.django_db
def test_query_set(syto_user, syto_slot):
    start = START
    end = start + timedelta(hours=8)
    AvailabilityPeriod.objects.create(
        slot=syto_slot(),
        start=start.time(),
        end=end.time(),
        user=syto_user("foo@bar.baz"),
    )

    assert (
        AvailabilityPeriod.objects.with_timedelta().first().timedelta.seconds
        == 8 * 3600
    )
