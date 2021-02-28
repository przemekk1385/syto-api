from rest_framework import serializers
from rest_framework.serializers import ValidationError

from .models import AvailabilityHours, AvailabilityPeriod


class AvailabilityHoursSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)

    class Meta:

        fields = "__all__"
        model = AvailabilityHours

    @staticmethod
    def validate_hours(val):
        if val > 24:
            raise ValidationError({"hours": "maximum allowed number of hours is 24"})

        return val


class AvailabilityPeriodSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)

    class Meta:

        fields = "__all__"
        model = AvailabilityPeriod

    def validate(self, attrs):
        errors = {}

        if attrs["start"].date() != attrs["end"].date():
            errors["non_field_errors"] = "start and end must by at the same day"

        if (attrs["end"] - attrs["start"]).seconds < 3600:
            errors["end"] = "end must be at least 1 hour after start"

        if errors:
            raise ValidationError(errors)

        return attrs
