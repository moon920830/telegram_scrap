import asyncio
import re
import pymongo
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import PeerFloodError
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import InputPeerChannel
from telethon.tl.functions.users import GetFullUserRequest


class MessageScraper:
    def __init__(self, api_id, api_hash, phone_number, channel_username):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.channel_username = channel_username
        self.client = TelegramClient(phone_number, api_id, api_hash)
        self.scrape_limit = 1000

    async def __aenter__(self):
        await self.client.connect()
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Enter the code: '))
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.disconnect()

    async def scrape_messages(self, max_iterations=10):
        entity = await self.client.get_entity(self.channel_username)
        message_count = 0
        limit = self.scrape_limit

        db = MongoDatabase('mydatabase', 'mycollection')

        iteration_count = 0
        while iteration_count < max_iterations:
            try:
                messages = await self.client(GetHistoryRequest(
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
                if  message.from_id:
                    user_id = message.from_id.user_id
                    user_info = await self.client(GetFullUserRequest(message.from_id.user_id))

                    sender_username = user_info.user.username or ""
                else:
                    user_id = "messages from service"
                    sender_username = ""

                text = message.message
                caller_chat_id = message.id
                caller_call_date = message.date
                alpha_group = self.channel_username
                coin_links, social_links = [], []
                if text:
                    # Extract the required fields using regular expressions
                    contract_address = re.findall(r"0x[a-fA-F0-9]{40}", text)
                    link_dextools = re.findall(r".*https://www\.dextools\.io.*", text)
                    link_dexscreener = re.findall(r".*https://www\.dexscreener\.com.*", text)
                    link_coinmarketcap = re.findall(r".*https://www\.coinmarketcap\.com.*", text)
                    link_twitter = re.findall(r".*https://www\.twitter\.com.*", text)
                    link_facebook = re.findall(r".*https://www\.facebook\.com.*", text)

                    # Add the extracted links to the appropriate list
                    if link_twitter or link_facebook or contract_address or link_dextools or link_dexscreener or link_coinmarketcap:
                        coin_links.extend(contract_address + link_dextools + link_dexscreener + link_coinmarketcap)
                        social_links.extend(link_twitter + link_facebook)
                        document = document_schema.copy()
                        document["telegram_id"] = user_id
                        document["user_name"] = sender_username
                        document["alpha_group"] = alpha_group
                        document["caller_chat_id"] = caller_chat_id
                        document["caller_call_date"] = caller_call_date
                        document["raw_chat"] = text
                        document["coin_links"] = coin_links
                        document["social_links"] = social_links

                        # Insert the document into MongoDB
                        result = db.insert_one(document)
                        if result:
                            message_count += 1

            iteration_count += 1

        print(f'Successfully scraped {message_count} messages '
              f'from entity "{entity.username or entity.phone}"'
              f' and wrote them to MongoDB')

        return message_count

# Define the document schema
document_schema = {
    "telegram_id": "",
    "user_name": "",
    "alpha_group": "",
    "caller_chat_id": "",
    "caller_call_date": "",
    "raw_chat": "",
    "coin_links": [],
    "social_links": []
}

class MongoDatabase:
    def __init__(self, database_name, collection_name):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]

    def insert_one(self, document):
        result = self.collection.insert_one(document)
        return result.acknowledged

async def run_scraper():
    api_id = 24197053
    api_hash = 'bca24709b49d903f928503346d0315ae'
    phone_number = '+212616104490'
    channels = ['KillersCalls69', 'BRENTLYSROYALS', 'Chad_Crypto', 'maythouscalls']
    message_count = 0

    for channel in channels:
        async with MessageScraper(api_id, api_hash, phone_number, channel) as scraper:
            message_count += await scraper.scrape_messages()

    if message_count > 0:
        print("Successfully inserted documents into MongoDB")
    else:
        print("No messages were scraped")


# Run the scraper
asyncio.run(run_scraper())
