# -- coding : utf-8 -- *

import MySQLdb

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

        self.db = MySQLdb.connect(host=host, user=user, db=db, passwd=passwd, charset=charset)

    def get_shop_by_name(self, condition):
        pass

    def get_shops(self):
        c = self.db.cursor(MySQLdb.cursors.DictCursor)
        c.execute("select * from shops")
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

    def get_products(self):
        c = self.db.cursor(MySQLdb.cursors.DictCursor)
        sql = "select * from products limit 1"
        c.execute(sql)
        return c.fetchall()


if __name__ == "__main__":
    db = MysqlHelper()
    res = db.get_shops()
    print(res)
