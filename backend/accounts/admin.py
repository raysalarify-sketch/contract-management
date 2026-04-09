from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Company, LandlordProfile, AgentProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'get_full_name', 'role', 'phone', 'is_verified', 'company']
    list_filter = ['role', 'is_verified', 'company']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('워크드 정보', {'fields': ('role', 'phone', 'is_verified', 'profile_image', 'company')}),
    )

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'business_number', 'representative', 'usage_rate', 'is_active']

@admin.register(LandlordProfile)
class LandlordProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'response_rate', 'avg_response_minutes', 'total_contracts']

@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'office_name', 'license_number']
