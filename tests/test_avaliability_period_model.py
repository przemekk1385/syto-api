from datetime import timedelta

import pytest
from django.utils import timezone

from syto_api.models import AvailabilityPeriod

CURRENT_TIME = timezone.now()


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
