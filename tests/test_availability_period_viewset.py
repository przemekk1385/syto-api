"""
TODO:
- tests for failed update
"""

import json

import pytest
from django.shortcuts import reverse

from syto_api.models import AvailabilityPeriod


@pytest.mark.django_db
def test_create_ok(api_client, syto_user, syto_slot):
    user = syto_user(groups=["stationary_worker"])
    api_client.force_authenticate(user)

    payload = {
        "slot": syto_slot(stationary_workers_limit=1).day,
        "start": "6:00",
        "end": "14:00",
    }

    response = api_client.post(reverse("syto_api:availability-period-list"), payload)

    assert response.status_code == 201
    assert not set(payload.keys()).difference(response.data.keys())


@pytest.mark.django_db
def test_create_failed(api_client, syto_user, syto_slot):
    user = syto_user(groups=["cottage_worker"])
    api_client.force_authenticate(user)

    payload = {
        "slot": syto_slot(stationary_workers_limit=1).day,
        "start": "6:00",
        "end": "14:00",
    }

    response = api_client.post(reverse("syto_api:availability-period-list"), payload)

    assert response.status_code == 403


@pytest.mark.django_db
def test_retrieve_ok(api_client, syto_user, syto_slot):
    user = syto_user(groups=["stationary_worker"])
    api_client.force_authenticate(user)

    availability = AvailabilityPeriod.objects.create(
        slot=syto_slot(stationary_workers_limit=1),
        start="6:00",
        end="14:00",
        user=user,
    )

    response = api_client.get(
        reverse("syto_api:availability-period-detail", args=[availability.id])
    )

    assert response.status_code == 200
    assert response.data["start"] == "06:00"
    assert response.data["end"] == "14:00"


@pytest.mark.django_db
def test_update_ok(api_client, syto_user, syto_slot):
    user = syto_user(groups=["stationary_worker"])
    api_client.force_authenticate(user)

    availability = AvailabilityPeriod.objects.create(
        slot=syto_slot(stationary_workers_limit=1),
        start="6:00",
        end="14:00",
        user=user,
    )

    response = api_client.patch(
        reverse("syto_api:availability-period-detail", args=[availability.id]),
        data=json.dumps({"end": "12:00"}),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.data["start"] == "06:00"
    assert response.data["end"] == "12:00"


@pytest.mark.django_db
def test_update_failed(api_client, syto_user, syto_slot):
    user1 = syto_user("foo1@bar.baz", groups=["stationary_worker"])
    user2 = syto_user("foo2@bar.baz", groups=["stationary_worker"])
    api_client.force_authenticate(user1)

    availability = AvailabilityPeriod.objects.create(
        slot=syto_slot(stationary_workers_limit=1),
        start="6:00",
        end="14:00",
        user=user2,
    )

    response = api_client.patch(
        reverse("syto_api:availability-period-detail", args=[availability.id]),
        data=json.dumps({"end": "12:00"}),
        content_type="application/json",
    )

    assert response.status_code == 403
