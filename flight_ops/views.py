from rest_framework import viewsets

from .models import Crew, Route, Flight
from .serializers import (
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    CrewSerializer,
    FlightSerializer,
    FlightListSerializer
)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.prefetch_related("flights")
    serializer_class = CrewSerializer


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


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.select_related("route", "airplane")

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        return FlightSerializer
