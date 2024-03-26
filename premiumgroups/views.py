from django.shortcuts import render
from django.views import generic

from .models import (
    PremiumGroup, Sector, Location
)


class PGListView(generic.ListView):
    model = PremiumGroup
    context_object_name = 'pgs'


class SectorListView(generic.ListView):
    model = Sector
    context_object_name = 'sectors'


class LocationListView(generic.ListView):
    model = Location
    context_object_name = 'locations'
