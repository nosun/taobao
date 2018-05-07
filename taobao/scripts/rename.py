# -*- coding:utf-8 -*-  
"""
@author: nosun
@file: rename.py
@time: 2017/10/31
"""

import os


def rename(file, old, new):
    if os.path.isfile(file):
        new_path = file.rstrip(old) + new
        os.rename(file, new_path)


def search_rename(target_dir, old, new):
    for i in os.listdir(target_dir):
        i = os.path.join(target_dir, i)
        if os.path.isfile(i):
            if i.endswith(old):
                new_path = i.rstrip(old) + new
                os.rename(i, new_path)
        elif os.path.isdir(i):
            search_rename(i, old, new)


def main():
    suffix = "SS2"
    new_suffix = "jpg"
    target_path = os.path.join("/python/taobao/taobao", "_images")
    search_rename(target_path, suffix, new_suffix)


if __name__ == '__main__':
    main()
