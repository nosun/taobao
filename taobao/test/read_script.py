import re
import ejson

# with open("/python/taobao/taobao/_data/data.html", 'r') as fp:
#     c = fp.read()
#
# r_title = re.compile("(.*)title\s+:(.*?),", re.S)
# r_id = re.compile("(.*)item(.*?)id\s+:(.*?),", re.S)
# r_images = re.compile("(.*)auctionImages\s+:\s+\[(.*?)\]", re.S)
#
# m = re.match(r_id, c, 0)
# js = m.group(3)
# print js


s = "item.taobao.com/item.htm?id=40416245248"
_arr = s.split("?id=")[1]
print(_arr)

