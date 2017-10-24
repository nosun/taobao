import csv
import time

import lxml.html
import re

import os
import requests
import urllib3

urllib3.disable_warnings()
session = requests.session()


def get_shop_product(name, wid, page=1):
    time_stamp = int(time.time() * 1000)
    url = "https://{}.taobao.com/i/asynSearch.htm".format(name)

    params = {"_ksTS": "{}_141".format(time_stamp),
              "callback": "jsonp142",
              "mid": "w-{}-0".format(wid),
              "wid": wid,
              "path": "/search.htm",
              "search": "y",
              "pageNo": page, }

    headers = {
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/62.0.3188.4 Safari/537.36',
        'accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, '
                  '*/*; q=0.01',
        'referer': 'https://{}.taobao.com/search.htm'.format(name),
        'authority': '{}.taobao.com'.format(name),
        'x-requested-with': 'XMLHttpRequest', }
    print("get_shop_product", url, page)
    rep = session.get(url, params=params, headers=headers, verify=False)
    product_html = rep.text.strip()[len(params['callback']):-2]
    product_html = product_html.replace('\\"', '"')
    etree = lxml.html.fromstring(product_html)
    product_items = etree.cssselect("dl.item")
    products = []
    for item in product_items:
        item_info = item.cssselect('img')[0]
        item_img = item_info.attrib['src']
        item_title = item_info.attrib['alt']
        item_price = item.cssselect('span.c-price')[0].text
        ele_sale_num = item.cssselect('span.sale-num')
        item_sale = ele_sale_num[0].text if len(ele_sale_num) > 0 else -1
        ele_comment = item.cssselect('div.title a span')
        item_comment = ele_comment[0].text if len(ele_comment) > 0 else -1
        products.append([item_title, item_img, item_price, item_sale, item_comment])
    has_next = etree.cssselect("a.J_SearchAsync.next")
    print("len {}".format(len(products)))
    return products, len(has_next) > 0


def read_all_taobao_shop():
    with open('task.csv', 'r', encoding='utf-8-sig') as file:
        lines = file.readlines()
        shops = [line.split('/')[2] for line in lines]
        shop_infos = [get_shop_wid(shop) for shop in shops]
        write_to_csv([item.popitem() for item in shop_infos], "task_info")


def get_shop_wid(shop):
    url = "https://{}/search.htm".format(shop)
    print("get_shop_wid", url)
    rep = session.get(url, verify=False)
    etree = lxml.html.fromstring(rep.content)
    wid = etree.cssselect('div#bd div.J_TModule')[0].attrib['data-widgetid']
    time.sleep(30)
    name = shop.split(".")[0]
    return {name: wid}


def write_to_csv(data_, filename):
    filename = filename if filename.endswith(".csv") else filename + '.csv'
    with open(filename, "w", newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerows(data_)


def read_csv(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        lines = file.readlines()
    return lines


def main():
    shops = read_csv("task_infos.csv")
    for item in shops:
        name, wid = item.strip().split(",")
        file_name = "shop_data/{}_products.csv".format(name)
        has_next = True
        page = 1
        products = []
        if os.path.exists(file_name):
            continue
        while has_next:
            products_temp, has_next = get_shop_product(name, wid, page)
            products.extend(products_temp)
            page = page + 1
            time.sleep(30)
        write_to_csv(products, file_name)
        # get_shop_product('shop128075555', '11818602936')


if __name__ == '__main__':
    main()
    #read_all_taobao_shop()
