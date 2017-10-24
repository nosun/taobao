# -- coding : utf-8 -- *


if __name__ == '__main__' and __package__ is None:
    from os import sys, path

    sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import os
from taobao.mysql_helper import MysqlHelper
from taobao.settings import DATA_PATH
from taobao.utils.csv import read_csv


def insert_task():
    csv_file = os.path.join(DATA_PATH, "task.csv")
    lines = read_csv(csv_file)
    db = MysqlHelper()
    for line in lines:
        task = line.split("@")[0].strip()
        print(task)
        db.add_task_url(task)


def update_task():
    csv_file = os.path.join(DATA_PATH, "shop_infos.csv")
    lines = read_csv(csv_file)
    db = MysqlHelper()
    id = 1
    for line in lines:
        name, wid = line.split(",")
        db.update_task(name, wid, id)
        id = id + 1


if __name__ == '__main__':
    update_task()
