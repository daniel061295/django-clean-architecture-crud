from rest_framework.routers import DefaultRouter
from store.tips.interfaces.views import TipViewSet

router = DefaultRouter()
router.register(r'', TipViewSet, basename='tips')

urlpatterns = router.urls
