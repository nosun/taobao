# coding:utf-8

import os
import MySQLdb
import json
import requests
from random import choice
from .headers import headers
from taobao.settings import MYSQL_CONFIG_SERVICE, DATA_PATH


class Proxy(object):
    def __init__(self):
        self.pf = os.path.join(DATA_DIR, "proxies.json")
        self.proxies = list()
        self._get_proxies()

    def _get_proxies(self):
        # second check file
        if not os.path.isfile(self.pf):
            db = simplemysql.SimpleMysql(**MYSQL_CONFIG_SERVICE)
            res = db.getAll("host", ["ip"], ["active = 1 and mbyte = 1"])
            if res:
                for p in res:
                    proxy = {"https": "https://avarsha:avarsha@" + p.ip + ":31028"}
                    self.proxies.append(proxy)
                with open(self.pf, "w") as f:
                    f.write(json.dumps(self.proxies))
        else:
            with open(self.pf, "r") as f:
                self.proxies = json.loads(f.read())

        return self.proxies

    def get_proxy(self):
        if len(self.proxies):
            return choice(self.proxies)
        return None

    def gen_proxies_enable(self, url, timeout):
        for proxy in self.proxies:
            try:
                self.check_proxy(proxy, url, timeout)
            except Exception as e:
                self.proxies.remove(proxy)

        # cache
        with open(self.pf, "w") as f:
            f.write(json.dumps(self.proxies))

    def check_proxy(self, proxy, url, timeout):
        try:
            rsp = requests.get(url, proxies=proxy, headers=headers, timeout=timeout)
            print(rsp.status_code)
        except Exception as e:
            print(e)
            raise


if __name__ == '__main__':
    proxy = Proxy()
    # proxy.gen_proxies_enable("https://www.baidu.com", timeout=5)
    for i in range(1, 4):
        p = proxy.get_proxy()
        print(p)