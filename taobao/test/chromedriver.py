# -*- coding:utf-8 -*-  
""" 
@author: nosun 
@file: chromedriver.py
@time: 2017/10/29 
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree

if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from taobao.settings import CHROME_DRIVER_PATH
from taobao.items import TaobaoItem
from taobao.mysql_helper import MysqlHelper

options = webdriver.ChromeOptions()
options.add_argument('--lang=en')
options.add_argument("--disable-notifications")
driver = webdriver.Chrome(CHROME_DRIVER_PATH, chrome_options=options)


def crawl_tmall_list(task):
    url = task['task_url'] + "?pageNo=2"
    sid = task['id']

    try:
        driver.get(url)
        print("success get query success %s" % url)
    except Exception as e:
        print("failed when get query %s" % url)
        raise
    else:
        db = MysqlHelper()
        time.sleep(10)
        items_xpath = "//dl[contains(@class,'item')]"
        items = driver.find_elements_by_xpath(items_xpath)
        for item in items:
            product = TaobaoItem()
            product['thumb'] = item.find_element_by_xpath("./dt//img").get_attribute('src')
            product['url'] = item.find_element_by_xpath("./dt/a").get_attribute('href')
            product['title'] = item.find_element_by_xpath("./dd[@class='detail']/a").get_attribute('innerText').strip()
            product['price'] = item.find_element_by_xpath(".//span[@class='c-price']").get_attribute(
                'innerText').strip()
            try:
                product['sn'] = product['url'].split("?id=")[1]
            except Exception as e:
                continue
            else:
                if "&" in product['sn']:
                    product['sn'] = product['sn'].split("&")[0]
            product['sid'] = sid
            db.upsert_products_from_list(product)
        db.db.close()


def main():
    db = MysqlHelper()
    tasks = db.get_tmall_shops()
    for task in tasks:
        crawl_tmall_list(task)

    driver.close()
if __name__ == '__main__':
    main()
