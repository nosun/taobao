# -*- coding: utf-8 -*-
import os
import scrapy
from lxml import etree
import json
import re
import time
import random
from furl import furl

if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from taobao.items import TaobaoItem
from taobao.utils.useragent import user_agents
from taobao.utils.proxystatic import ProxyStatic
from taobao.mysql_helper import MysqlHelper


class ProductOnlySpider(scrapy.Spider):
    name = "productonly"
    allowed_domains = ["taobao.com", "tmall.com"]
    # handle_httpstatus_list = [302]
    # proxy = ProxyStatic()

    def start_requests(self):
        tasks = self.get_tasks()
        for task in tasks:
            # meta['proxy'] = self.proxy.get_proxy()['https']
            url = furl(task)
            headers = self.get_headers(url.url, url.host)
            yield scrapy.Request(task, headers=headers, callback=self.parse_page,)

    def parse_page(self, response):
        item = TaobaoItem()

        # extract
        item['sn'] = response.url.split("?id=")[1]
        item['images'] = self.extract_images(response)
        item['choices'], item['sizes'], item['colors'] = self.extract_choice(response)
        item['properties'] = self.extract_properties(response)
        # print item
        return item

    def extract_images(self, response):
        images = []
        r = re.compile(r"(.*)auctionImages\s+:\s+\[(.*?)\]", re.S)
        matchObj = re.match(r, response.text, 0)
        if matchObj and len(matchObj.group()) > 1:
            res = matchObj.group(2)
            _arr = res.split(",")
            for url in _arr:
                images.append("https:" + url.strip('"'))

        return images

    def extract_choice(self, response):
        r = re.compile(r"(.*)skuMap\s+:\s+(.*?)(\s+),propertyMemoMap", re.S)
        match_sku = re.match(r, response.text, 0)

        if match_sku and len(match_sku.group()) > 1:
            res = match_sku.group(2)
        else:
            res = ""

        """
            may empty from js data
        """
        # r_type = re.compile("(.*)propertyMemoMap\s?:\s+(.*?)\s", re.S)
        # match_type = re.match(r_type, response.text, 0)
        #
        # if match_type and len(match_sku.group()) > 1:
        #     res_type = match_type.group(2)
        # else:
        #     res_type = ""

        # color
        color_types = response.xpath('//dl[contains(@class,"J_Prop_Color")]//li/@data-value').extract()
        colors = response.xpath('//dl[contains(@class,"J_Prop_Color")]//span/text()').extract()
        f_colors = ','.join(colors)
        ctypes = {}
        if len(colors):
            for i in range(len(colors)):
                ctypes[color_types[i]] = "color:" + str(colors[i])

        # size
        size_types = response.xpath('//dl[contains(@class,"J_Prop_measurement")]//li/@data-value').extract()
        sizes = response.xpath('//dl[contains(@class,"J_Prop_measurement")]//span/text()').extract()
        f_sizes = ','.join(sizes)
        stypes = {}
        if len(sizes):
            for i in range(len(sizes)):
                stypes[size_types[i]] = "size:" + str(sizes[i])

        skus = []
        if res:
            js = res.strip()
            js = json.loads(js)
            sku = {}
            for k, v in js.items():
                sku['sku'] = v['skuId']
                sku['attr'] = get_attrs(k, ctypes, stypes)
                sku['price'] = v['price']
                skus.append(sku)
        return skus, f_sizes, f_colors

        # skuMap     : {";1627207:28320;":{"oversold":false,"price":"276.00","skuId":"3590438822427","stock":"2"},";1627207:28326;":{"oversold":false,"price":"276.00","skuId":"3590438822428","stock":"2"},";1627207:28327;":{"oversold":false,"price":"276.00","skuId":"3457048284671","stock":"2"},";1627207:28334;":{"oversold":false,"price":"276.00","skuId":"3590438822430","stock":"2"},";1627207:28341;":{"oversold":false,"price":"276.00","skuId":"3590438822431","stock":"2"}}
        # ,propertyMemoMap: {"1627207:28320":"白色","1627207:28326":"红色","1627207:28327":"酒红色","1627207:28334":"灰色","1627207:28341":"黑色"}

    def extract_properties(self, response):

        properties = {}
        pts = response.xpath('//ul[@class="attributes-list"]/li/text()').extract()

        for pt in pts:
            k, v = pt.split(":")
            properties[k.strip()] = v.strip()

        return properties

    def get_tasks(self):
        db = MysqlHelper()
        products = db.get_product_tasks()
        tasks = [product['url'] for product in products if product['url'] is not None]
        return tasks

    def get_headers(self, referer, site):
        headers = {'User-Agent': random.choice(user_agents),
                   'Accept-Encoding': 'gzip, deflate, sdch',
                   'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Connection': 'keep-alive'
                   }

        headers['referer'] = referer
        headers['authority'] = site

        return headers


def get_attrs(key, colors=None, sizes=None):
    key = key.strip(";")
    for k, v in colors.items():
        key = key.replace(k, v)

    for k, v in sizes.items():
        key = key.replace(k, v)

    return key


if __name__ == '__main__':
    spider = ProductOnlySpider()
    # urls = spider.get_shop_url()
    # print(urls)
