from telethon import TelegramClient, events

# Replace with your API ID, API Hash, and bot token
api_id = 123456  # Your Telegram API ID
api_hash = 'your_api_hash'  # Your Telegram API Hash
bot_token = 'YOUR_BOT_TOKEN'  # Your bot token

# Replace with the username of your bot
username = '@your_bot_username'

# Replace with the chat ID of the open group (use a negative value)
group_chat_id = -1234567890

async def main():
  async with TelegramClient(username, api_id, api_hash) as client:
    @client.on(events.NewMessage(chat=group_chat_id))
    async def handle_message(event):
      # Access message content
      message_text = event.text

      # Do something with the message (e.g., print or store)
      print(f"Received message: {message_text}")

      # Optionally, reply to the message
      # await event.reply(message_text)

    # Start listening for messages
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
  import asyncio
  asyncio.run(main())
