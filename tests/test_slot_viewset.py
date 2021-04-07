import json
from datetime import date
from functools import partial

import pytest
from django.shortcuts import reverse

from syto_api.models import AvailabilityHours, AvailabilityPeriod, Slot

TODAY = date.today()


@pytest.mark.parametrize(
    ("groups", "results_count"),
    [
        (["cottage_worker"], 10),
        (["stationary_worker"], 10),
        (["foreman"], 0),
    ],
)
@pytest.mark.django_db
def test_list(groups, results_count, syto_datetime, api_client, syto_user):
    dt = partial(syto_datetime, **{"year": 2021, "month": 1, "day": 1})
    for i in range(5):
        Slot.objects.create(
            day=dt(timedelta_days=-i).date(), stationary_workers_limit=5
        )
    for i in range(5, 10):
        Slot.objects.create(
            day=dt(timedelta_days=-i).date(),
            is_open_for_cottage_workers=True,
        )
    for i in range(10, 15):
        Slot.objects.create(
            day=dt(timedelta_days=-i).date(),
            stationary_workers_limit=5,
            is_open_for_cottage_workers=True,
        )

    user = syto_user(groups=groups)
    api_client.force_authenticate(user)

    response = api_client.get(reverse("syto_api:slot-list"))

    assert response.status_code == 200
    assert len(response.data) == results_count


@pytest.mark.django_db
def test_create_ok(api_client, syto_user):
    user = syto_user(groups=["foreman"])
    api_client.force_authenticate(user)

    payload = {
        "day": TODAY,
        "stationary_workers_limit": 99,
        "is_open_for_cottage_workers": True,
    }

    response = api_client.post(reverse("syto_api:slot-list"), payload)

    assert response.status_code == 201
    assert not set(payload.keys()).difference(response.data.keys())


@pytest.mark.parametrize(
    ("groups",),
    [
        (["stationary_worker"],),
        (["cottage_worker"],),
        (["new_employee"],),
    ],
)
@pytest.mark.django_db
def test_create_failed(groups, api_client, syto_user):
    user = syto_user(groups=groups)
    api_client.force_authenticate(user)

    payload = {
        "day": TODAY,
        "stationary_workers_limit": 99,
        "is_open_for_cottage_workers": True,
    }

    response = api_client.post(reverse("syto_api:slot-list"), payload)

    assert response.status_code == 403


@pytest.mark.django_db
def test_retrieve_ok(api_client, syto_user):
    user = syto_user(groups=["foreman"])
    api_client.force_authenticate(user)

    slot = Slot.objects.create(
        day=TODAY,
        stationary_workers_limit=99,
        is_open_for_cottage_workers=True,
    )

    response = api_client.get(reverse("syto_api:slot-detail", args=[slot.day]))

    assert response.status_code == 200
    assert response.data["stationary_workers_limit"] == 99


@pytest.mark.django_db
def test_update_ok(api_client, syto_user):
    user = syto_user(groups=["foreman"])
    api_client.force_authenticate(user)

    slot = Slot.objects.create(
        day=TODAY,
        stationary_workers_limit=999,
        is_open_for_cottage_workers=True,
    )

    response = api_client.patch(
        reverse("syto_api:slot-detail", args=[slot.day]),
        data=json.dumps({"stationary_workers_limit": 99}),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.data["stationary_workers_limit"] == 99


@pytest.mark.django_db
def test_update_workers_related_fields_ok(api_client, syto_datetime, syto_user):
    dt = partial(syto_datetime, **{"year": 2021, "month": 1, "day": 1})
    user = syto_user(groups=["foreman"])
    api_client.force_authenticate(user)

    slot = Slot.objects.create(
        day=dt().date(),
        stationary_workers_limit=5,
        is_open_for_cottage_workers=True,
    )

    for i in range(5):
        AvailabilityHours.objects.create(
            slot=slot,
            hours=8,
            user=syto_user(f"foo2{i}@bar.baz", groups=["cottage_worker"]),
        )
        AvailabilityPeriod.objects.create(
            slot=slot,
            start=dt(hour=6),
            end=dt(hour=14),
            user=syto_user(f"foo1{i}@bar.baz", groups=["stationary_worker"]),
        )

    response = api_client.patch(
        reverse("syto_api:slot-detail", args=[slot.day]),
        data=json.dumps(
            {"is_open_for_cottage_workers": False, "stationary_workers_limit": 1}
        ),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert not AvailabilityHours.objects.filter(slot=slot).exists()
    assert AvailabilityPeriod.objects.filter(slot=slot).count() == 1


@pytest.mark.parametrize(
    ("groups",),
    [
        (["stationary_worker"],),
        (["cottage_worker"],),
        (["new_employee"],),
    ],
)
@pytest.mark.django_db
def test_update_failed(groups, api_client, syto_user):
    user = syto_user(groups=[groups])
    api_client.force_authenticate(user)

    slot = Slot.objects.create(
        day=TODAY,
        stationary_workers_limit=999,
        is_open_for_cottage_workers=True,
    )

    response = api_client.patch(
        reverse("syto_api:slot-detail", args=[slot.day]),
        data=json.dumps({"stationary_workers_limit": 99}),
        content_type="application/json",
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    ("groups", "status"),
    [
        (["cottage_worker"], 403),
        (["stationary_worker"], 403),
        (["foreman"], 200),
    ],
)
@pytest.mark.django_db
def test_all(groups, status, api_client, syto_datetime, syto_user):
    dt = partial(syto_datetime, **{"year": 2021, "month": 1, "day": 1})
    for i in range(5):
        Slot.objects.create(
            day=dt(timedelta_days=-i).date(),
            stationary_workers_limit=5,
            is_open_for_cottage_workers=True,
        )

    user = syto_user(groups=groups)
    api_client.force_authenticate(user)

    response = api_client.get(reverse("syto_api:slot-all"))

    assert response.status_code == status
