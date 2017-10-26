# coding:utf-8

if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import os
import json
from taobao.mysql_helper import MysqlHelper
from taobao.utils.csv import write_dict_to_csv
from taobao.utils.csv import write_list_to_csv
from taobao.settings import DATA_PATH


def get_choice(choices, type):
    choices = format_data(choices)
    # for k, v in choices.items():



def get_property_keys():
    db = MysqlHelper()
    products = db.get_products()
    all_keys = set()
    for p in products:
        properties = format_data(p['properties'])
        keys = properties.keys()
        for k in keys:
            all_keys.add(k)
    return all_keys


def format_data(properties):
    s = properties.replace("\\", "").replace("\'", "\"")
    s = json.loads(s)
    return s


def write_head(file_path):
    head = ("sn", "title", "price", "prices", "colors", "sizes", "url", "shop_name", "shop_url")
    attrs = get_property_keys()
    head = head + tuple(attrs)
    write_list_to_csv([head], file_path)


def main():
    file_path = os.path.join(DATA_PATH, 'products.csv')
    write_head(file_path)

    db = MysqlHelper()
    shops = db.get_shops_by_status('1')
    for shop in shops:
        products = db.get_products_by_shop(shop['id'])
        for product in products:
            line = dict()
            line['sn'] = product['sn']
            line['title'] = product['title']
            line['price'] = product['price']
            line['url'] = product['url']
            line['shop_name'] = product['shop_display_name']
            line['shop_url'] = product['task_url']
            # @todo attrs
            line['prices'] = get_choice(product['choices'], 'prices')
            line['color'] = get_choice(product['choices'], 'color')
            line['sizes'] = get_choice(product['choices'], 'size')
            line['attrs'] = get_attrs(product['properties'])


if __name__ == '__main__':
    main()
