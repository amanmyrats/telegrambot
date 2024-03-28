import requests
import ast
import logging
from pathlib import Path

from django.conf import settings

from premiumgroups.models import (
    PremiumGroup, SectorKeyword, LocationKeyword, 
)
from .models import LastRead, FailedMessage, BotState


BOT_URL = f'{settings.TELEGRAM_BOT_URL}{settings.TELEGRAM_TOKEN}'
logger = logging.getLogger('django')

def fetch_messages():
    logger.info('Started fetching messages')

    # Set offset
    last_read = LastRead.objects.all().first()
    if last_read is None:
        logger.info('Last_read is None')
        offset = 0
    else:
        offset=int(last_read.update_id) + 1
    params={}
    if offset is not None:
        params={'offset':offset}
    logger.info(f"URL:{BOT_URL}/getUpdates?{params}")

    # Send request
    response = requests.get(f"{BOT_URL}/getUpdates", params=params)
    data = response.json()
    logger.info(f"Length of result:{len(data.get('result'))}")

    # Loop through results
    # 1 - Filter
    # 2 - Generate Text if there is match
    # 3 - Send message
    # 4 - Update LastRead update_id
    for result in data['result']:
        # for k,v in result.items():
        #     print(k, ':',v)
        print('--------')
        filter(result)
        update_last_read_message(result['update_id'])

    pass



def filter(result):
    try:
        message = result['message']
    except:
        try:
            message = result['edited_message']
        except:
            message = None
    if message is None:
        return
    full_text = get_full_text(message)
    chat_title = get_chat_title(message)
    users_text = get_users_text(message)
    logger.info('Filtering...')
    logger.info(f"full_text:{str(full_text)}")
    logger.info(f"chat_title:{str(chat_title)}")
    logger.info(f"users_text:{str(users_text)}")

    if full_text is None:
        return
    sector_keywords = SectorKeyword.objects.all()
    location_keywords = LocationKeyword.objects.all()
    sector_pgs = []
    location_pgs = []
    pgs_to_send_message = []
    for sector_keyword in sector_keywords:
        if sector_keyword.keyword.lower() in full_text.lower():
            logger.info(f"sector_keyword matches: {sector_keyword.keyword.lower()}")

            matched_pgs = sector_keyword.sector.sector_pgs.all()
            for pg in matched_pgs:
                sector_pgs.append(pg)

            for location_keyword in location_keywords:
                is_location_match = False
                if location_keyword.keyword.lower() in users_text.lower():
                    logger.info(f"location_keyword matches with users text: {location_keyword.keyword.lower()}")
                    is_location_match = True
                elif location_keyword.keyword.lower() in full_text.lower() or \
                    location_keyword.keyword.lower() in chat_title.lower():
                    logger.info(f"location_keyword matches with title: {location_keyword.keyword.lower()}")
                    is_location_match = True
                if is_location_match:
                    matched_pgs = location_keyword.location.location_pgs.all()
                    for pg in matched_pgs:
                        location_pgs.append(pg)
                
            pgs_to_send_message = list(set(sector_pgs) & set(location_pgs))
            logger.info(f"sector_pgs: {str(sector_pgs)}")
            logger.info(f"location_pgs: {str(location_pgs)}")
            logger.info(f"pgs_to_send_message: {str(pgs_to_send_message)}")


            for pg in pgs_to_send_message:    
                send_message(
                        pg.chat_id, 
                        full_text,
                        generate_inline_keyboard(get_message_button(message), get_user_button(message))
                    )


def send_message(chat_id, text_to_send, inline_keyboard):
    logger.info('Sending message')
    data = {
        'chat_id':chat_id, 
        'text':text_to_send, 
        'reply_markup':{
            'inline_keyboard': inline_keyboard
        }
    }

    logger.info('Data to be sent')
    logger.info(str(data))

    try:
        resp = requests.post(f"{BOT_URL}/sendMessage", json=data)
        logger.info(f"Message status: {str(resp.json())}")
        if resp.json()['ok']==True:
            logger.info('Message sent successfully')
            remove_from_failed_messages(data['chat_id'], data['text'], inline_keyboard)
        else:
            logger.info('Failed to send a message')
            logger.info(str(resp.json()))

            add_to_failed_messages(data['chat_id'], data['text'], inline_keyboard, resp.json())
    except Exception as e:
        logger.info('Network error')
        logger.info(str(e))

        add_to_failed_messages(data['chat_id'], data['text'], inline_keyboard, str(e))


def add_to_failed_messages(chat_id, text, inline_keyboard, error_message):
    # Check if text already exists
    count_text= FailedMessage.objects.filter(chat_id=chat_id, text=text).count()
    if count_text==0:
        failed_message = FailedMessage()
        failed_message.chat_id = chat_id
        failed_message.text = text
        failed_message.inline_keyboard = inline_keyboard
        failed_message.error_message = error_message
        failed_message.save()


