import pytest

from syto_api.models import User


@pytest.mark.django_db
def test_create_user():

    user = User.objects.create_user(email="foo@bar.baz", password="foo")

    assert user.email == "foo@bar.baz"
    assert user.password != "foo"
    assert not user.is_active
    assert not user.is_staff
    assert not user.is_superuser


@pytest.mark.django_db
def test_create_superuser():
    user = User.objects.create_superuser(email="foo@bar.baz", password="foo")

    assert user.email == "foo@bar.baz"
    assert user.password != "foo"
    assert user.is_active
    assert user.is_staff
    assert user.is_superuser
