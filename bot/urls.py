from django.urls import path

from .views import (
    status_view, start_view, stop_view
)


urlpatterns = [
    path('status/', status_view, name='bot-status'),
    path('start/', start_view, name='bot-start'),
    path('stop/', stop_view, name='bot-stop'),
]