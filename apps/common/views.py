from rest_framework.response import Response
from rest_framework import viewsets, mixins, permissions, generics, filters, views
from . import models
from rest_framework.exceptions import PermissionDenied
from . import serializers
from apps.user.permissions import IsAdminUser, IsOwnerUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Case, When, IntegerField


class StadiumViewSet(viewsets.ModelViewSet):
    queryset = models.Stadium.objects.all()
    permission_classes = [IsAdminUser | IsOwnerUser]

    def get_serializer_class(self):
        user = self.request.user
        if user.role == 'admin':
            return serializers.StadiumAdminCreateSerializer
        else:
            return serializers.StadiumOwnerCreateSerializer


    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return models.Stadium.objects.all()
        return models.Stadium.objects.filter(owner=user)

    def perform_destroy(self, instance):
        if self.request.user.role == 'owner' and instance.owner != self.request.user:
            raise PermissionDenied("You do not have permission to delete!")
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.role == 'owner' and instance.owner != request.user:
            raise PermissionDenied("You do not have permission to update!")
        return super().update(request, *args, **kwargs)

class StadiumStatsCountAPIView(views.APIView):
    permission_classes = [IsAdminUser, IsOwnerUser]

    def get(self, request):
        stats = models.Stadium.objects.aggregate(
            total=Count('id'),
            active=Count(Case(When(is_active=True, then=1), output_field=IntegerField())),
            inactive=Count(Case(When(is_active=False, then=1), output_field=IntegerField()))
        )

        return Response({
            "total_stadiums": stats['total'],
            "active_stadiums": stats['active'],
            "inactive_stadiums": stats['inactive']
        })


class StadiumListAPIView(generics.ListAPIView):
    queryset = models.Stadium.objects.select_related('owner', 'manager').all()
    serializer_class = serializers.StadiumListSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'price_hour']
    search_fields = ['name', 'price_hour', 'owner__full_name', 'owner__phone_number', 'manager__full_name',
                     'manager__phone_number']
    ordering_fields = ['name']
