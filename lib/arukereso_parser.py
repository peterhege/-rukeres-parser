import hashlib
import json
import os
import re
import time
from datetime import datetime

import requests
from functools import reduce
from typing import Union, List, Dict
from lxml import html

from lib.parser import phone
from lib.property_dictionaries import translate, missing_keys, DEFAULT_DICT, dictionaries, dict_values

if not os.path.exists('cache'):
    os.mkdir('cache')
if not os.path.exists('results'):
    os.mkdir('results')

PARSERS = {
    'Mobiltelefon': {'parser': phone, 'dict': 'phone'}
}

cache = {}
result = {}
for_ratings = {}


if os.path.exists('cache/cache.json'):
    with open('cache/cache.json', 'r', encoding='utf-8') as f:
        cache = json.load(f)


def parse(list_urls: Union[str, list]):
    list_url = list_urls if type(list_urls) == str else list_urls.pop(0)
    tree = get_tree(list_url)

    try:
        product_urls = tree.xpath('//*[contains(@class,"product-box-container")]//h2/a/@href')
        parse_products(product_urls)
    except Exception as e:
        print('{}: {}'.format(type(e), e))

    if type(list_urls) == str:
        list_urls = get_pages(tree)

    if list_urls:
        parse(list_urls)
    else:
        with open('cache/cache.json', 'w', encoding='utf-8') as f:
            json.dump(cache, f)
        with open('cache/missing_keys.json', 'w', encoding='utf-8') as f:
            json.dump(missing_keys, f, ensure_ascii=False)

        dir_name = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        for category, products in result.items():
            save_result(category, products, dir_name)


def parse_products(product_urls: List[str]):
    for_rating = {
        'rating': {'w': 1, 't': True},
        'rating_count': {'w': 1, 't': True},
        'rating_count_1': {'w': 3, 't': False},
        'rating_count_2': {'w': 2, 't': False},
        'rating_count_3': {'w': 1, 't': True},
        'rating_count_4': {'w': 2, 't': True},
        'rating_count_5': {'w': 3, 't': True},
        'shop_rating': {'w': 1, 't': True},
        'shop_rating_count': {'w': 1, 't': True},
        'shop_well': {'w': 1, 't': True},
        'price': {'w': 1, 't': False},
        'shipping': {'w': 1, 't': False},
    }
    for product_url in product_urls:
        try:
            data = parse_product(product_url)

            category = 'Ismeretlen'
            if data['category'] in PARSERS:
                category = data['category']

            if category not in for_ratings:
                for_ratings[category] = for_rating
                if category in PARSERS:
                    for_ratings[category].update(PARSERS[data['category']]['parser'].for_rating)

            if category not in result:
                result[category] = []

            set_min_max(data, category)

            for price_data in data['prices']:
                data.update(price_data)
                result[category].append(data.copy())

        except Exception as e:
            print('{}: {}'.format(type(e), e))


def set_min_max(data: dict, category: str):
    for key in for_ratings[category].keys():
        if key not in data:
            continue
        if 'min' not in for_ratings[category][key] or for_ratings[category][key]['min'] > data[key]:
            for_ratings[category][key]['min'] = float(data[key])
        if 'max' not in for_ratings[category][key] or for_ratings[category][key]['max'] < data[key]:
            for_ratings[category][key]['max'] = float(data[key])


