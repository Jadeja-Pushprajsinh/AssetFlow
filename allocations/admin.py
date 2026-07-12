from django.contrib import admin
from .models import Allocation, TransferRequest

@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'asset', 'holder_type', 'status', 'allocated_date', 'expected_return_date')
    list_filter = ('status', 'holder_type')
    search_fields = ('asset__asset_tag', 'asset__name')

@admin.register(TransferRequest)
class TransferRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'asset', 'status', 'requested_by', 'created_at')
    list_filter = ('status',)
