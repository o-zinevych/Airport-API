from django.urls import path, include
from rest_framework import routers

from .views import RouteViewSet

router = routers.DefaultRouter()
router.register("routes", RouteViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "flight-ops"
