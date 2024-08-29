from rest_framework import serializers

from .models import Route


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
