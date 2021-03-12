from rest_access_policy import AccessPolicy
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


class AvailabilityHoursAccessPolicy(AccessPolicy):

    statements = [
        {"action": ["*"], "principal": ["group:cottage_worker"], "effect": "allow"}
    ]


class AvailabilityHoursViewSet(viewsets.ModelViewSet):

    permission_classes = [AvailabilityHoursAccessPolicy]
    serializer_class = AvailabilityHoursSerializer
    queryset = AvailabilityHours.objects.all()


class AvailabilityPeriodAccessPolicy(AccessPolicy):

    statements = [
        {"action": ["*"], "principal": ["group:stationary_worker"], "effect": "allow"}
    ]


class AvailabilityPeriodViewSet(viewsets.ModelViewSet):

    permission_classes = [AvailabilityPeriodAccessPolicy]
    serializer_class = AvailabilityPeriodSerializer
    queryset = AvailabilityPeriod.objects.all()
