# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TaobaoItem(scrapy.Item):
    # define the fields for your item here like:
    sn = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    thumb = scrapy.Field()
    price = scrapy.Field()
    prices = scrapy.Field()
    images = scrapy.Field()
    choices = scrapy.Field()
    sizes = scrapy.Field()
    colors = scrapy.Field()
    properties = scrapy.Field()
    sid = scrapy.Field()  # shop_id
    # type = scrapy.Field()  # product_type
    pass

