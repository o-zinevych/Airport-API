from django.contrib import admin

from .models import Order, Ticket

admin.site.register(Ticket)


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1
    max_num = 9


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [TicketInline]
