from rest_framework import serializers

from .models import Crew, Route, Flight


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class RouteSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(RouteSerializer, self).validate(attrs)
        Route.validate_source_and_destination(
            attrs["source"],
            attrs["destination"],
            serializers.ValidationError
        )
        return data

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(read_only=True, slug_field="name")
    destination = serializers.SlugRelatedField(
        read_only=True,
        slug_field="name"
    )


class RouteDetailSerializer(RouteSerializer):
    source = serializers.StringRelatedField(read_only=True)
    destination = serializers.StringRelatedField(read_only=True)


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id",
            "number",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew"
        )


class FlightListSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        read_only=True,
        slug_field="source.name",
        source="route"
    )
    destination = serializers.SlugRelatedField(
        read_only=True,
        slug_field="destination.name",
        source="route"
    )
    seats_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "number",
            "source",
            "destination",
            "departure_time",
            "arrival_time",
            "seats_available"
        )


class FlightDetailSerializer(serializers.ModelSerializer):
    route = serializers.StringRelatedField(read_only=True)
    airplane = serializers.StringRelatedField(read_only=True)
    crew = CrewSerializer(many=True, read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "number",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew"
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")

        if request and not request.user.is_staff:
            representation.pop("crew")

        return representation
