from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import AvailabilityHours, AvailabilityPeriod


class AvailabilityHoursSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)

    class Meta:

        fields = "__all__"
        model = AvailabilityHours

    @staticmethod
    def validate_hours(val):
        if val > 24:
            raise ValidationError("maximum allowed number of hours is 24")

        return val


class AvailabilityPeriodSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)

    class Meta:

        fields = "__all__"
        model = AvailabilityPeriod

    def validate(self, attrs):
        if attrs["start"].date() != attrs["end"].date():
            raise ValidationError("start and end must by at the same day")

        if (attrs["end"] - attrs["start"]).seconds < 3600:
            raise ValidationError("end must be at least 1 hour after start")

        return attrs
