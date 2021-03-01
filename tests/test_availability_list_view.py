from datetime import date, timedelta

import pytest
from dateutil import tz
from django.conf import settings
from django.shortcuts import reverse
from django.utils import timezone

from syto_api.models import AvailabilityHours, AvailabilityPeriod
from syto_api.views import AvailabilityView

tz = tz.gettz(settings.TIME_ZONE)
TODAY = date.today()
START = timezone.datetime(TODAY.year, TODAY.month, TODAY.day, 6, 0, 0, tzinfo=tz)


@pytest.mark.django_db
def test_get(rf, syto_user):
    users = [syto_user("foo1@bar.baz"), syto_user("foo2@bar.baz")]
    for i in range(10):
        AvailabilityHours.objects.create(
            day=TODAY - timedelta(days=i), hours=8, user=users[0]
        )
        AvailabilityHours.objects.create(
            day=TODAY - timedelta(days=i), hours=8, user=users[1]
        )

        start = START - timedelta(days=i)
        end = start + timedelta(hours=8)

        AvailabilityPeriod.objects.create(start=start, end=end, user=users[0])
        AvailabilityPeriod.objects.create(start=start, end=end, user=users[1])

    request = rf.get(reverse("syto_api:availability-list"))

    view = AvailabilityView.as_view()
    response = view(request)

    assert response.status_code == 200
    assert set(response.data.keys()) == {"hours", "categories"}


@pytest.mark.django_db
def test_post_availability_hours(rf, syto_user):
    payload = {
        "day": TODAY,
        "hours": 8,
        "user": syto_user("foo@bar.baz").id,
    }

    request = rf.post(reverse("syto_api:availability-list"), payload)

    view = AvailabilityView.as_view()
    response = view(request)

    assert response.status_code == 201
    assert not set(payload.keys()).difference(response.data.keys())


@pytest.mark.django_db
def test_post_availability_period(rf, syto_user):
    start = START
    end = start + timedelta(hours=8)
    payload = {
        "start": start,
        "end": end,
        "user": syto_user("foo@bar.baz").id,
    }

    request = rf.post(reverse("syto_api:availability-list"), payload)

    view = AvailabilityView.as_view()
    response = view(request)

    assert response.status_code == 201
    assert not set(payload.keys()).difference(response.data.keys())


def test_post_unhandled_payload(rf):
    payload = {
        "foo": "foo",
        "bar": "bar",
    }

    request = rf.post(reverse("syto_api:availability-list"), payload)

    view = AvailabilityView.as_view()
    response = view(request)

    assert response.status_code == 400
