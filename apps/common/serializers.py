from rest_framework import serializers
from . import models
from apps.user.models import User
from datetime import timedelta
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
            'owner': {'required': False},
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

        if manager and manager.role in ['admin', 'owner']:
            raise serializers.ValidationError({"message": _("Manager cannot be a user with 'admin' or 'owner' role.")})

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
    class Meta:
        model = models.Stadium
        fields = [
            'id', 'name', 'latitude', 'longitude', 'description',
            'price_hour', 'manager', 'is_active'
        ]

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
    manager = UserShortInfoSerializer()

    class Meta:
        model = models.Stadium
        fields = [
            'id', 'name', 'latitude', 'longitude', 'description',
            'price_hour', 'manager', 'is_active', 'image'
        ]

class BronCreateSerializer(serializers.ModelSerializer):
    is_team = serializers.BooleanField(write_only=True)
    team = serializers.PrimaryKeyRelatedField(
        queryset=models.Team.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = models.Bron
        fields = ['stadium', 'start_time', 'end_time', 'order_type', 'is_team', 'team']

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        stadium = attrs.get('stadium')
        is_team = attrs.get('is_team')
        team = attrs.get('team', None)
        user = self.context['request'].user

        if start_time >= end_time:
            raise serializers.ValidationError(_("Start time must be before end time"))

        duration = (end_time - start_time).total_seconds() / 3600
        if duration < 1:
            raise serializers.ValidationError(_("Booking must be at least 1 hour"))
        if duration % 1 != 0:
            raise serializers.ValidationError(_("Booking duration must be in full hours (1, 2, 3, ...)"))

        overlaps = models.Bron.objects.filter(
            stadium=stadium,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )
        if overlaps.exists():
            raise serializers.ValidationError(_("This time slot is already booked."))

        if user.role in ['admin', 'manager']:
            raise serializers.ValidationError(_("Admins and Managers cannot book stadiums."))

        if is_team:
            if not team:
                raise serializers.ValidationError({"team": _("Team must be provided for team bookings.")})
            if not (team.owner == user or user in team.members.all()):
                raise serializers.ValidationError(_("You are not allowed to book on behalf of this team."))
        else:
            if team:
                raise serializers.ValidationError({"team": _("Team should not be provided for user bookings.")})

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        validated_data.pop('is_team')  # Not needed for DB

        return super().create(validated_data)
