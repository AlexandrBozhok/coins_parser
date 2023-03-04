import asyncio
import datetime
import time

import logging
import motor.motor_asyncio

from aiogram import Bot

from config import settings
from product_parser import ProductParser
from schemas import Product
from utils import build_new_product_message, get_known_product_message

logging.basicConfig(level=logging.INFO)
bot = Bot(token=settings.bot_api_token)


async def find_new_products(products: list[Product]) -> list[Product]:
    collection = await get_coins_collection()
    product_ids = [product.bank_product_id for product in products]
    cursor = collection.find({'bank_product_id': {'$in': product_ids}}, {'bank_product_id': 1, '_id': 0})
    found_products_ids = [item['bank_product_id'] async for item in cursor]
    return [item for item in products if item.bank_product_id not in found_products_ids]


async def update_sold_products():
    collection = await get_coins_collection()
    await collection.update_many({'updated': {'$lt': datetime.datetime.now() - datetime.timedelta(minutes=5)}},
                                 {'$set': {'sold_out': True}})


async def main():
    parser = ProductParser()
    products = await parser.get_all()
    logging.info(f'Founded product in catalog: {len(products)}')
    product_ids = [product.bank_product_id for product in products]
    collection = await get_coins_collection()
    new_products = await find_new_products(products)

    for product in new_products:
        msg = build_new_product_message(product)
        await bot.send_message(chat_id=settings.chat_id, text=msg, parse_mode='HTML')

    # Якщо товар є в каталозі сайту, а в базі він sold_out=True - змінюємо його статус
    # і відправляємо сповіщення в бот
    async for item in collection.find({'bank_product_id': {'$in': product_ids}, 'sold_out': True}):
        msg = get_known_product_message(Product(**item))
        await bot.send_message(chat_id=settings.chat_id, text=msg, parse_mode='HTML')
        await collection.update_one({'_id': item['_id']}, {'$set': {'sold_out': False}})

    # Оновлюємо поле updated для тих товарів, які є в каталозі
    await collection.update_many({'bank_product_id': {'$in': product_ids}},
                                 {'$set': {'updated': datetime.datetime.now()}})

    await update_sold_products()
    if new_products:
        await collection.insert_many([item.dict() for item in new_products])
        logging.info('Added new products %s' % [item.name for item in new_products])
    else:
        logging.info('The script has completed work. No new coins were added')


async def get_coins_collection():
    conn_str = "mongodb+srv://%s:%s@%s/?retryWrites=true&w=majority" % (
        settings.db_user, settings.db_password, settings.db_host
    )
    client = motor.motor_asyncio.AsyncIOMotorClient(conn_str, serverSelectionTimeoutMS=5000)
    db = client['coins-db']
    collection = db[settings.db_collection]
    return collection

if __name__ == '__main__':
    t = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    print(f'TIME: {time.time() - t}')
