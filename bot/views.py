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
    offset=int(LastRead.objects.all().first().update_id) + 1
    params={}
    if offset is not None:
        params={'offset':offset}
        
    response = requests.get(f"{BOT_URL}/getUpdates", params=params)
    print(response.json())
    data = response.json()
    for result in data['result']:
        for k,v in result.items():
            print(k, ':',v)
        print('--------')
        filter(result)
        update_last_read_message(result['update_id'])

    pass



def filter(result):
    try:
        message = result['message']
        text = result['message']['text'].lower()
        chat_title = result['message']['chat']['title']
    except:
        try:
            message = result['edited_message']
            text = result['edited_message']['text'].lower()
            chat_title = result['edited_message']['chat']['title']
            print('filtering', text)
        except:
            text = ''
    sector_keywords = SectorKeyword.objects.all()
    location_keywords = LocationKeyword.objects.all()
    for sector_keyword in sector_keywords:
        if sector_keyword.keyword.lower() in text:
            print('sector_keyword matches:', sector_keyword.keyword.lower())
            for location_keyword in location_keywords:
                # Here you have to catch chat title
                # Here you have to catch chat title
                # Here you have to catch chat title
                if location_keyword.keyword.lower() in text or \
                    location_keyword.keyword.lower() in chat_title.lower():
                    print('location_keyword matches:', location_keyword.keyword.lower())
                    pgs_to_send_message = list(
                        set(sector_keyword.sector.sector_pgs.all()) \
                            & \
                                set(location_keyword.location.location_pgs.all())
                    )
                    # if sector_keyword.sector.premium_group == location_keyword.city.premium_group:
                    for pg in pgs_to_send_message:    
                        print('sending filtered message')

                        send_message(
                            pg.chat_id, 
                            generate_text(message, sector_keyword), 
                            result['update_id']
                            )


def send_message(chat_id, text, update_id):
    print('sending message')
    print(f"{BOT_URL}/sendMessage?chat_id={chat_id}&text={text}")
    resp = requests.get(f"{BOT_URL}/sendMessage?chat_id={chat_id}&text={text}")
    print('Message sent or not:',resp.json)
    if resp.json()['ok']==True:
        print('message sent successfully')
        update_last_read_message(update_id)
    else:
        print('Failed to send a message')


def generate_text(message, keyword):
    text = f"Chat:{message['chat']['title']}\n\
        Sender:{message['from']['username']}\n\
        \n\
        Keyword: {keyword}\n\
        \n\
        {message['text']}\
        "
    return text


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

