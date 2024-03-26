from django.apps import AppConfig


class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bot'

    def ready(self) -> None:
        from .models import BotState
        is_exists = BotState.objects.all().exists()
        if not is_exists:
            new_status = BotState()
            new_status.is_running = False
            new_status.save()
        else:
            existing_status = BotState.objects.all().first()
            existing_status.is_running = False
            existing_status.save()
        return super().ready()