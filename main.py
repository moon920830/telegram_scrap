import asyncio
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import PeerFloodError
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import InputPeerChannel

api_id = 24197053
api_hash = 'bca24709b49d903f928503346d0315ae'
phone = '+212616104490'

group_url = 'https://t.me/KillersCalls69'
channel_username = 'KillersCalls69'

async def scrape_messages(client):
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    entity = await client.get_entity(channel_username)
    print("hello world")
    limit = 1000

    try:
        message_count = 0
        with open('output.txt', 'w', encoding='utf-8') as f:

            max_iterations = 10  # Set a limit on the number of times to retrieve messages
            iteration_count = 0

            while iteration_count < max_iterations:
                try:
                    messages = await client(GetHistoryRequest(
                        peer=entity,
                        offset_id=0,
                        offset_date=None,
                        add_offset=0,
                        limit=limit,
                        max_id=0,
                        min_id=0,
                        hash=0
                    ))
                except PeerFloodError:
                    print("Getting flooded, sleeping for 5 seconds...")
                    await asyncio.sleep(5)
                    continue
                
                if not messages.messages:
                    break

                for message in messages.messages:
                    text = message.message
                    if text:
                        f.write(text + '\n')
                        message_count += 1

                iteration_count += 1

        print(f'Successfully scraped {message_count} messages '
              f'from entity "{entity.username or entity.phone}"'
              f'and wrote them to file')
    # Add a KeyboardInterrupt exception handler here:
    except KeyboardInterrupt:
        await client.disconnect()
        print('\nProgram stopped by user.')
        raise KeyboardInterrupt

    except Exception as e:
        print(e)
        print('Error writing to file. Terminating program.')
        await client.disconnect()
        return

    await client.disconnect()
    print('Successfully logged {message_count} messages to telegram_log.txt')

client = TelegramClient(phone, api_id, api_hash)

loop = asyncio.get_event_loop()
loop.run_until_complete(scrape_messages(client))
