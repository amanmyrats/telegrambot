from django.contrib import admin

from .models import (
    PremiumGroup, Sector, Location, 
    SectorKeyword, LocationKeyword
)


admin.site.register(PremiumGroup)
admin.site.register(Sector)
admin.site.register(Location)
admin.site.register(SectorKeyword)
admin.site.register(LocationKeyword)
