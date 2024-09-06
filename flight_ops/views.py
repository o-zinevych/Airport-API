from datetime import datetime

from django.db.models import F, Count
from drf_spectacular.utils import extend_schema, OpenApiParameter
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
    queryset = Crew.objects.all()
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

    @staticmethod
    def _params_to_int(query_str):
        return [int(str_id) for str_id in query_str.split(",")]

    def get_queryset(self):
        """
        Filter the list by certain parameters and annotate the queryset with
        available seats count.
        """
        queryset = self.queryset
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        departure_date = self.request.query_params.get("departure_date")
        arrival_date = self.request.query_params.get("arrival_date")

        if source:
            source_ids = self._params_to_int(source)
            queryset = queryset.filter(route__source_id__in=source_ids)
        if destination:
            destination_ids = self._params_to_int(destination)
            queryset = queryset.filter(
                route__destination_id__in=destination_ids
            )

        if departure_date:
            dep_date = datetime.strptime(departure_date, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date=dep_date)
        if arrival_date:
            arr_date = datetime.strptime(arrival_date, "%Y-%m-%d").date()
            queryset = queryset.filter(arrival_time__date=arr_date)

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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                description="Filter the flights by their source airport ids, "
                            "e.g. ?source=1,3."
            ),
            OpenApiParameter(
                "destination",
                description="Filter the flights by their destination airport "
                            "ids, e.g. ?destination=4,5."
            ),
            OpenApiParameter(
                "departure_date",
                type={'type': 'string', 'format': 'date'},
                description="Filter the flights by their departure date, e.g. "
                            "2024-09-01."
            ),
            OpenApiParameter(
                "arrival_date",
                type={'type': 'string', 'format': 'date'},
                description="Filter the flights by their arrival date, e.g. "
                            "2024-09-02."
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
