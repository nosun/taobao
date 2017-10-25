# coding=utf-8

if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import json
import codecs
from taobao.mysql_helper import MysqlHelper


def t_get_product():
    db = MysqlHelper()
    products = db.get_products()
    for p in products:
        images = p['images']
        s = images.replace("\\", "").replace("\'", "\"")
        s = json.loads(s)
        print(s[1]['sku'])


if __name__ == '__main__':
    t_get_product()
