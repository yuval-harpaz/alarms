"""collect Telegram messages for IDF."""

from telethon import TelegramClient
import telethon.sync
import os
import asyncio
local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    # with open('/home/innereye/alarms/oath.txt') as f:
    #     oauth = f.readlines()[0][:-1]
    with open('.txt') as f:
        lines = f.readlines()
else:
    oauth = os.environ['OAuth']
    cities_url = os.environ['cities_url']

api_id = lines[3][:-1]
api_hash = lines[4][:-1]
phone_number = lines[5][:-1]
channel_username ='idf_telegram'


client = TelegramClient('get_idf', api_id, api_hash)

client.connect()

async for message in client.iter_messages('me'):
    print((await client.get_me()).first_name)

loop = asyncio.get_event_loop()


loop.run_until_complete(my_async_def())











from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import GetHistoryRequest
import os
local = '/home/innereye/alarms/'
if os.path.isdir(local):
    os.chdir(local)
    # with open('/home/innereye/alarms/oath.txt') as f:
    #     oauth = f.readlines()[0][:-1]
    with open('.txt') as f:
        lines = f.readlines()
else:
    oauth = os.environ['OAuth']
    cities_url = os.environ['cities_url']

api_id = lines[3][:-1]
api_hash = lines[4][:-1]
phone_number = lines[5][:-1]
channel_username ='idf_telegram'
# client = TelegramClient('get_idf', api_id, api_hash)
# client.start()

# messages = client.get_messages('idf_telegram')


client = TelegramClient('get_idf',
                        int(api_id),
                        api_hash)
assert client.connect()
# if not client.is_user_authorized():
#     client.send_code_request(phone_number)
#     me = client.sign_in(phone_number, input('Enter code: '))

channel_entity=client.get_entity(channel_username)
posts = client(GetHistoryRequest(
    peer=channel_username,
    limit=100,
    offset_date=None,
    offset_id=0,
    max_id=0,
    min_id=0,
    add_offset=0,
    hash=0))


for message in client.get_messages(channel_username, limit=10):
    print(message.message)

async def fetch_messages(limit=None):
    # Connect to the client
    await client.start(phone_number)
    # Get the target chat (you can use chat ID or username)
    chat = await client.get_entity('idf_telegram')
    # Open a file to save messages
    with open('tmp.txt', 'w', encoding='utf-8') as f:
        # Iterate through all messages in the chat
        async for message in client.iter_messages(chat, limit):
            if message.text:  # Check if it's a text message
                f.write(message.text + '\n')

# Run the fetch messages function
with client:
    client.loop.run_until_complete(fetch_messages(10))


##
async def fetch_messages():
    # Use "async with" to connect the client properly in async context
    async with TelegramClient('session_name', api_id, api_hash) as client:
        # Start the client
        await client.start(phone_number)
        
        # Get the target chat (you can use chat ID or username)
        chat = await client.get_entity(chat_name)

        # Open a file to save messages
        with open('messages.txt', 'w', encoding='utf-8') as f:
            # Iterate through all messages in the chat
            async for message in client.iter_messages(chat, limit=None):
                if message.text:  # Check if it's a text message
                    f.write(message.text + '\n')

# Run the fetch_messages function
import asyncio
asyncio.run(fetch_messages())
