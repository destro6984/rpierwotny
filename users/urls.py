from rest_framework.routers import DefaultRouter
from .views import (
    SubscriberViewSet,
    SubscriberSMSViewSet,
    ClientViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register(r"subscribers", SubscriberViewSet)
router.register(r"subscribersms", SubscriberSMSViewSet)
router.register(r"clients", ClientViewSet)
router.register(r"users", UserViewSet)

urlpatterns = router.urls
