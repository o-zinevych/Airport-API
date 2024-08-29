from django.contrib import admin

from .models import Country, City, Airport

admin.site.register(Country)
admin.site.register(City)
admin.site.register(Airport)
