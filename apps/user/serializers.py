from rest_framework import serializers
from .models import User
import re
from django.utils.translation import gettext_lazy as _
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework_simplejwt.tokens import RefreshToken, TokenError, AccessToken


class RegisterSerializers(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=225)
    phone_number = PhoneNumberField(required=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['full_name', 'phone_number', 'password']

    def validate_phone_number(self, value):
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


class LoginSerializers(serializers.Serializer):
    phone_number = PhoneNumberField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        password = attrs.get('password')
        phone_number = attrs.get('phone_number')
        user_qs = User.objects.filter(phone_number=phone_number)

        if not user_qs.exists():
            raise serializers.ValidationError({'message': _('User not found')})

        user = user_qs.first()
        if not user.check_password(password):
            raise serializers.ValidationError({'message': _('The password is incorrect')})

        attrs['user'] = user
        return attrs

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError as e:
            raise serializers.ValidationError({"refresh": f"Token is invalid or expired. Details: {str(e)}"})


