from rest_framework import serializers
from .models import User
import re
from django.utils.translation import gettext_lazy as _


class RegisterSerializers(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=225)
    phone_number = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['full_name', 'phone_number', 'password']

    def validate_phone_number(self, value):
        pattern = r"^\+998\d{9}$"
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                {
                    "message": [_("Phone number format should be +998 followed by 9 digits.")]
                }
            )
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                {
                    "message": [_("This phone number is already registered")]
                }
            )
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            full_name=validated_data["full_name"],
            phone_number=validated_data["phone_number"],
            password=validated_data["password"]
        )
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["tokens"] = instance.tokens()
        return data


