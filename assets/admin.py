from django.contrib import admin
from .models import Asset


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('asset_tag', 'name', 'category', 'status', 'condition', 'location')
    list_filter = ('status', 'condition', 'category', 'is_bookable')
    search_fields = ('name', 'asset_tag', 'serial_number')
    readonly_fields = ('asset_tag', 'created_at', 'updated_at')
