from django.contrib import admin

from .models import Donation


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('date', 'donation_type', 'amount', 'payment_method', 'is_anonymous')
    list_filter = ('donation_type', 'payment_method', 'is_anonymous')
    date_hierarchy = 'date'
