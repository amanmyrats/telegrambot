import time
import requests

from django.conf import settings
from django.shortcuts import render

from premiumgroups.models import (
    PremiumGroup, SectorKeyword, LocationKeyword
)
from .models import LastRead


BOT_URL = f'{settings.TELEGRAM_BOT_URL}{settings.TELEGRAM_TOKEN}'


def keep_fetching():
    print('start fetching')
    while True:
        time.sleep(2)
        try:
            fetch_messages()
        except Exception as e:
            print('error when fetching', e)
            pass


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
    full_text = get_full_text(message)
    chat_title = get_chat_title(message)
    users_text = get_users_text(message)
    print('filtering')
    print('full_text:', full_text)
    print('chat_title:', chat_title)
    print('users_text:', users_text)

    if message is None or full_text is None:
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
                    result['update_id']
                    )


def send_message(chat_id, text_to_send, update_id):
    print('sending message')
    print(f"{BOT_URL}/sendMessage?chat_id={chat_id}&text={text_to_send}")
    resp = requests.get(f"{BOT_URL}/sendMessage?chat_id={chat_id}&text={text_to_send}")
    print('Message sent or not:',resp.json)
    if resp.json()['ok']==True:
        print('message sent successfully')
    else:
        # TODO
        # if messages is failed to send, then save it to database
        # later every time fetch_messages begins, then send unsend messages first
        print('Failed to send a message')


def generate_text_to_send(message, keyword):
    chat_title = get_chat_title(message)
    sender_username = get_sender_username(message)
    sender_fullname = get_sender_fullname(message)
    text = get_full_text(message)
    text_to_send = f"Chat:{chat_title}\n\
        username: @{sender_username}\n\
        Name: {sender_fullname}\n\
        \n\
        Keyword: {keyword}\n\
        \n\
        {text}\
        "
    return text_to_send


def get_full_text(message):
    text = message.get('text')
    if text is None:
        text = message.get('caption')
    if text is None:
        return ''
    return text


def get_users_text(message):
    text = get_full_text(message)
    if text is None:
        return ''
    parts = text.split('\n')
    if len(parts)>1:
        return ' '.join(parts[2:])
    else:
        return text
    

def get_chat_title(message):
    text = get_full_text(message)
    if text is None:
        return ''
    parts = text.split('\n')
    if len(parts)>=0:
        return parts[0]
    else:
        return ''

def get_user_link(message):
    entities = message.get('entities')
    if entities is None:
        return ''
    for entity in entities:
        if 'url' in entity:
            if 'user?id=' in entity['url']:
                return entity['url']


def get_message_link(message):
    entities = message.get('entities')
    if entities is None:
        return ''
    for entity in entities:
        if 'url' in entity:
            if '//t.me/c/' in entity['url']:
                return entity['url']

def get_sender_username(message):
    # forward_origin
    text = get_full_text(message)
    if text is None:
        return ''
    parts = text.split('\n')
    if len(parts)>0:
        return parts[1]
    else:
        return ''


def get_sender_fullname(message):
    # forward_origin
    fullname = ''
    first_name = ''
    last_name = ''
    sender = None
    if 'forward_origin' in message:
        sender = message.get('forward_origin').get('sender_user')
    else:
        sender = message.get('from')
    if sender is None:
        return ''
    first_name = sender.get('first_name')
    last_name = sender.get('last_name')

    if first_name is not None:
        fullname += first_name
    if last_name is not None:
        if fullname: 
            fullname += " "
        fullname += last_name
    return fullname


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


# {
#     "ok":true,
#     "result":[
#         {
#         "update_id":963437181,
#         "message":
#             {
#             "message_id":18,
#             "from":{"id":6613204121,"is_bot":false,"first_name":"Aman","username":"amanmyrats"},
#             "chat":{"id":-4143214173,"title":"Toplu mesajlar","type":"group","all_members_are_administrators":true},
#             "date":1710919342,"text":"Test"
#             }
#         },
#         {
#             "update_id":963437182,
#             "message":
#                 {
#                   "message_id":19,
#                   "from":{"id":6613204121,"is_bot":false,"first_name":"Aman","username":"amanmyrats"},
#                   "chat":{"id":-4143214173,"title":"Toplu mesajlar","type":"group","all_members_are_administrators":true},
#                   "date":1710919352,
#                   "text":"Test2"
#                 }
#         }
#     ]
# }

