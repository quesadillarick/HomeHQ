from django.contrib import admin
from .models import Vehicle, ServiceLog

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['year', 'make', 'model', 'plate', 'odometer']

admin.site.register(ServiceLog)