def parse_product(product_url: str) -> dict:
    print('Parse:', product_url)
    cache_key = hashlib.md5(product_url.encode('utf-8')).hexdigest()
    if cache_key in cache and (time.time() - cache[cache_key]['last']) < 24 * 3600:
        return cache[cache_key]['data']

    tree = get_tree(product_url)

    brand = tree.xpath('//h1/*[@itemprop="brand"]/span/text()')
    name = tree.xpath('//h1/*[@itemprop="name"]/text()')
    category = tree.xpath('//h1/text()')  # type: List[str]
    rating_count = tree.xpath('//*[@itemprop="reviewCount"]/text()')
    rating = tree.xpath('//*[@itemprop="aggregateRating"]/meta[@itemprop="ratingValue"]/@content')
    ratings = get_ratings(tree.xpath('//*[contains(@class,"opinions-by-rating")]'), tree)

    data = {
        'brand': brand[0] if brand else '',
        'name': name[0] if name else '',
        'category': category[-1].strip() if len(category) > 1 else '',
        'url': product_url,
        'rating': float(rating[0]) if rating else 0,
        'rating_count': int(rating_count[0]) if rating_count else 0
    }

    if ratings:
        for stars, count in ratings.items():
            data['rating_count_{}'.format(stars)] = count

    product_properties = tree.xpath('//table[contains(@class,"property-sheet")]')  # type: html.HtmlElement
    if not len(product_properties):
        product_properties = tree.xpath('//table[contains(@class,"product-properties")]')
    product_properties = reduce(
        lambda a, b: a.xpath('.//tr') + b.xpath('.//tr'),
        product_properties
    )  # type: List[html.HtmlElement]
    product_properties = reduce(properties_reduce, product_properties)  # type: dict

    if data['category'] in PARSERS:
        data = translate(product_properties, data, PARSERS[data['category']]['dict'])
        PARSERS[data['category']]['parser'].parse(data)

    for key, value in data.items():
        if value in ['Igen', 'Van']:
            data[key] = True
        elif value in ['Nem', 'Nincs']:
            data[key] = False

    data['prices'] = []
    price_blocks = tree.xpath('//*[@id="offer-list"]//*[contains(@class,"optoffer")]')  # type: List[html.HtmlElement]
    for price_block in price_blocks:
        shop_name = price_block.xpath('.//*[contains(@class,"shopname")]/text()')
        price = price_block.xpath('.//*[contains(@class,"row-price")]/span/@content')
        if not shop_name or not price:
            continue

        shop_rating = len(price_block.xpath('.//*[@class="star icon-star"]'))
        if len(price_block.xpath('.//*[@class="star icon-star-half-alt"]')):
            shop_rating += .5

        shop_rating_count = price_block.xpath('.//*[contains(@class,"reviews-count")]//text()')
        if shop_rating_count:
            shop_rating_count = re.search(r'[0-9]+', shop_rating_count[0])

        shipping = price_block.xpath('.//*[@data-title="Szállítási költség"]/text()')

        shop_trusted = price_block.xpath('.//img[contains(@src,"trusted-flat")]')
        shop_well = price_block.xpath('.//img[contains(@src,"well-flat")]')

        price_data = {
            'shop_name': shop_name[0],
            'shop_rating': shop_rating,
            'shop_rating_count': int(shop_rating_count.group(0)) if shop_rating_count else 0,
            'shop_well': 1 if shop_well else (.5 if shop_trusted else 0),
            'price': float(price[0]),
            'shipping': float(re.search(r'[0-9]+', shipping[0].replace(' ', '')).group(0)) if shipping else 0
        }
        data['prices'].append(price_data)

    cache[cache_key] = {'data': data, 'last': time.time()}
    return data


def properties_reduce(properties: Union[html.HtmlElement, dict], tr: html.HtmlElement) -> dict:
    if type(properties) == html.HtmlElement:
        _tr = properties
        properties = parse_property_tr(_tr, {})
    return parse_property_tr(tr, properties)


def parse_property_tr(tr: html.HtmlElement, properties: dict) -> dict:
    try:
        true_value = tr.xpath('.//*[contains(@class,"icon-ok")]')
        false_value = tr.xpath('.//*[contains(@class,"icon-cancel")]')
        texts = [td.strip() for td in tr.xpath('./td//text()') if td.strip()]
        if len(texts) > 1:
            properties[texts[0]] = texts[1] if len(texts[1:]) == 1 else [text.replace('\xa0', '') for text in texts[1:]]
        elif len(true_value):
            properties[texts[0]] = True
        elif len(false_value):
            properties[texts[0]] = False
    except Exception as e:
        print('{}: {}'.format(type(e), e))

    return properties


