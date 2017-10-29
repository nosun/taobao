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

url = 'https://yinxiangjiadao.tmall.com/category-1332170528.htm'
try:
	driver.get(url)
	print("success get query success %s" % url)
except Exception as e:
	print("failed when get query %s" % url)
try:
	time.sleep(10)
	element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "J_TItems")))
	items_xpath = "//dl[contains(@class,'item')]"
	items = driver.find_elements_by_xpath(items_xpath)
	db = MysqlHelper()
	for item in items:
		product = TaobaoItem()
		thumb = item.find_element_by_xpath("./dt//img")
		product['thumb'] = item.find_element_by_xpath("./dt//img").get_attribute('src')
		product['url'] = item.find_element_by_xpath("./dt/a").get_attribute('href')
		product['title'] = item.find_element_by_xpath("./dd[@class='detail']/a").get_attribute('innerText').strip()
		product['price'] = item.find_element_by_xpath(".//span[@class='c-price']").get_attribute('innerText').strip()
		product['sn'] = product['url'].split("?id=")[1].split("&")[0]
		db.upsert_products_from_list(product)
		
finally:
	driver.quit()
