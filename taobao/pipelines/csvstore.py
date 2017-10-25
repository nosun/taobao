# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
from taobao.utils.csv import write_list_to_csv


class CsvStorePipeline(object):
    filename = ''

    def open_spider(self, spider):
        self.filename = os.path.join(spider.settings.get('DATA_PATH'), 'products.csv')
        data = [('sn', 'title', 'url', 'thumb', 'price', 'images', 'choice', 'properties')]
        write_list_to_csv(data, self.filename)
        pass

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        images = str(item['images'])
        choices = str(item['choices'])
        properties = str(item['properties'])
        data = [(item['sn'], item['title'], item['url'], item['thumb'], item['price'], images, choices, properties)]
        write_list_to_csv(data, self.filename)
        return item

