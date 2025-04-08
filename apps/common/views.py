from rest_framework import viewsets, mixins, permissions
from .models import Stadium
from .serializers import StadiumCreateSerializer
from apps.user.permissions import IsAdminUser

class StadiumRestrictedViewSet(mixins.CreateModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.DestroyModelMixin,
                                viewsets.GenericViewSet):
    queryset = Stadium.objects.all()
    serializer_class = StadiumCreateSerializer
    permission_classes = [IsAdminUser]
