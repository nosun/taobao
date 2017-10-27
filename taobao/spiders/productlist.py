# -*- coding: utf-8 -*-

from lxml import etree
from furl import furl
import random

if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from taobao.items import TaobaoItem
from taobao.utils.useragent import user_agents
from taobao.mysql_helper import MysqlHelper
import logging
import scrapy

logger = logging.getLogger('productlist')


class ProductListSpider(scrapy.Spider):
    name = "productlist"
    handle_httpstatus_list = [301, 302]
    # handle_httpstatus_list = [302]
    # proxy = ProxyStatic()

    allowed_domains = ["taobao.com", "tmall.com"]

    custom_settings = {
        'ITEM_PIPELINES': {
            'taobao.pipelines.mysqlstorelist.MysqlStoreListPipeline': 10,
        }
    }

    def start_requests(self):
        shop_id = getattr(self, 'id', None)
        start = getattr(self, 'start', None)
        tasks = self.get_tasks(shop_id)
        for task in tasks:
            meta = dict()
            if start:
                task['url'] = task['url'][:-1] + str(start)
            meta['task'] = task
            # meta['proxy'] = "https://avarsha:avarsha@45.33.75.249:31028"
            headers = self.get_headers(task['task_url'], task['site'])
            yield scrapy.Request(task['url'], headers=headers, callback=self.parse, meta=meta)

    def parse(self, response):

        meta = response.meta
        logger.info('Parse function called on %s, status is %s' % (response.url, response.status))

        task = meta['task']
        headers = self.get_headers(task['task_url'], task['site'])

        elements = etree.HTML(response.text.replace('\\', '').strip()[10:-2])
        lists = elements.xpath("//dl[contains(@class,'item')]")
        has_next = elements.xpath("//a[@class='J_SearchAsync next']")

        if has_next:
            page = int(response.url[-1])
            page += 1
            next_url = response.url[:-1] + str(page)
            yield scrapy.Request(next_url, headers=headers, callback=self.parse, meta=meta)

        if len(lists):
            for p in lists:
                p_meta = {}
                item = TaobaoItem()
                item['sid'] = task['id']  # shopid
                item['title'] = p.xpath("./dd[@class='detail']/a/text()")[0].strip()
                item['thumb'] = response.urljoin(p.xpath("./dt//img/@src")[0])
                item['url'] = response.urljoin(p.xpath("./dd[@class='detail']/a/@href")[0]).replace(" ", "")
                item['price'] = p.xpath(".//span[@class='c-price']/text()")[0].strip()
                item['sn'] = item['url'].split("?id=")[1].split("&")[0]
                p_meta['item'] = item
                if item['url']:
                    yield item
                    # break  # for test

    def get_tasks(self, shop_id=None):
        db = MysqlHelper()
        shops = db.get_shops(shop_id)
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
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Accept-Language': 'en-US,en;q=0.5',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Connection': 'keep-alive',
                   'x - insight': 'activate',
                   'Cache - Control': 'max - age = 0'
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
    spider = ProductListSpider()
    # urls = spider.get_shop_url()
    # print(urls)
