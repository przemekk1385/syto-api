import pytest

from syto_api.models import AvailabilityPeriod


@pytest.mark.django_db
def test_query_set(syto_user, syto_slot):
    AvailabilityPeriod.objects.create(
        slot=syto_slot(),
        start="6:00",
        end="14:00",
        user=syto_user(),
    )

    assert (
        AvailabilityPeriod.objects.with_timedelta().first().timedelta.seconds
        == 8 * 3600
    )
