from datetime import date

import pytest

from syto_api.serializers import SlotCreateSerializer, SlotSerializer

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
    ],
)
@pytest.mark.django_db
def test_valid_data(data):
    serializer = SlotSerializer(data=data)
    create_serializer = SlotCreateSerializer(data=data)

    assert serializer.is_valid()
    assert create_serializer.is_valid()


@pytest.mark.django_db
def test_invalid_data():
    data = {
        "day": TODAY,
    }

    serializer = SlotSerializer(data=data)
    create_serializer = SlotCreateSerializer(data=data)

    assert not serializer.is_valid()
    assert not create_serializer.is_valid()
