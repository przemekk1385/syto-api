from rest_framework import viewsets

from .models import AvailabilityHours, AvailabilityPeriod, User
from .serializers import (
    AvailabilityHoursSerializer,
    AvailabilityPeriodSerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):

    serializer_class = UserSerializer
    queryset = User.objects.all()


class AvailabilityHoursViewSet(viewsets.ModelViewSet):

    serializer_class = AvailabilityHoursSerializer
    queryset = AvailabilityHours.objects.all()


class AvailabilityPeriodViewSet(viewsets.ModelViewSet):

    serializer_class = AvailabilityPeriodSerializer
    queryset = AvailabilityPeriod.objects.all()
