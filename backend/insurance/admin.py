from django.contrib import admin
from .models import InsuranceApplication, NotaryApplication, MortgageApplication

@admin.register(InsuranceApplication)
class InsuranceAdmin(admin.ModelAdmin):
    list_display = ['contract', 'provider', 'status', 'coverage_amount', 'premium', 'policy_number']
    list_filter = ['provider', 'status']

@admin.register(NotaryApplication)
class NotaryAdmin(admin.ModelAdmin):
    list_display = ['contract', 'status', 'notary_office', 'scheduled_date']

@admin.register(MortgageApplication)
class MortgageAdmin(admin.ModelAdmin):
    list_display = ['contract', 'status', 'amount', 'lawyer_name']
