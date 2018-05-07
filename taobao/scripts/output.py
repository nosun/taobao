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

head = list()


def get_choice(choices, type):
    choices = format_data(choices)
    choices = json.loads(choices)
    prices = set()
    for choice in choices:
        prices.add(choice['price'])
    prices = ','.join(prices)
    return prices


def get_property_keys():
    db = MysqlHelper()
    products = db.get_products()
    all_keys = set()
    for p in products:
        try:
            properties = format_data(p['properties'])
            properties = json.loads(properties)
            keys = properties.keys()
            for k in keys:
                all_keys.add(k)
        except Exception as e:
            print(p['id'])
            print(p['properties'])
    return all_keys


def format_data(properties):
    s = properties.replace("\\", "").replace("\'", "\"")
    return s


def write_head(file_path):
    global head
    head = ["1-sn", "2-title", "3-price", "4-prices", "5-colors", "6-sizes", "7-url", "8-shop_name", "9-shop_url"]
    attrs = list(get_property_keys())
    head = sorted(head + attrs)
    write_list_to_csv([head], file_path)


def format_line():
    line = dict()
    for k in head:
        line[k] = ''
    return line


def list_to_string(l):
    l = json.loads(l)
    return ",".join(l)


def main():
    file_path = os.path.join(DATA_PATH, 'products_tmall.csv')
    write_head(file_path)

    db = MysqlHelper()
    shops = db.get_tmall_shops()
    for shop in shops:
        products = db.get_products_by_shop(shop['id'])
        for product in products:
            line = format_line()
            line['1-sn'] = product['sn']
            line['2-title'] = product['title']
            line['3-price'] = product['price']
            line['4-prices'] = list_to_string(format_data(product['prices']))
            line['5-colors'] = list_to_string(format_data(product['colors']))
            line['6-sizes'] = list_to_string(format_data(product['sizes']))
            line['7-url'] = product['url']
            line['8-shop_name'] = product['name']
            line['9-shop_url'] = product['task_url']
            properties = format_data(product['properties'])
            properties = json.loads(properties)
            for k, v in properties.items():
                line[k] = v.replace("\"", "")
            print(line)
            new_line = line.values()
            print(new_line)
            write_list_to_csv([new_line], file_path)


if __name__ == '__main__':
    main()

