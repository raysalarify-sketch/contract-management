from django.contrib import admin
from .models import Property, PropertyImage, RiskScan, PropertyTag

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1

class PropertyTagInline(admin.TabularInline):
    model = PropertyTag
    extra = 1

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['name', 'property_type', 'deposit_display', 'risk_grade', 'risk_score', 'is_insurable', 'is_available']
    list_filter = ['property_type', 'risk_grade', 'is_insurable', 'is_available']
    search_fields = ['name', 'address']
    inlines = [PropertyImageInline, PropertyTagInline]

@admin.register(RiskScan)
class RiskScanAdmin(admin.ModelAdmin):
    list_display = ['related_property', 'overall_grade', 'overall_score', 'scanned_at']
    list_filter = ['overall_grade']
