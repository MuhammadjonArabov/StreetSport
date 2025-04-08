from rest_framework import serializers
from . import models

class StadiumCreateSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=models.User.objects.exclude(role='admin'), required=True)
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

    def create(self, validated_data):
        owner = validated_data.get('owner')
        owner.role = 'owner'
        owner.save()
        return super().create(validated_data)
