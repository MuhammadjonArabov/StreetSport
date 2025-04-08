from rest_framework.routers import DefaultRouter
from .views import StadiumRestrictedViewSet

router = DefaultRouter()
router.register(r'stadium', StadiumRestrictedViewSet, basename='stadium')

urlpatterns = router.urls
