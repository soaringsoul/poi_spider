# -*- coding: utf-8 -*-
def gen_scrapycfg(prname='poi_spider'):
    data = """
[settings]
default = {prname}.settings

[deploy]
#url = http://localhost:6800/
project = {prname}
    """.format(prname=prname)

    with open('scrapy.cfg', 'w') as f:
        f.write(data)

if __name__ == "__main__":
    gen_scrapycfg()