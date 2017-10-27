# -*- coding: utf-8 -*-

import os
from lxml import etree

if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from taobao.items import TaobaoItem
from taobao.settings import DATA_PATH
from taobao.utils.csv import read_csv
import logging
import scrapy

logger = logging.getLogger('productlist')


class TmallProductListSpider(scrapy.Spider):
    name = "tmallproductlist"
    handle_httpstatus_list = [301, 302]
    # handle_httpstatus_list = [302]
    # proxy = ProxyStatic()

    allowed_domains = ["html.app"]

    custom_settings = {
        'ITEM_PIPELINES': {
            'taobao.pipelines.mysqlstorelist.MysqlStoreListPipeline': 10,
        }
    }

    def start_requests(self):
        shop_id = getattr(self, 'id', None)
        tasks = self.get_tasks(shop_id)
        for task in tasks:
            meta = dict()
            meta['task'] = task
            yield scrapy.Request(task['url'], callback=self.parse, meta=meta)

    def parse(self, response):
        meta = response.meta
        logger.info('Parse function called on %s, status is %s' % (response.url, response.status))
        task = meta['task']

        elements = etree.HTML(response.text.replace('\\', '').replace("\n", "").strip()[10:-2])
        lists = elements.xpath("//dl[contains(@class,'item')]")

        if len(lists):
            for p in lists:
                item = TaobaoItem()
                item['sid'] = task['sid']  # shopid
                item['title'] = p.xpath("./dd[@class='detail']/a/text()")[0].strip()
                item['thumb'] = response.urljoin(p.xpath("./dt//img/@src")[0])
                item['url'] = response.urljoin(p.xpath("./dd[@class='detail']/a/@href")[0])
                item['price'] = p.xpath(".//span[@class='c-price']/text()")[0]
                item['sn'] = item['url'].split("?id=")[1]
                if item['url']:
                    yield item
                    # break  # for test

    def get_tasks(self, shop_id):
        task_path = os.path.join(DATA_PATH, "tmallurl.txt")
        lines = read_csv(task_path)
        tasks = []
        for line in lines:
            sid, url = line.split(",")
            tasks.append({
                'sid': sid,
                'url': url.replace("\n", "")
            })
        return tasks


if __name__ == '__main__':
    spider = TmallProductListSpider()
    # urls = spider.get_shop_url()
    # print(urls)
