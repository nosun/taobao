# -- coding : utf-8 -- *

import pymysql
import time

if __name__ == '__main__' and __package__ is None:
	from os import sys, path
	
	sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from taobao.settings import MYSQL_CONFIG


class MysqlHelper(object):
	tb_user = "shops"
	tb_wb_user = "products"
	
	def __init__(self):
		host = MYSQL_CONFIG.get('host', '127.0.0.1')
		db = MYSQL_CONFIG.get('db', '')
		user = MYSQL_CONFIG.get('user', 'root')
		passwd = MYSQL_CONFIG.get('passwd', '')
		charset = MYSQL_CONFIG.get('charset', 'utf8')
		
		self.db = pymysql.connect(host=host, user=user, db=db, passwd=passwd, charset=charset)
	
	def get_shop_by_name(self, condition):
		pass
	
	def get_shops_by_status(self, status):
		c = self.db.cursor(pymysql.cursors.DictCursor)
		sql = "select * from shops where status = %s order by id asc" % status
		c.execute(sql)
		return c.fetchall()
	
	def get_shops(self, shop_id=None):
		c = self.db.cursor(pymysql.cursors.DictCursor)
		if shop_id:
			sql = "select * from shops where id = %s" % shop_id
		else:
			sql = "select * from shops where status = 0 and task_url not like '%tmall%'"
		c.execute(sql)
		return c.fetchall()
	
	def add_task_url(self, task):
		c = self.db.cursor()
		try:
			c.execute("""INSERT INTO shops (`task_url`) VALUES (%s)""", (task,))
			self.db.commit()
		except:
			pass
	
	def update_task(self, name, wid, id):
		c = self.db.cursor()
		c.execute("""update shops set wid = %s, name = %s where id = %s""", (wid, name, id))
		self.db.commit()
	
	def get_product_tasks(self):
		c = self.db.cursor(pymysql.cursors.DictCursor)
		sql = "select * from products where images is Null order by id asc"
		c.execute(sql)
		return c.fetchall()
	
	def get_products(self):
		c = self.db.cursor(pymysql.cursors.DictCursor)
		sql = "select * from products where images is not Null order by id asc"
		c.execute(sql)
		return c.fetchall()
	
	def get_products_by_shop(self, shop_id):
		c = self.db.cursor(pymysql.cursors.DictCursor)
		sql = "select p.*, s.* from products p inner join shops s on p.sid = s.id  where s.id = %s " \
		      "order by p.id asc" % shop_id
		c.execute(sql)
		return c.fetchall()
	
	def upsert_products_from_list(self, item):
		
		now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
		
		item = self._format(item)
		c = self.db.cursor(pymysql.cursors.DictCursor)
		c.execute("select * from products where sn = %s", (item['sn'],))
		ret = c.fetchone()
		
		if ret:
			return
		else:
			# insert article list data
			sql = """insert into products(sn, title, url, thumb, price, sid, created_at, updated_at)
	                 values (%s, %s, %s, %s, %s, %s, %s, %s)"""
			print(sql)
			
			params = (item['sn'], item['title'], item['url'], item['thumb'], item['price'], item['sid'], now, now)
			print(params)
			try:
				c.execute(sql, params)
			except Exception as e:
				print(e)
	
	def update_product(self, item):
		now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
		
		item = self.format_data(item)
		c = self.db.cursor(pymysql.cursors.DictCursor)
		c.execute("select * from products where sn = %s", (item['sn'],))
		ret = c.fetchone()
		
		if ret:
			sql ="""update products set images = %s, sizes = %s, colors = %s, prices = %s, choices = %s , properties
			= %s, updated_at = %s where sn = %s """
			params = (item['images'], item['sizes'], item['colors'], item['prices'], item['choices'],
			          item['properties'], now, item['sn'])
			print(params)
			try:
				c.execute(sql, params)
			except Exception as e:
				print(e)
	
	def format_data(self, item):
		item['images'] = pymysql.escape_string(repr(item['images']))
		item['choices'] = pymysql.escape_string(repr(item['choices']))
		item['properties'] = pymysql.escape_string(repr(item['properties']))
		return item


if __name__ == "__main__":
	db = MysqlHelper()
	res = db.get_shops()
	print(res)
