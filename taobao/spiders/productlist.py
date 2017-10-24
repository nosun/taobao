# -*- coding: utf-8 -*-
import scrapy


class ProductListSpider(scrapy.Spider):
    name = "productlist"
    allowed_domains = ["taobao.com"]
    start_urls = ['http://taobao.com/']

    def parse(self, response):
        pass
