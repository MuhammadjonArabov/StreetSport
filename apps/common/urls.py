from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register(r'stadium', views.StadiumViewSet, basename='stadium')

urlpatterns = [
    path("stadium/list/", views.StadiumListAPIView.as_view(), name="stadium-list"),
    path('stadium/status/', views.StadiumStatsCountAPIView.as_view(), name="status-count"),
    path('bron/create/', views.BronCreateAPIView.as_view(), name="bron-create"),
    path("", include(router.urls)),
]
