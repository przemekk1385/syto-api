import json

import pytest
from django.shortcuts import reverse

from syto_api.models import AvailabilityHours


@pytest.mark.django_db
def test_create_ok(api_client, syto_user, syto_slot):
    user = syto_user(groups=["cottage_worker"])
    api_client.force_authenticate(user)

    payload = {
        "slot": syto_slot(is_open_for_cottage_workers=True).day,
        "hours": 8,
    }

    response = api_client.post(reverse("syto_api:availability-hours-list"), payload)

    assert response.status_code == 201
    assert not set(payload.keys()).difference(response.data.keys())


@pytest.mark.django_db
def test_create_failed(api_client, syto_user, syto_slot):
    user = syto_user(groups=["stationary_worker"])
    api_client.force_authenticate(user)

    payload = {
        "slot": syto_slot(is_open_for_cottage_workers=True).day,
        "hours": 8,
    }

    response = api_client.post(reverse("syto_api:availability-hours-list"), payload)

    assert response.status_code == 403


@pytest.mark.django_db
def test_retrieve_ok(api_client, syto_user, syto_slot):
    user = syto_user(groups=["cottage_worker"])
    api_client.force_authenticate(user)

    availability = AvailabilityHours.objects.create(
        slot=syto_slot(is_open_for_cottage_workers=True),
        hours=8,
        user=user,
    )

    response = api_client.get(
        reverse("syto_api:availability-hours-detail", args=[availability.id])
    )

    assert response.status_code == 200
    assert response.data["hours"] == 8


@pytest.mark.django_db
def test_update_ok(api_client, syto_user, syto_slot):
    user = syto_user(groups=["cottage_worker"])
    api_client.force_authenticate(user)

    availability = AvailabilityHours.objects.create(
        slot=syto_slot(is_open_for_cottage_workers=True),
        hours=8,
        user=user,
    )

    response = api_client.patch(
        reverse("syto_api:availability-hours-detail", args=[availability.id]),
        data=json.dumps({"hours": 10}),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.data["hours"] == 10


@pytest.mark.django_db
def test_update_failed(api_client, syto_user, syto_slot):
    user1 = syto_user("foo1@bar.baz", groups=["cottage_worker"])
    user2 = syto_user("foo2@bar.baz", groups=["cottage_worker"])
    api_client.force_authenticate(user1)

    availability = AvailabilityHours.objects.create(
        slot=syto_slot(is_open_for_cottage_workers=True),
        hours=8,
        user=user2,
    )

    response = api_client.patch(
        reverse("syto_api:availability-hours-detail", args=[availability.id]),
        data=json.dumps({"hours": 10}),
        content_type="application/json",
    )

    assert response.status_code == 403
