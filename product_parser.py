import asyncio
import logging
import re
from typing import Any

import aiohttp
from bs4 import BeautifulSoup, Tag
from pydantic import ValidationError

from schemas import Product


class ProductParser:

    def __init__(self):
        self.bank_base_url = 'https://coins.bank.gov.ua/'
        self.catalog_page = self.bank_base_url + 'catalog.html'

    async def __get_page_text(self, url: str) -> str:
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/89.0.4389.82 Safari/537.36'
            }
            async with session.get(url, headers=headers) as response:
                result = await response.text()
                return result

    async def __scrap_page(self, url: str) -> BeautifulSoup:
        catalog_page_html = await self.__get_page_text(url)
        return BeautifulSoup(catalog_page_html, 'html.parser')

    def __get_pagination_urls(self, main_page: BeautifulSoup) -> list:
        pagination_urls = []
        try:
            main_block = main_page.find('div', {'id': 'block'})
            pagination = main_block.find('ul', {'class': 'pagination'})
            if pagination:
                pagination_items = pagination.find_all('a')
                pagination_urls = list({f'{self.bank_base_url}{item["href"]}' for item in pagination_items})
        except AttributeError:
            logging.error('Catalog page is unavailable. Main block with id=block not found.')

        return pagination_urls

    def __parse_product(self, product_tag: Tag) -> dict[str, Any]:
        data = {}
        try:
            bank_product_id = product_tag.select_one('.basked_product_bank .add2cart')
            data['bank_product_id'] = bank_product_id.get('data-id')

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
                url = f'{self.bank_base_url}{url_tag["href"].lstrip("/")}'
                data['url'] = url

            image_url = product_tag.find('a', {'class': 'p_img_href'}).find('img')
            if image_url:
                image_url = image_url['data-src']
                data['image_url'] = image_url

            coin_params = product_tag.find('div', {'class': 'product_bank_parameters'}).find_all('p')
            if coin_params:
                if len(coin_params) == 3:
                    data['material'] = coin_params[0].text
                    data['circulation'] = coin_params[1].text
                    data['year_of_production'] = coin_params[2].text
                else:
                    logging.info(f'Product {data["name"]} has problem with parsing params. '
                                 f'Coin_params: {coin_params}')
        except Exception as e:
            print(f'Error: {e}')

        return data

    async def get_products_from_page(self, page_scrap: BeautifulSoup) -> list[Product]:
        catalog_products = page_scrap.find('div', {'class': 'row_catalog_products'})
        if catalog_products:
            items = catalog_products.find_all('div', {'class': 'product'})
            # Обираємо тільки ті елементи, які є в наявності на сайті по класу "add2cart"
            items = [item for item in items if item.select_one('.basked_product_bank .add2cart')]
            products = []
            for item in items:
                product_data = self.__parse_product(item)
                try:
                    products.append(Product(**product_data))
                except ValidationError as e:
                    error_data = e.errors()[0]
                    logging.error(f'Validation error. Field: {error_data.get("loc")}. '
                                  f'Message: {error_data.get("msg")}.\n'
                                  f'Product data: {product_data}')
            return products

    async def get_all(self):
        main_page_soup = await self.__scrap_page(self.catalog_page)
        pagination_urls = self.__get_pagination_urls(main_page_soup)
        pages_soup = [main_page_soup]
        for url in pagination_urls:
            soup = await self.__scrap_page(url)
            pages_soup.append(soup)

        logging.info(f'Catalog page loaded. Pages count: {len(pages_soup)}')

        products = []
        for page in pages_soup:
            parsed_products = await self.get_products_from_page(page)
            products.extend(parsed_products)

        return products
