import requests
import ast

from django.conf import settings

from premiumgroups.models import (
    PremiumGroup, SectorKeyword, LocationKeyword, 
)
from .models import LastRead, FailedMessage, BotState


BOT_URL = f'{settings.TELEGRAM_BOT_URL}{settings.TELEGRAM_TOKEN}'

def fetch_messages():
    print('fetching messages')

    # Set offset
    last_read = LastRead.objects.all().first()
    if last_read is None:
        print("last_read is None")
        offset = 0
    else:
        offset=int(last_read.update_id) + 1
    params={}
    if offset is not None:
        params={'offset':offset}
    print("URL", f"{BOT_URL}/getUpdates?{params}")

    # Send request
    response = requests.get(f"{BOT_URL}/getUpdates", params=params)
    data = response.json()
    print('Length of result:',len(data.get('result')))

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
    print('filtering')
    print(result)
    print('full_text:', full_text)
    print('chat_title:', chat_title)
    print('users_text:', users_text)

    if full_text is None:
        return
    sector_keywords = SectorKeyword.objects.all()
    location_keywords = LocationKeyword.objects.all()
    sector_pgs = []
    location_pgs = []
    pgs_to_send_message = []
    for sector_keyword in sector_keywords:
        if sector_keyword.keyword.lower() in full_text.lower():
            print('sector_keyword matches:', sector_keyword.keyword.lower())
            matched_pgs = sector_keyword.sector.sector_pgs.all()
            for pg in matched_pgs:
                sector_pgs.append(pg)

            for location_keyword in location_keywords:
                is_location_match = False
                if location_keyword.keyword.lower() in users_text.lower():
                    print('location_keyword matches with users text:', location_keyword.keyword.lower())
                    is_location_match = True
                elif location_keyword.keyword.lower() in full_text.lower() or \
                    location_keyword.keyword.lower() in chat_title.lower():
                    print('location_keyword matches with title:', location_keyword.keyword.lower())
                    is_location_match = True
                if is_location_match:
                    matched_pgs = location_keyword.location.location_pgs.all()
                    for pg in matched_pgs:
                        location_pgs.append(pg)
                
            pgs_to_send_message = list(set(sector_pgs) & set(location_pgs))
            print('sector_pgs', sector_pgs)
            print('location_pgs', location_pgs)
            print('pgs_to_send_message', pgs_to_send_message)

            for pg in pgs_to_send_message:    
                print('sending filtered message')
                send_message(
                        pg.chat_id, 
                        full_text,
                        generate_inline_keyboard(get_message_button(message), get_user_button(message))
                    )


def send_message(chat_id, text_to_send, inline_keyboard):
    print('sending message')
    data = {
        'chat_id':chat_id, 
        'text':text_to_send, 
        'reply_markup':{
            'inline_keyboard': inline_keyboard
        }
    }
    # if see_user_button:
    #     if data.get('reply_markup') is None:
    #         data['reply_markup'] = {}
    #     if data['reply_markup'].get('inline_keyboard') is None:
    #         data['reply_markup']['inline_keyboard'] = []
    #     data['reply_markup']['inline_keyboard'].append([see_user_button])
    # if send_message_button:
    #     if data.get('reply_markup') is None:
    #         data['reply_markup'] = {}
    #     if data['reply_markup'].get('inline_keyboard') is None:
    #         data['reply_markup']['inline_keyboard'] = []
    #     data['reply_markup']['inline_keyboard'].append([send_message_button])
        


    print('data to be sent')
    print(data)

    # {
    #     'inline_keyboard': [[{'text': 'Send Message', 'url': 'https://t.me/c/1610051836/624474'}, 
    #                 {'text': 'See User', 'url': 'tg://user?id=1184644318'}]]
    # }
    try:
        resp = requests.post(f"{BOT_URL}/sendMessage", json=data)
        print('Message status:',resp.json())
        if resp.json()['ok']==True:
            print('message sent successfully')
            remove_from_failed_messages(data['chat_id'], data['text'], inline_keyboard)
        else:
            print('Failed to send a message')
            print(resp.json())
            add_to_failed_messages(data['chat_id'], data['text'], inline_keyboard, resp.json())
    except Exception as e:
        print('Network error')
        print(str(e))
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
    print('Resending failed messages')
    failed_messages = FailedMessage.objects.all()
    for fm in failed_messages:
        try:
            print('chat_id', fm.chat_id)
            print('text', fm.text)
            print('inline_keyboard', fm.inline_keyboard)
            send_message(fm.chat_id, fm.text, ast.literal_eval(fm.inline_keyboard))
        except Exception as e:
            print('Failed to sending again:', e)
            fm.error_message = str(e)
            fm.save()
    print('Resending failed messages is done')


def generate_text_to_send(message, keyword):
    text = get_full_text(message)
    text_to_send = f"{text}\nKeyword: {keyword}"
    return text_to_send


def generate_inline_keyboard(get_message_button, get_user_button):
    inline_keyboard = [[]]
    if get_message_button:
        inline_keyboard[0].append(get_message_button)
    if get_user_button:
        inline_keyboard[0].append(get_user_button)

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
    if len(parts)>=0:
        return parts[0]
    else:
        return ''


def get_user_link(message):
    user_link = None
    if message is None:
        return user_link
    entities = message.get('entities')
    if entities is None:
        return user_link
    for entity in entities:
        if 'url' in entity:
            if 'user?id=' in entity['url']:
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
            print('last read update id was added to database:', update_id)
        except:
            print('error when adding new update_id to database:', update_id)
    else:
        last_read.update_id = update_id
        try:
            last_read.save()
            print('last read update id updated in database:', update_id)
        except:
            print('error when updating update_id to database:', update_id)


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