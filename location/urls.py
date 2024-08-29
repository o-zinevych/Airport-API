from django.urls import path, include
from rest_framework import routers

from .views import CountryViewSet

router = routers.DefaultRouter()
router.register("countries", CountryViewSet)

urlpatterns = [
    path("", include(router.urls))
]

app_name = "location"
