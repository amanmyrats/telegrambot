from django.contrib import admin
from django.urls import reverse  # Import for related_link generator

from .models import (
    PremiumGroup, Sector, Location, 
    SectorKeyword, LocationKeyword
)


admin.site.register(PremiumGroup)
# admin.site.register(Sector)
# admin.site.register(Location)
admin.site.register(SectorKeyword)
admin.site.register(LocationKeyword)



class SectorKeywordInline(admin.TabularInline):  # Use TabularInline for list view
    model = SectorKeyword
    # readonly_fields = ['sector', 'keyword']  # Make sector and keyword fields read-only

class SectorAdmin(admin.ModelAdmin):
    inlines = [SectorKeywordInline]

    def get_queryset(self, request):
        # Optionally filter displayed sectors based on user permissions
        return super().get_queryset(request).prefetch_related('keywords')  # Pre-fetch keywords

    # def get_related_link(self, obj):
        # Generate link to the SectorKeyword change list filtered by this sector
        # return reverse('admin:yourapp.sectorkeyword_changelist') + f'?sector__id={obj.pk}'
    
    list_display = ['name', ]  # Add 'get_related_link' column
    readonly_fields = ['name']  # Make the name field read-only in the edit form

class LocationKeywordInline(admin.TabularInline):  # Use TabularInline for list view
    model = LocationKeyword
    # readonly_fields = ['location', 'keyword']  # Make location and keyword fields read-only

class LocationAdmin(admin.ModelAdmin):
    inlines = [LocationKeywordInline]

    def get_queryset(self, request):
        # Optionally filter displayed locations based on user permissions
        return super().get_queryset(request).prefetch_related('keywords')  # Pre-fetch keywords

    # def get_related_link(self, obj):
        # Generate link to the LocationKeyword change list filtered by this location
        # return reverse('admin:yourapp.locationkeyword_changelist') + f'?location__id={obj.pk}'
    
    list_display = ['name', ]  # Add 'get_related_link' column
    readonly_fields = ['name']  # Make the name field read-only in the edit form


admin.site.register(Sector, SectorAdmin)
admin.site.register(Location, LocationAdmin)
