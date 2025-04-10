from rest_framework.response import Response
from rest_framework import viewsets, permissions, generics, filters, views
from . import models
from rest_framework.exceptions import PermissionDenied
from . import serializers
from apps.user.permissions import IsAdminUser, IsOwnerUser, IsManager
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Case, When, IntegerField, Sum, Q, F, ExpressionWrapper, DecimalField


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
        elif user.role == 'owner':
            return models.Stadium.objects.filter(owner=user)
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
    permission_classes = [IsAdminUser]

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
    queryset = models.Stadium.objects.filter(is_active=True).select_related('owner', 'manager').all()
    serializer_class = serializers.StadiumListSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'price_hour']
    search_fields = ['name', 'price_hour', 'manager__full_name', 'manager__phone_number']
    ordering_fields = ['name']

class BronCreateAPIView(generics.CreateAPIView):
    queryset = models.Bron.objects.all()
    serializer_class = serializers.BronCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

class BronUpdateAPIView(generics.UpdateAPIView):
    queryset = models.Bron.objects.all()
    serializer_class = serializers.BronUpdateSerializer
    permission_classes = [IsManager]
    lookup_field = 'pk'

class OwnerBronListAPIView(generics.ListAPIView):
    serializer_class = serializers.StadionBronSerializer
    permission_classes = [IsOwnerUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['stadium__name', 'start_time', 'end_time', 'is_paid']
    search_fields = ['stadium__name', ]
    ordering_fields = ['start_time', 'end_time']
    ordering = ['start_time']

    def get_queryset(self):
        user = self.request.user
        owner_stadium = models.Stadium.objects.filter(owner=user)
        bron_list = models.Bron.objects.filter(stadium__in=owner_stadium)
        return bron_list


class OwnerStadiumStatsView(generics.ListAPIView):
    serializer_class = serializers.StadiumStatsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (
            models.Stadium.objects.filter(owner=user)
            .annotate(
                total_bron_count=Count('bron_stadium', distinct=True),
                total_income=Sum(
                    ExpressionWrapper(
                        F('price_hour'),
                        output_field=DecimalField()
                    ),
                    filter=Q(bron_stadium__is_paid=True)
                )
            )
        )