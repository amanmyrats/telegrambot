from django.urls import path

from .views import (
    PGListView, SectorListView, LocationListView
)


urlpatterns = [
    path('pgs/', PGListView.as_view(), name='pg-list'),
    path('sectors/', SectorListView.as_view(), name='sector-list'),
    path('locations/', LocationListView.as_view(), name='location-list'),
]