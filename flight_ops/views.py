from rest_framework import viewsets

from .models import Route
from .serializers import (
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer
)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "retrieve":
            queryset = queryset.select_related(
                "source__closest_big_city",
                "source__closest_big_city__country",
                "destination__closest_big_city",
                "destination__closest_big_city__country"
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer
