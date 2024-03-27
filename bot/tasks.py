import time

from core.celery import app

from .utils import (
        get_bot_status, set_bot_status, resend_failed_messages, fetch_messages
    )


@app.task
def keep_fetching(data):
    print('start fetching')
    set_bot_status(True)
    is_running = True
    while is_running:
        time.sleep(3)
        is_running = get_bot_status()
        try:
            resend_failed_messages()
            fetch_messages()
        except Exception as e:
            print('error when fetching', e)
            pass
    return f"Done snitching..."