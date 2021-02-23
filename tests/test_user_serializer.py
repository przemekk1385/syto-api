from datetime import date

import pytest

from syto_api.serializers import UserSerializer


@pytest.mark.django_db
def test_valid_data_new_employee():
    data = {
        "first_name": "foo",
        "last_name": "bar",
        "email": "foo@bar",
        "is_new": True,
        "evidence_number": 123456,  # PESEL
        "birth_date": date.today(),
    }

    serializer = UserSerializer(data=data)

    assert serializer.is_valid()


@pytest.mark.django_db
def test_valid_data_old_employee():
    data = {
        "first_name": "foo",
        "last_name": "bar",
        "email": "foo@bar",
        "is_new": False,
    }

    serializer = UserSerializer(data=data)

    assert serializer.is_valid()


@pytest.mark.django_db
def test_invalid_data_new_employee():
    data = {
        "first_name": "foo",
        "last_name": "bar",
        "email": "foo@bar",
        "is_new": True,
    }

    serializer = UserSerializer(data=data)

    assert not serializer.is_valid()


@pytest.mark.django_db
def test_invalid_data_old_employee():
    data = {
        "email": "foo@bar",
        "is_new": False,
    }

    serializer = UserSerializer(data=data)

    assert not serializer.is_valid()
