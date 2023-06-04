Telegram Group Message Scraper
This is a Python script that scrapes messages from multiple Telegram channels and saves relevant data to a MongoDB database. The script uses the Telethon library to communicate with the Telegram API.

Dependencies
Python 3.x
Telethon library (pip install telethon)
PyMongo library (pip install pymongo)
Configuration
Before running the script, you need to configure the following variables in the run_scraper() function:

api_id: Your Telegram API ID (you can obtain this from the Telegram website)
api_hash: Your Telegram API hash (you can obtain this from the Telegram website)
phone_number: Your phone number in international format (e.g. +1234567890)
channels: A list of channel usernames that you want to scrape messages from
You also need to have a running instance of MongoDB on your local machine, or modify the MongoDatabase class to connect to a remote MongoDB server.

Usage
To run the scraper, simply execute the run_scraper() function. The script will authenticate with the Telegram API using your phone number, connect to the specified channels, and start scraping messages. Relevant data will be saved to a MongoDB database.

Note that if you run the script multiple times, it will not duplicate messages in the database - the script uses unique message IDs to ensure that messages are only added once.