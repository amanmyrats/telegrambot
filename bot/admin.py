from django.contrib import admin

from .models import LastRead, FailedMessage, BotState


admin.site.register(LastRead)
admin.site.register(FailedMessage)
admin.site.register(BotState)