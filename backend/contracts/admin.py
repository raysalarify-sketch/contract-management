from django.contrib import admin
from .models import Inquiry, InquiryMessage, ContractAgreement, Contract, ESignature, AgentVerification
from schedules.models import RentSchedule, Notification

class InquiryMessageInline(admin.TabularInline):
    model = InquiryMessage
    extra = 0
    readonly_fields = ['created_at']

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ['related_property', 'tenant', 'landlord', 'status', 'created_at']
    list_filter = ['status']
    inlines = [InquiryMessageInline]

@admin.register(ContractAgreement)
class ContractAgreementAdmin(admin.ModelAdmin):
    list_display = ['related_property', 'tenant', 'landlord', 'status', 'landlord_agreed', 'tenant_agreed']
    list_filter = ['status']

class ESignatureInline(admin.TabularInline):
    model = ESignature
    extra = 0
    readonly_fields = ['signed_at']

class RentScheduleInline(admin.TabularInline):
    model = RentSchedule
    extra = 0
    fields = ['due_date', 'amount', 'status', 'paid_date']

class NotificationInline(admin.TabularInline):
    model = Notification
    extra = 0
    fields = ['channel', 'status', 'title', 'sent_at']
    readonly_fields = ['sent_at']

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['related_property', 'tenant', 'landlord', 'status', 'start_date', 'end_date', 'days_until_expiry']
    list_filter = ['status']
    search_fields = ['property__name', 'tenant__first_name', 'landlord__first_name']
    inlines = [ESignatureInline, RentScheduleInline, NotificationInline]
