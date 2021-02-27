from rest_framework import serializers
from rest_framework.serializers import ValidationError

from syto_api.models import User


class UserSerializer(serializers.ModelSerializer):
    evidence_number = serializers.IntegerField(required=False)
    birth_date = serializers.DateField(required=False)

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "is_new",
            "evidence_number",
            "birth_date",
        ]

    def validate(self, data):
        if data["is_new"]:
            data["evidence_number"] = self.initial_data["evidence_number"]
            data["birth_date"] = self.initial_data["birth_date"]
            return data
