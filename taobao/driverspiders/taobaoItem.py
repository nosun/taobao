# -*- coding:utf-8 -*-  
""" 
@author: nosun 
@file: taobaoItem.py
@time: 2017/10/29 
"""

import time
import logging
import re
import json
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

logger = logging


class TaobaoItemSpider(object):
	driver = None
	driver_option = None
	mysql_db = None
	
	def __init__(self):
		self.lang = "zh"
		self.db = MysqlHelper()
	
	def init_chrome_driver(self):
		""" init chrome dirver """
		options = webdriver.ChromeOptions()
		options.add_argument('--lang=' + self.lang)
		options.add_argument("--disable-notifications")
		self.driver = webdriver.Chrome(CHROME_DRIVER_PATH, chrome_options=options)
		pass
	
	def start(self):
		self.init_chrome_driver()
		
		tasks = self.get_tasks()
		
		for task in tasks:
			self.crawl_taobao_item(task)
			print("crawl the page finished %s" % (task,))
		
		self.close()
	
	def close(self):
		"""close driver"""
		self.driver.quit()
		self.db.db.close()
		logger.info('Goodbye, The tasks is finished.')
		pass
	
	def get_tasks(self):
		""" get tasks from db"""
		tasks = self.db.get_product_tasks()
		tasks = ["https://detail.tmall.com/item.htm?id=538781935997"]
		return tasks
	
	def crawl_taobao_item(self, task):
		"""
			1. crawl taobao item page
			2. get item info form page
			3. save info to database
		"""
		url = task
		print("begin to crawl page: %s" % url)
		
		try:
			self.driver.get(url)
			print("success get query success %s" % url)
		except Exception as e:
			print("failed when get query %s" % url)
		else:
			try:
				time.sleep(5)
				product = TaobaoItem()
				# get properties
				properties_xpath = "//ul[@id='J_AttrUL']/li"
				_arrs = self.driver.find_elements_by_xpath(properties_xpath)
				properties = dict()
				for pt in _arrs:
					pt = pt.get_attribute("innerText")
					_arr = pt.split(":")
					properties[_arr[0].strip()] = _arr[1].strip()
				
				body = self.driver.find_element_by_tag_name("body").get_attribute("innerHTML")
				r = re.compile(r"(.*)TShop.Setup\((.*?)\}\)", re.S)
				matchObj = re.match(r, body, 0)
				if matchObj and len(matchObj.group()) > 1:
					obj_json = matchObj.group(2)
					obj_json = obj_json.strip()[:-2].strip()
					obj_json = json.loads(obj_json)
					
					# get images
					js_images = obj_json['propertyPics']
					images = set()
					for k, v in js_images.items():
						for i in v:
							images.add("https:" + i)
					product['images'] = list(images)
					
					# get colors
					product['colors'] = []
					sku_list = obj_json['valItemInfo']['skuList']
					for sku in sku_list:
						product['colors'].append(sku['names'].strip())
					
					# get prices
					product['prices'] = []
					sku_maps = obj_json['valItemInfo']['skuMap']
					prices = set()
					for k, v in sku_maps.items():
						prices.add(v['price'])
					product['prices'] = list(prices)
					
					# get choices
					product['choices'] = self.format_sku(sku_list, sku_maps)
					self.db.update_product(product)
			
			except Exception as e:
				print(e)
				raise e
	
	def format_sku(self, sku_list, sku_maps):
		new_sku_list = dict()
		for sku in sku_list:
			new_sku_list[sku['pvs']] = sku["names"].strip()
		
		for k, v in sku_maps.items():
			if k.strip(";") in new_sku_list.keys():
				sku_maps[k]['color'] = new_sku_list[k.strip(";")]
		
		return sku_maps


if __name__ == '__main__':
	crawler = TaobaoItemSpider()
	crawler.start()
