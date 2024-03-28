import logging

from django.shortcuts import render
from django.http import JsonResponse

from .tasks import keep_fetching
from .utils import set_bot_status, get_bot_status


logger = logging.getLogger('django')

def status_view(request):
    is_running = get_bot_status()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if is_running:
            return JsonResponse({'data':is_running})
        else:
            return JsonResponse({'error_message': is_running}, status=500)
    else:
        return render(request, 'bot/status.html', {'status': is_running})


def start_view(request):
    bot_status = {
      "message": "Bot is running!",
    }
    keep_fetching.delay(True)
    return JsonResponse(bot_status)


def stop_view(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        is_running = set_bot_status(False)
        return JsonResponse({'data':is_running})
