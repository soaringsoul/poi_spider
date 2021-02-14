# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class BaidumapwebapispierItem(scrapy.Item):

    # 记录区域及搜索的关键字
    poly = Field()
    search_word = Field()
    region = Field()
    requests_url = Field()
    # 可获取的信息

    results = Field()
    # 队列信息
    Q=Field()

