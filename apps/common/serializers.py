from rest_framework import serializers
from . import models
from apps.user.models import User
from django.utils.translation import gettext_lazy as _

class BaseStadiumCreateSerializer(serializers.ModelSerializer):
    manager = serializers.PrimaryKeyRelatedField(queryset=models.User.objects.exclude(role='admin'), required=False)
    name = serializers.CharField(max_length=255, required=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
    price_hour = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)

    class Meta:
        model = models.Stadium
        fields = [
            'id', 'name', 'latitude', 'longitude', 'description',
            'price_hour', 'owner', 'manager', 'is_active'
        ]
        extra_kwargs = {
            'owner': {'required': False},  # Admin serializerda override qilinadi
        }

    def validate(self, attrs):
        name = attrs.get('name')
        latitude = attrs.get('latitude')
        longitude = attrs.get('longitude')
        owner = attrs.get('owner', self.context['request'].user)
        manager = attrs.get('manager')

        if models.Stadium.objects.filter(name=name, latitude=latitude, longitude=longitude).exists():
            raise serializers.ValidationError({"message": _("Such a stadium already exists.")})

        if manager and manager == owner:
            raise serializers.ValidationError({"message": _("Owner and Manager cannot be the same user.")})

        if owner.role == 'owner' and models.Stadium.objects.filter(owner=owner).count() >= 3:
            raise serializers.ValidationError({"message": _("This owner already has 3 stadiums.")})

        return attrs

    def create(self, validated_data):
        manager = validated_data.get('manager')
        if manager:
            manager.role = 'manager'
            manager.save()
            validated_data['manager'] = manager

        return super().create(validated_data)

class StadiumOwnerCreateSerializer(BaseStadiumCreateSerializer):
    class Meta(BaseStadiumCreateSerializer.Meta):
        exclude = ['owner']

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class StadiumAdminCreateSerializer(BaseStadiumCreateSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=models.User.objects.exclude(role='admin'))

    def create(self, validated_data):
        owner = validated_data['owner']
        if owner.role != 'owner':
            owner.role = 'owner'
            owner.save()
        validated_data['owner'] = owner
        return super().create(validated_data)



class UserShortInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'phone_number']

class StadiumListSerializer(serializers.ModelSerializer):
    owner = UserShortInfoSerializer()
    manager = UserShortInfoSerializer()

    class Meta:
        model = models.Stadium
        fields = [
            'id', 'name', 'latitude', 'longitude', 'description',
            'price_hour', 'owner', 'manager', 'is_active', 'image'
        ]