from datetime import date

import pytest

from syto_api.serializers import SlotSerializer

TODAY = date.today()


@pytest.mark.parametrize(
    ("data",),
    [
        (
            {
                "day": TODAY,
                "stationary_workers_limit": 99,
                "is_open_for_cottage_workers": True,
            },
        ),
        ({"day": TODAY, "stationary_workers_limit": 99},),
        ({"day": TODAY, "is_open_for_cottage_workers": True},),
        ({"day": TODAY},),
    ],
)
@pytest.mark.django_db
def test_valid_data(data):
    serializer = SlotSerializer(data=data)

    assert serializer.is_valid()
