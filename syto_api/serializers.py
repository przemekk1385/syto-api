from rest_framework import serializers

from .models import AvailabilityHours, AvailabilityPeriod


class AvailabilityHoursSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)

    class Meta:

        fields = "__all__"
        model = AvailabilityHours


class AvailabilityPeriodSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)

    class Meta:

        fields = "__all__"
        model = AvailabilityPeriod
