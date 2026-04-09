from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'reviewee', 'review_type', 'rating', 'created_at']
    list_filter = ['review_type', 'rating']
