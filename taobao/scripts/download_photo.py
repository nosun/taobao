# coding:utf-8

if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import os
import json
from taobao.mysql_helper import MysqlHelper
from taobao.settings import IMG_PATH
import requests
import random
import time


def format_data(properties):
    s = properties.replace("\\", "").replace("\'", "\"")
    s = json.loads(s)
    return s


def mk_image_dir(sid):
    image_path = os.path.join(IMG_PATH, str(sid))
    if not os.path.isdir(image_path):
        os.mkdir(image_path)
    return image_path


def get_random_time(min_time=0, max_time=3):
    return random.randint(min_time, max_time)


def save_images(sn, images, image_path):
    i = 1
    for image in images:
        suffix = image.split(".")[-1]
        file_name = sn + "_" + str(i) + "." + suffix
        file_path = os.path.join(image_path, file_name)
        with open(file_path, "wb") as fs:
            try:
                rsp = requests.get(image)
                if rsp.status_code == 200:
                    fs.write(rsp.content)
                    print("download sn: %s image: %s ok" % (sn, image))
                    time.sleep(get_random_time(0, 5))
            except Exception as e:
                print("image download failed, sn is %s , and url is %s" % (sn, image))
                print(e)
        i += 1


def main():
    db = MysqlHelper()
    shops = db.get_shops_by_status('1')
    for shop in shops:
        image_path = mk_image_dir(shop['id'])
        products = db.get_products_by_shop(shop['id'])
        for product in products:
            images = format_data(product['images'])
            save_images(product['sn'], images, image_path)
        break


if __name__ == '__main__':
    main()
