from django.contrib import admin
from .models import Asset, InsurancePolicy

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'value', 'serial_number']
    list_filter = ['category']

@admin.register(InsurancePolicy)
class InsurancePolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'policy_number']
