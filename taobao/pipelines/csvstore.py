# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import json
import csv


class CsvStorePipeline(object):
    filename = ''

    def open_spider(self, spider):
        self.filename = os.path.join(spider.settings.get('DATA_PATH'), 'products.csv')
        data = [('sn', 'title', 'url', 'images', 'choice', 'properties')]
        write_list_to_csv(data, self.filename)
        pass

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        images = str(item['images'])
        choices = str(item['choices'])
        properties = str(item['properties'])
        data = [(item['sn'], item['title'], item['url'], images, choices, properties)]
        write_list_to_csv(data, self.filename)
        return item


def write_dict_to_csv(data_, filename, mode='a'):
    data_new = [(k, v) for k, v in data_.items()]
    write_list_to_csv(data_new, filename, mode)


def write_list_to_csv(data_, filename, mode='a'):
    filename = filename if filename.endswith(".csv") else filename + '.csv'
    with open(filename, mode, newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerows(data_)


def read_csv(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        lines = file.readlines()
    return lines
