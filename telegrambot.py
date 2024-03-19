from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel
import re

# Telegram API credentials
api_id = '7156890309'
api_hash = 'AAFOhkmgYUK4uo23NsK_KsCTrl-eSjZahFw'
phone = '0099365493616'

# Define the list of groups to scrape from
groups_to_scrape = [
    -4143214173,   # Group ID 1 to scrape from
    # Add more group IDs as needed
]

# Keywords and corresponding group IDs to forward messages to
keyword_groups = {
    'emlak': -4182513036,   # Group ID where messages with 'emlak' will be forwarded
    'transfer': -4143899596,   # Group ID where messages with 'transfer' will be forwarded
    # Add more mappings as needed
}

def categorize_message(message):
    # Implement your message categorization logic here
    for keyword, group_id in keyword_groups.items():
        if re.search(r'\b{}\b'.format(keyword), message, re.IGNORECASE):
            return keyword, group_id
    return None, None

def scrape_and_forward():
    print('starting scrape_and_forward')
    print('starting scrape_and_forward')
    print('starting scrape_and_forward')
    with TelegramClient(phone, api_id, api_hash) as client:
        print('inside with')
        print('inside with')
        print('inside with')
        for group_to_scrape in groups_to_scrape:
            try:
                messages = client.get_messages(group_to_scrape, limit=10)  # Adjust the limit as needed
                print('messages:', messages)
                for message in messages:
                    text = message.message
                    keyword_found, forward_group = categorize_message(text)
                    if keyword_found and forward_group:
                        client.forward_messages(forward_group, message)
            except Exception as e:
                print(f"Error processing group {group_to_scrape}: {e}")

if __name__ == "__main__":
    scrape_and_forward()