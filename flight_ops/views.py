from django.db.models import F, Count
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAdminUser

from .models import Crew, Route, Flight
from .serializers import (
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    CrewSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer
)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.prefetch_related("flights")
    serializer_class = CrewSerializer
    permission_classes = (IsAdminUser,)


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


class FlightViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin
):
    queryset = Flight.objects.select_related(
        "route",
        "route__source",
        "route__destination"
    )

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            queryset = queryset.annotate(
                seats_available=F("airplane__seats_in_row")
                * F("airplane__rows") - Count("tickets")
            )

        if self.action == "retrieve":
            queryset = queryset.select_related(
                "route__source__closest_big_city",
                "route__destination__closest_big_city",
                "airplane",
                "airplane__airplane_type"
            ).prefetch_related(
                "route__source__closest_big_city__country",
                "route__destination__closest_big_city__country",
                "crew"
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer

        return FlightSerializer
