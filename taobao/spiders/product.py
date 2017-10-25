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


class ProductSpider(scrapy.Spider):
    name = "product"
    allowed_domains = ["taobao.com", "tmall.com"]
    # handle_httpstatus_list = [302]
    # proxy = ProxyStatic()

    def start_requests(self):
        tasks = self.get_tasks()
        for task in tasks:
            meta = dict()
            meta['task'] = task
            # meta['proxy'] = self.proxy.get_proxy()['https']
            headers = self.get_headers(task['task_url'], task['site'])
            yield scrapy.Request(task['url'], headers=headers, callback=self.parse, meta=meta)

    def parse(self, response):

        meta = response.meta
        task = meta['task']
        headers = self.get_headers(task['task_url'], task['site'])

        elements = etree.HTML(response.text.replace('\\', '').strip()[10:-2])
        lists = elements.xpath("//dl[contains(@class,'item')]")
        has_next = elements.xpath("//a[@class='J_SearchAsync next']")

        if has_next:
            page = int(task['url'][-1])
            page += 1
            next_url = task['url'][:-1] + str(page)
            yield scrapy.Request(next_url, headers=headers, callback=self.parse, meta=meta)

        if len(lists):
            for p in lists:
                p_meta = {}
                item = TaobaoItem()
                item['sid'] = task['id']  # shopid
                item['title'] = p.xpath("./dd[@class='detail']/a/text()")[0].strip()
                item['thumb'] = response.urljoin(p.xpath("./dt//img/@src")[0])
                item['url'] = response.urljoin(p.xpath("./dd[@class='detail']/a/@href")[0])
                item['price'] = p.xpath(".//span[@class='c-price']/text()")[0]
                p_meta['item'] = item
                if item['url']:
                    yield scrapy.Request(item['url'], headers=headers, callback=self.parse_page, meta=p_meta)
                # break  # for test

    def parse_page(self, response):
        item = response.meta['item']

        # extract
        item['sn'] = response.url.split("?id=")[1]
        item['images'] = self.extract_images(response)
        item['choices'] = self.extract_choice(response)
        item['properties'] = self.extract_properties(response)
        # print item
        return item

    # from detail page parse title, no use
    def extract_title(self, response):
        title = response.xpath("//h3[@class='tb-main-title']/text()").extract_first().strip()
        return title

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
        ctypes = {}
        if len(colors):
            for i in range(len(colors)):
                ctypes[color_types[i]] = "color:" + str(colors[i])

        # size
        size_types = response.xpath('//dl[contains(@class,"J_Prop_measurement")]//li/@data-value').extract()
        sizes = response.xpath('//dl[contains(@class,"J_Prop_measurement")]//span/text()').extract()
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
        return skus

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
        shops = db.get_shops()
        tasks = []
        for shop in shops:
            wid = shop['wid']
            name = shop['name']
            task_url = shop['task_url']
            _arr = task_url.split("/")
            if len(_arr) >= 3:
                site = _arr[2]
                path = _arr[3]

                url = "https://{}/i/asynSearch.htm".format(site)

                params = {"_ksTS": "replace_time_141",  # will replace later
                          "callback": "jsonp142",
                          "mid": "w-{}-0".format(wid),
                          "wid": wid,
                          "path": "/{}".format(path),
                          "search": "y",
                          "pageNo": 1}

                f = furl(url)
                f.args = params
                # print(f.url)
                task = dict()
                task['id'] = str(shop['id'])
                task['name'] = name
                task['site'] = site
                task['path'] = path
                task['task_url'] = task_url
                task['url'] = f.url
                tasks.append(task)
                # break  # only get one for test
            else:
                continue
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
    key = key.replace(";", "")
    for k, v in colors.items():
        key = key.replace(k, v)

    for k, v in sizes.items():
        key = key.replace(k, v)

    return key


if __name__ == '__main__':
    spider = ProductSpider()
    # urls = spider.get_shop_url()
    # print(urls)