def remove_from_failed_messages(chat_id, text, inline_keyboard):
    # Check if it exists
    is_exist = FailedMessage.objects.filter(chat_id=chat_id, text=text, inline_keyboard=inline_keyboard).exists()
    if is_exist:
        FailedMessage.objects.filter(chat_id=chat_id, text=text, inline_keyboard=inline_keyboard).delete()


def resend_failed_messages():
    logger.info('Resending failed messages')
    failed_messages = FailedMessage.objects.all()
    for fm in failed_messages:
        try:
            logger.info(f"chat_id:  {fm.chat_id}")
            logger.info(f"text:  {fm.text}")
            logger.info(f"inline_keyboard:  {str(fm.inline_keyboard)}")
            send_message(fm.chat_id, fm.text, ast.literal_eval(fm.inline_keyboard))
        except Exception as e:
            logger.info(f"Failed to sending again: {str(e)}")
            fm.error_message = str(e)
            fm.save()
    logger.info('Resending failed messages is done')



def generate_text_to_send(message, keyword):
    text = get_full_text(message)
    text_to_send = f"{text}\nKeyword: {keyword}"
    return text_to_send


def generate_inline_keyboard(message_button, user_button):
    inline_keyboard = [[]]
    if message_button:
        inline_keyboard[0].append(message_button)
    if user_button:
        inline_keyboard[0].append(user_button)

    return inline_keyboard


def get_full_text(message):
    if message is None:
        return ''
    text = message.get('text')
    if text is None:
        text = message.get('caption')
    if text is None:
        return ''
    return text


def get_users_text(message):
    if message is None:
        return ''
    text = get_full_text(message)
    if text is None:
        return ''
    parts = text.split('\n')
    if parts is None:
        return ''
    if len(parts)>1:
        return ' '.join(parts[2:])
    else:
        return text
    

def get_chat_title(message):
    if message is None:
        return ''
    text = get_full_text(message)
    if text is None:
        return ''
    parts = text.split('\n')
    if parts is None:
        return ''
    if len(parts)>=0:
        return parts[0]
    else:
        return ''


def get_user_link(message):
    logger.info('Inside get_user_link')
    logger.info(f"Searching for message: {str(message)}")
    user_link = None
    if message is None:
        return user_link
    entities = message.get('entities')
    if entities is None:
        return user_link
    for entity in entities:
        logger.info(f"entity: {str(entity)}")
        if 'url' in entity:
            logger.info('has url')
            if 'user' in entity['url']:
                logger.info('has user')
                user_link = entity['url']
    return user_link
    


def get_message_link(message):
    message_link = None
    if message is None:
        return message_link
    entities = message.get('entities')
    if entities is None:
        return message_link
    for entity in entities:
        if 'url' in entity:
            if '//t.me/c/' in entity['url']:
                message_link = entity['url']
    return message_link


def get_user_button(message):

    user_link = get_user_link(message)
    logger.info(f"get_user_button, user_link: {str(user_link)}")
    logger.info(f"mesage: {str(message)}")
    if user_link:
        return {'text':'See User', 'url':user_link}
    else:
        return None


def get_message_button(message):
    message_link = get_message_link(message)
    if message_link:
        return {'text':'Send Message', 'url':message_link}
    else:
        return None


def get_sender_username(message):
    if message is None:
        return ''
    # forward_origin
    text = get_full_text(message)
    if text is None:
        return ''
    parts = text.split('\n')
    if parts is None:
        return ''
    if len(parts)>0:
        return parts[1]
    else:
        return ''


def update_last_read_message(update_id):
    last_read = LastRead.objects.all().first()
    if last_read is None:
        new_last_read = LastRead()
        new_last_read.update_id = update_id
        try:
            new_last_read.save()
            logger.info(f"Last read update id was added to database: {str(update_id)}")
        except Exception as e:
            logger.info(f"Error when adding new update_id to database: {str(update_id)} - {str(e)}")
    else:
        last_read.update_id = update_id
        try:
            last_read.save()
            logger.info(f"Last read update id updated in database: {str(update_id)}")
        except Exception as e:
            logger.info(f"Error when updating update_id to database:: {str(update_id)} - {str(e)}")


def get_bot_status():
    is_exists = BotState.objects.all().exists()
    if not is_exists:
        new_status = BotState()
        new_status.is_running = False
        new_status.save()
    existing_status = BotState.objects.all().first()
    return existing_status.is_running


def set_bot_status(status=False):
    is_exists = BotState.objects.all().exists()
    if not is_exists:
        new_status = BotState()
        new_status.is_running = status
        new_status.save()
    existing_status = BotState.objects.all().first()
    existing_status.is_running=status
    existing_status.save()