def save_result(category: str, products: list, dir_name: str):
    file_name = 'unknown'
    property_dict = DEFAULT_DICT
    os.mkdir('results/{}'.format(dir_name))

    if category in PARSERS:
        file_name = PARSERS[category]['dict']
        property_dict.update(dictionaries[PARSERS[category]['dict']])

    file_name = 'results/{}/{}.txt'.format(dir_name, file_name)

    property_dict = dict_values(property_dict)

    with open(file_name, 'w', encoding='utf-8') as f:
        f.write('{}\n'.format(','.join(['"{}"'.format(name.replace('"', "'")) for name in property_dict.values()])))
        for product in products:
            add_result_row(product, property_dict, f)


def add_result_row(data: dict, property_dict: dict, f):
    data['calculated_rating'] = calculate(data, for_ratings[data['category']])
    buffer = []
    for key in property_dict.keys():
        value = data[key] if key in data else ''
        if type(value) == list:
            value = '|'.join(value)
        if type(value) == bool:
            value = 1 if value else 0
        buffer.append(value)
    f.write('{}\n'.format(','.join(['"{}"'.format(str(value).replace('"', "'")) for value in buffer])))


def calculate(data: dict, for_rating: dict) -> float:
    values = []
    for key, info in for_rating.items():
        if key not in data or 'min' not in info or 'max' not in info:
            continue
        diff = info['max'] - info['min']

        value = (data[key] - info['min']) / diff if diff else 1
        if not info['t']:
            value = 1 - value

        # if value == 0 and '{} {}'.format(key, data['url']) not in [
        #     'rating https://www.arukereso.hu/mobiltelefon-c3277/xiaomi/redmi-note-11-128gb-4gb-ram-dual-p763881576/',
        #     'rating_count https://www.arukereso.hu/mobiltelefon-c3277/xiaomi/redmi-note-11-128gb-4gb-ram-dual-p763881576/',
        #     'shop_well https://www.arukereso.hu/mobiltelefon-c3277/xiaomi/redmi-note-11-128gb-4gb-ram-dual-p763881576/',
        #     'rating_count_3 https://www.arukereso.hu/mobiltelefon-c3277/xiaomi/redmi-note-10-5g-64gb-4gb-ram-dual-p665366232/',
        #     'shop_rating https://www.arukereso.hu/mobiltelefon-c3277/xiaomi/redmi-note-10-5g-64gb-4gb-ram-dual-p665366232/',
        #     'shop_rating_count https://www.arukereso.hu/mobiltelefon-c3277/xiaomi/redmi-note-10-5g-64gb-4gb-ram-dual-p665366232/'
        # ] and key not in ['shop_well', 'shipping', 'screen_technology_for_rating']:
        #     print(key, data['url'], data[key], info['min'], info['max'])
        #     exit()

        for i in range(info['w']):
            values.append(value)
    return sum(values) / len(values) if values else 0


def get_ratings(ratings: List[html.HtmlElement], tree: html.HtmlElement) -> Union[Dict[int, int], None]:
    if ratings:
        ratings = ratings[0].xpath('.//*[contains(@class,"rating-sum")]/*/text()')
        return dict(zip(list(range(len(ratings) - 1, 0, -1)), [int(ratings[i]) for i in range(1, len(ratings))]))
    return None


def get_tree(page_url) -> html.HtmlElement:
    page = requests.get(page_url)
    return html.fromstring(page.content)


def get_pages(tree: html.HtmlElement) -> List[str]:
    try:
        pagination = tree.xpath('//*[contains(@class,"pagination")]')[0]  # type: html.HtmlElement
        pages = pagination.xpath('./a/@href')
        return pages
    except Exception as e:
        print('{}: {}'.format(type(e), e))
        return []
