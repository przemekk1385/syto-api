from functools import partial

import pytest

from syto_api.models import AvailabilityPeriod


@pytest.mark.django_db
def test_query_set(syto_datetime, syto_user, syto_slot):
    dt = partial(syto_datetime, **{"year": 2021, "month": 1, "day": 1})

    AvailabilityPeriod.objects.create(
        slot=syto_slot(day=dt().date()),
        start=dt(hour=6),
        end=dt(hour=14),
        user=syto_user(),
    )

    assert (
        AvailabilityPeriod.objects.with_timedelta().first().timedelta.seconds
        == 8 * 3600
    )
