from django.contrib import admin

from .models import AirplaneType, Airplane

admin.site.register(AirplaneType)
admin.site.register(Airplane)
