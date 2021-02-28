from rest_framework import serializers
from rest_framework.serializers import ValidationError

from syto_api.models import User


class UserSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)

    first_name = serializers.CharField()
    last_name = serializers.CharField()

    evidence_number = serializers.CharField(required=False)
    date_of_birth = serializers.DateField(required=False)

    # extra field that doesn't go to db
    is_new = serializers.BooleanField(required=False)

    class Meta:
        model = User
        fields = "__all__"

    def validate(self, attrs):
        if attrs.get("is_new"):
            errors = {}

            evidence_number = self.initial_data.get("evidence_number")
            if not evidence_number:
                errors[
                    "evidence_number"
                ] = "This field is required when 'is_new' flag is True"

            date_of_birth = self.initial_data.get("date_of_birth")
            if not date_of_birth:
                errors[
                    "date_of_birth"
                ] = "This field is required when 'is_new' flag is True"

            if errors:
                raise ValidationError(errors)

        return attrs
