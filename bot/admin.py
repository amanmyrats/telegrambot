from django.contrib import admin

from .models import LastRead, FailedMessage


admin.site.register(LastRead)
admin.site.register(FailedMessage)