from django.urls import path, include
from rest_framework import routers

from .views import CrewViewSet, RouteViewSet

router = routers.DefaultRouter()
router.register("routes", RouteViewSet)
router.register("crew", CrewViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "flight-ops"
