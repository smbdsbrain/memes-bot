import asyncio
import re
import urllib.request

import motor.motor_asyncio
from aiotg import Bot, os, logging
from aiovk import API, TokenSession


async def run(config):
    interval = int(config.interval)
    client = motor.motor_asyncio.AsyncIOMotorClient(config.mongo_url)
    db = client.memes_db
    collection = db.test_collection
    session = TokenSession(config.vk.token)
    api = API(session)

    bot = Bot(api_token=config.token, proxy=config.proxy['proxy_url'])
    channel = bot.channel("@MemesAggregation")

    while True:
        logging.info('Start checking groups')
        for group in config.vk.groups:
            asyncio.sleep(1)
            r = await api('wall.get', domain=group)
            for item in r['items']:
                if len(item['attachments']) == 1 and item['marked_as_ads'] == 0 and item['attachments'][0]['type'] == 'photo':
                    url = item['attachments'][0]['photo']['photo_604']
                    name = re.findall('(?=\w+\.\w{3,4}$).+', url)[0]
                    if await collection.find_one({'name': name}) is None:
                        logging.info('Found new meme')
                        collection.insert_one({'name': name})
                        # TODO: Make it async
                        urllib.request.urlretrieve(url, f"data/images/{name}")
                        await channel.send_photo(photo=open(f"data/images/{name}", "rb"))
                        os.remove(f"data/images/{name}")

        logging.info('Groups checked, waiting for next time...')
        await asyncio.sleep(interval)
