from datetime import date

import pytest

from syto_api.serializers import UserSerializer


@pytest.mark.django_db
def test_valid_data_new_stationary_worker():
    data = {
        "email": "foo@bar.baz",
        "password": "FooBarBaz123",
        "first_name": "Foo",
        "last_name": "Bar",
        "is_new": True,
        "date_of_birth": date.today(),
        "evidence_number": "11111111111",  # PESEL
    }

    serializer = UserSerializer(data=data)

    serializer.is_valid()
    serializer.save()

    assert set(serializer.data["groups"]) == {"new_employee", "stationary_worker"}


@pytest.mark.django_db
def test_valid_data_old_stationary_worker():
    data = {
        "email": "foo@bar.baz",
        "password": "FooBarBaz123",
        "first_name": "Foo",
        "last_name": "Bar",
    }

    serializer = UserSerializer(data=data)

    serializer.is_valid()
    serializer.save()

    assert set(serializer.data["groups"]) == {"stationary_worker"}


@pytest.mark.django_db
def test_valid_data_new_cottage_worker():
    data = {
        "email": "foo@bar.baz",
        "password": "FooBarBaz123",
        "first_name": "Foo",
        "last_name": "Bar",
        "is_new": True,
        "is_cottage": True,
        "date_of_birth": date.today(),
        "evidence_number": "11111111111",  # PESEL
    }

    serializer = UserSerializer(data=data)

    serializer.is_valid()
    serializer.save()

    assert set(serializer.data["groups"]) == {"new_employee", "cottage_worker"}


@pytest.mark.django_db
def test_valid_data_old_cottage_employee():
    data = {
        "email": "foo@bar.baz",
        "password": "FooBarBaz123",
        "first_name": "Foo",
        "last_name": "Bar",
        "is_cottage": True,
    }

    serializer = UserSerializer(data=data)

    serializer.is_valid()
    serializer.save()

    assert set(serializer.data["groups"]) == {"cottage_worker"}


@pytest.mark.django_db
def test_invalid_data_new_employee():
    data = {
        "email": "foo@bar.baz",
        "password": "FooBarBaz123",
        "first_name": "Foo",
        "last_name": "Bar",
        "is_new": True,
        "evidence_number": "11111111111",  # PESEL
    }

    serializer = UserSerializer(data=data)

    assert not serializer.is_valid()


@pytest.mark.django_db
def test_invalid_data_old_employee():
    data = {
        "email": "foo@bar.baz",
        "password": "FooBarBaz123",
        "first_name": "Foo",
    }

    serializer = UserSerializer(data=data)

    assert not serializer.is_valid()
