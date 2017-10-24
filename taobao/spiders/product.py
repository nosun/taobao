# -*- coding: utf-8 -*-
import os
import scrapy
from lxml import etree
import json
import re
import time
from furl import furl

if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from taobao.items import TaobaoItem
from taobao.utils.csv import read_csv
from taobao.utils.headers import headers
from taobao.settings import DATA_PATH


class ProductSpider(scrapy.Spider):
    name = "product"
    allowed_domains = ["taobao.com", "tmall.com"]

    def __init__(self):
        super(ProductSpider, self).__init__(self)
        self._get_shop_url()

    def parse(self, response):
        elements = etree.HTML(response.text.replace('\\', '').strip()[10:-2])
        links = elements.xpath('//a[@class="J_TGoldData"]/@href')
        for link in links:
            yield scrapy.Request(response.urljoin(link), headers=headers, callback=self.parse_page)
            # @todo nextpage

    def parse_next_page(self):
        pass

    def parse_page(self, response):
        item = TaobaoItem()

        # extract
        item['sn'] = response.url.split("?id=")[1]
        item['url'] = response.url
        item['title'] = self.extract_title(response)
        item['images'] = self.extract_images(response)
        item['choices'] = self.extract_choice(response)
        item['properties'] = self.extract_properties(response)
        # print item
        return item

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
                images.append(response.urljoin(url))

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

    def _get_shop_url(self):
        task_file = os.path.join(DATA_PATH, "shop_infos.csv")
        shops = read_csv(task_file)
        self.start_urls = []

        for item in shops:
            name, wid = item.strip().split(",")
            url = "https://{}.taobao.com/i/asynSearch.htm".format(name)

            params = {"_ksTS": "replace_time_141",  # will replace later
                      "callback": "jsonp142",
                      "mid": "w-{}-0".format(wid),
                      "wid": wid,
                      "path": "/search.htm",
                      "search": "y",
                      "pageNo": 1}

            f = furl(url)
            f.args = params
            print(f.url)
            # self.start_urls.append(f)


def get_attrs(key, colors=None, sizes=None):
    key = key.replace(";", "")
    for k, v in colors.items():
        key = key.replace(k, v)

    for k, v in sizes.items():
        key = key.replace(k, v)

    return key


if __name__ == '__main__':
    spider = ProductSpider()
    print(spider.start_urls)

