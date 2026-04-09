from django.contrib import admin
from .models import RentSchedule, ContractEvent, Notification

@admin.register(RentSchedule)
class RentScheduleAdmin(admin.ModelAdmin):
    list_display = ['contract', 'due_date', 'amount', 'status', 'paid_date']
    list_filter = ['status', 'payment_type']

@admin.register(ContractEvent)
class ContractEventAdmin(admin.ModelAdmin):
    list_display = ['contract', 'event_type', 'title', 'status', 'scheduled_date']
    list_filter = ['event_type', 'status']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'channel', 'status', 'title', 'sent_at']
    list_filter = ['channel', 'status']
