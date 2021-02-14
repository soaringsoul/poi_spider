# -*- coding: utf-8 -*-
"""
@name:XXX
@Date: 2019/11/10 16:06
@Version: v.0.0
"""
data = """
[settings]
default = poi_spider.settings

[deploy]
#url = http://localhost:6800/
project = poi_spider
"""

with open('scrapy.cfg', 'w') as f:
    f.write(data)
