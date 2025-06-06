from django.urls import path, include
from rest_framework import routers

from .views import AirplaneTypeViewSet, AirplaneViewSet

router = routers.DefaultRouter()
router.register(
    "airplane-types",
    AirplaneTypeViewSet,
    basename="airplane-type"
)
router.register("airplanes", AirplaneViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "fleet"
