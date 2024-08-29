from django.contrib import admin

from .models import Crew, Route, Flight

admin.site.register(Crew)
admin.site.register(Route)
admin.site.register(Flight)
