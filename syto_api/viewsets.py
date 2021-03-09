from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import AvailabilityHours, AvailabilityPeriod, User
from .serializers import (
    AvailabilityHoursSerializer,
    AvailabilityPeriodSerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):

    serializer_class = UserSerializer
    queryset = User.objects.all()

    @action(detail=True, url_path="toggle_is_active", methods=["GET"])
    def toggle_is_active(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = not instance.is_active
        instance.save()

        return Response({"is_active": instance.is_active}, status=status.HTTP_200_OK)


class AvailabilityHoursViewSet(viewsets.ModelViewSet):

    serializer_class = AvailabilityHoursSerializer
    queryset = AvailabilityHours.objects.all()


class AvailabilityPeriodViewSet(viewsets.ModelViewSet):

    serializer_class = AvailabilityPeriodSerializer
    queryset = AvailabilityPeriod.objects.all()
