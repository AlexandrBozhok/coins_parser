from typing import Any

import aiohttp
import logging
import motor.motor_asyncio
import re

from aiogram import Bot
from bs4 import BeautifulSoup, Tag
from pydantic import ValidationError

from config import settings
from schemas import Product
from utils import build_new_product_message


logging.basicConfig(level=logging.INFO)
bot = Bot(token=settings.bot_api_token)


async def get_page_soup_obj(url: str) -> BeautifulSoup:
    async with aiohttp.ClientSession() as session:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/89.0.4389.82 Safari/537.36'
        }
        async with session.get(url, headers=headers) as response:
            html = await response.text()
            return BeautifulSoup(html, 'html.parser')


async def get_pagination_urls() -> list[str]:
    shop_page_1_url = f'{settings.nbu_shop_base_url}catalog.html'
    soup = await get_page_soup_obj(shop_page_1_url)
    main_block = soup.find('div', {'id': 'block'})
    pagination = main_block.find('ul', {'class': 'pagination'}).find_all('a')

    urls = list({f'{settings.nbu_shop_base_url}{item["href"]}' for item in pagination})
    urls.insert(0, shop_page_1_url)
    return urls


def parse_product(product_tag: Tag) -> dict[str, Any]:
    data = {}
    name_tag = product_tag.find('a', {'class': 'model_product'})
    if name_tag:
        name = name_tag.text.strip()
        data['name'] = name

    price_tag = product_tag.find('span', {'class': 'new_price'})
    if price_tag:
        price = re.search(r'^\d+', price_tag.text.replace(' ', ''))
        if price:
            price = price.group(0)
            data['price'] = price

    url_tag = product_tag.find('a', {'class': 'p_img_href'})
    if url_tag:
        url = f'{settings.nbu_shop_base_url}{url_tag["href"].lstrip("/")}'
        data['url'] = url

    image_url = product_tag.find('a', {'class': 'p_img_href'}).find('img')
    if image_url:
        image_url = image_url['data-src']
        data['image_url'] = image_url

    coin_params = product_tag.find('div', {'class': 'product_bank_parameters'}).find_all('p')
    if coin_params:
        material = ''
        year_of_production = coin_params[-1].text
        circulation = coin_params[-2].text
        if len(coin_params) == 3:
            material = coin_params[0].text

        data['material'] = material
        data['year_of_production'] = year_of_production
        data['circulation'] = circulation
    return data


async def get_products_from_page(url: str) -> list[Product]:
    soup = await get_page_soup_obj(url=url)
    items = soup.find('div', {'class': 'row_catalog_products'}).find_all('div', {'class': 'product'})

    products = []
    for item in items:
        product_data = parse_product(item)
        try:
            products.append(Product(**product_data))
        except ValidationError as e:
            error_data = e.errors()[0]
            logging.error(f'Validation error. Field: {error_data.get("loc")}. Message: {error_data.get("msg")}.\n'
                          f'Product data: {product_data}')
    return products


async def find_new_products(products: list[Product]) -> list[Product]:
    collection = await get_coins_collection()
    new_products = []
    for product in products:
        result = await collection.find_one({'url': product.url})
        if not result:
            msg = build_new_product_message(product)
            await bot.send_message(chat_id=settings.chat_id, text=msg)
            new_products.append(product)
    return new_products


async def main():
    shop_urls = await get_pagination_urls()
    products = []
    for url in shop_urls:
        result = await get_products_from_page(url)
        products.extend(result)
    logging.info(f'Product count on shop: {len(products)}')
    new_products = await find_new_products(products)
    if new_products:
        collection = await get_coins_collection()
        result = await collection.insert_many([item.dict() for item in new_products])
        logging.info('Added new products %s' % repr(result.inserted_ids))
    else:
        logging.info('The script has completed work. No new coins were added')


async def get_coins_collection():
    conn_str = "mongodb+srv://%s:%s@%s/?retryWrites=true&w=majority" % (
        settings.db_user, settings.db_password, settings.db_host
    )
    client = motor.motor_asyncio.AsyncIOMotorClient(conn_str, serverSelectionTimeoutMS=5000)
    db = client['coins-db']
    collection = db.coins
    return collection