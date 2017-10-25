# -*- coding: utf-8 -*-

import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi
import time
import pickle
import logging
import hashlib
from scrapy.exceptions import DropItem


class MysqlStorePipeline(object):
    def __init__(self, db_pool):
        self.db_pool = db_pool

    @classmethod
    def from_crawler(cls, crawler):
        """1、@classmethod 声明一个类方法，而对于平常我们见到的则叫做实例方法。
           2、类方法的第一个参数cls（class的缩写，指这个类本身），而实例方法的第一个参数是self，表示该类的一个实例
           3、可以通过类来调用，就像C.f()，相当于java中的静态方法
        """
        db_params = dict(
            host=crawler.settings['MYSQL_CONFIG']['host'],
            db=crawler.settings['MYSQL_CONFIG']['db'],
            user=crawler.settings['MYSQL_CONFIG']['user'],
            passwd=crawler.settings['MYSQL_CONFIG']['passwd'],
            charset=crawler.settings['MYSQL_CONFIG']['charset'],
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=False,
        )

        db_pool = adbapi.ConnectionPool('MySQLdb', **db_params)  # **表示将字典扩展为关键字参数,相当于host=xxx,db=yyy....
        return cls(db_pool)  # 相当于 db_pool 给了这个类，self中可以得到

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        d = self.db_pool.runInteraction(self._do_update_insert, item)
        d.addErrback(self._handle_error, item, spider)
        d.addBoth(lambda _: item)
        return item

    def _do_update_insert(self, conn, item):

        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        item = self._format(item)

        conn.execute("select * from products where sn = %s", (item['sn'],))
        ret = conn.fetchone()

        if ret:
            return

        else:
            # insert article list data
            sql = """insert into products(sn, title, url, thumb, price, images, choices, properties, sid, created_at, 
                     updated_at) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                  """
            print(sql)

            params = (item['sn'], item['title'], item['url'], item['thumb'], item['price'], item['images'],
                      item['choices'], item['properties'], item['sid'], now, now)
            print(params)
            try:
                conn.execute(sql, params)
            except Exception as e:
                print(e)

    def _format(self, item):
        item['title'] = item['title'].strip()
        item['images'] = MySQLdb.escape_string(repr(item['images']))
        item['choices'] = MySQLdb.escape_string(repr(item['choices']))
        item['properties'] = MySQLdb.escape_string(repr(item['properties']))
        return item

    def _format_images(self, images):
        pass


    def _handle_error(self, failue, item, spider):
        print(failue)
