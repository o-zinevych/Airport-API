from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from .models import Order
from .serializers import OrderSerializer, OrderListSerializer


class OrderViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin
):
    queryset = Order.objects.prefetch_related("tickets__flight")
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
