from rest_framework import viewsets

from .models import AirplaneType
from .serializers import AirplaneTypeSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
