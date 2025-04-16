from django.urls import path, include
from rest_framework import routers

from .views import CrewViewSet, RouteViewSet, FlightViewSet

router = routers.DefaultRouter()
router.register("routes", RouteViewSet)
router.register("crew", CrewViewSet)
router.register("flights", FlightViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "flight-ops"
