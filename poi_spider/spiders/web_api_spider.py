import logging
import scrapy
import os
import time
from scrapy.spiders import Spider
from datetime import datetime
from pandas import DataFrame
import pandas as pd
from china_areas import areas

import json
from multiprocessing.dummy import Pool as ThreadPool

from poi_spider.util.geo.district_nokey import get_region_polyline
from poi_spider.util.geo.GetRegionBounds import SplitRectangularArea

from poi_spider.items import BaidumapwebapispierItem
# from poi_spider.util.email.send_email import send_email_163
from poi_spider.util.geo.change_position import ChangePosition
import mysql


class WebApiCrawler(Spider):
    name = 'bd_map_spider'

    def __init__(self, Q=None, settings=None):
        self.settings = settings
        self.storage = settings.get("storage")
        self.csv_fname = settings.get("csv_fname")
        self.regions = settings.get('regions')
        self.ak = settings.get('ak')
        self.gd_key = settings.get('gd_key')
        self.keywords = settings.get('keywords')
        self.Q = Q
        self.error_code_list = [x for x in range(201, 500)] + [2, 3, 4, 5, 101, 102]

    def get_regions(self):

        prov = self.regions['prov']
        city = self.regions['city']
        district = self.regions['district']

        if district == "全部区县":
            district_like = ""
        else:
            district_like = district
        if city == "全部城市":
            city_like = ""
        else:
            city_like = city
        query = """
                select * from china_areas
                where district like '%{district}%'
                and province like '%{prov}%'
                and city like '%{city}%'
                """.format(district=district_like, prov=prov, city=city_like)

        df = pd.DataFrame(mysql.query_str(q_str=query),
                          columns=['province', 'province_adcode', 'province_center', 'city', 'city_adcode',
                                   'citycode', 'city_center', 'district', 'district_adcode',
                                   'district_center'])
        print(df)

        if city == "全部城市":
            df_district = df[df['province'] == prov]
        else:
            if district == "全部区县":
                df_district = df[(df['province'] == prov) & (df['city'] == city)]
            else:
                df_district = df[(df['province'] == prov) & (df['city'] == city) & (df['district'] == district)]
        region_adcodes = list(df_district['district_adcode'])
        print('region_adcodes:', region_adcodes)
        return region_adcodes

    def start_requests(self):
        """
        将符合城市的坐标遍历进url
        """
        region_adcodes = self.get_regions()
        print(region_adcodes)

        log_info = """采集程序启动中！目标区域：【%s】;关键词：【%s】""" % (self.regions, self.keywords)
        self.Q.put(log_info)
        for region_adcode in region_adcodes:

            prop, poly = get_region_polyline(region_adcode)
            try:
                region_name = prop['name']
                # region_parent_name = prop['parent']['name']
                log_info = """已获取【%s-%s】的边界坐标""" % (self.regions.get('city'), region_name)
                self.Q.put(log_info)

                change_pt = ChangePosition(ak=self.ak, Q=self.Q)
                self.Q.put("获取目标区域的经纬度坐标成功，将要进行经纬度转换，此过程可能耗时较长，如果1分未响应，请停止后重新启动！")
                bd_poly = change_pt.geo_convert_no_limit_return_polygon(poly)
                print('百度poly', bd_poly)

                # self.crawler.engine.close_spider(self, "失效")
                # raise CloseSpider()
                params_tuple_lst = []
                for keyword in self.keywords:
                    self.Q.put("开始在【%s】获取关键词为【%s】的兴趣点" % (region_name, keyword))
                    params_tuple = (region_name, keyword, bd_poly)
                    params_tuple_lst.append(params_tuple)
                p = ThreadPool(processes=20)
                yield_urls = p.map(self.get_query_word_request_urls, params_tuple_lst)

                url_lists = list(self.yield_from_iter(yield_urls))
                logging.info('当前需要解析的url共有%s个' % len(url_lists))
                for url_query_word in url_lists:
                    url, keyword = url_query_word
                    yield self.make_requests_from_url(url, keyword, region_name, poly)
            except Exception as e:
                log_info = """获取【%s-%s】的poi时失败！""" % (self.regions.get('city'), region_name)
                self.Q.put(log_info)

    def yield_from_iter(self, yield_iters):
        for yield_iter in yield_iters:
            yield from yield_iter

    def get_query_word_request_urls(self, params_tuple):
        region_name, keyword, poly = params_tuple
        log_info = '获取区域边界坐标成功，当前关键词：%s，将根据该关键词在各个矩形区域内的pois数量切割区域' % keyword
        self.Q.put(log_info)
        obj = SplitRectangularArea(keyword=keyword, region_poly=poly, ak=self.ak, Q=self.Q)
        bounds_lst = obj.get_bounds_lst()
        print('关键词：%s\n bounds_lst个数：%s' % (keyword, len(bounds_lst)))
        self.Q.put('已获取关键词对应的矩形区域列表，下面开始解析')
        init_url = "http://api.map.baidu.com/place/v2/search?output=json" \
                   "&query={keyword}" \
                   "&page_size=20" \
                   "&scope=2" \
                   "&bounds={bounds}" \
                   "&ak={ak}" \
                   "&page_num={page_num}"
        request_urls = []
        for bounds in bounds_lst:
            start_url = init_url.format(keyword=keyword, bounds=bounds, ak="{ak}", page_num="{page_num}")
            url_lst = [start_url.format(ak="{ak}", page_num=x) for x in range(20)]
            request_urls.extend(url_lst)
            for url in url_lst:
                # query_word和region_name只是为了记录
                yield url, keyword

    def make_requests_from_url(self, url, keyword, region_name, poly):
        # query_word和region_name只是为了记录

        ak = self.ak
        response = scrapy.Request(url.format(ak=ak), callback=self.parse_judge_success, errback=self.errback_httpbin,
                                  dont_filter=True)
        response.meta['ak'] = ak
        response.meta['raw_url'] = url
        response.meta['keyword'] = keyword
        response.meta['region'] = region_name
        response.meta['poly'] = poly
        return response

    def parse_judge_success(self, response):
        ak, raw_url, keyword, region, poly = response.meta['ak'], response.meta['raw_url'], \
                                             response.meta['keyword'], response.meta['region'], response.meta[
                                                 'poly']
        data = json.loads(response.text)
        status_code = data['status']
        if status_code != 0:
            message = data.get('message')
            # 对于失效ak对应的raw_url重新进行请求
            self.Q.put('采集异常！\n错误信息:%s\n当前使用的ak:%s无效，请求目标url:%s' % (message, ak, response.url))
            # self.make_requests_from_url(raw_url, keyword=keyword, region_name=region, poly=poly)

        else:
            item = BaidumapwebapispierItem()
            item['results'] = data['results']
            item['search_word'] = keyword
            item['region'] = region
            item['requests_url'] = response.url
            item['poly'] = poly
            if item['results']:
                yield item

    def errback_httpbin(self, failure):
        self.Q.put("请求失败：%s" % failure)

    def close(spider, reason):
        '''
        reason (str) – 描述spider被关闭的原因的字符串。
        如果spider是由于完成爬取而被关闭，则其为 'finished' 。
        否则，如果spider是被引擎的 close_spider 方法所关闭，
        则其为调用该方法时传入的 reason 参数(默认为 'cancelled')。
        如果引擎被关闭(例如， 输入Ctrl-C)，则其为 'shutdown' 。
        '''
        spider.Q.put('采集结束!\n结束原因：%s' % reason)
        print(os.getcwd())
        with open('log.txt', 'r', encoding='utf8') as f:
            logs = f.read()
        if "AttributeError: 'NoneType' object has no attribute 'exterior'" in logs:
            info = '你当前输入的行政区域不正确！请确保你输入的行政区域为【省、市、区县】三个级别中的任一区域名称或者adcode'
            url = '<a href = \"https://docs.qq.com/sheet/DYVZ2SFpiWFhBS2pJ">点击查看中国省市区县adcode大全</a>'
            loginfo = '<br />'.join([info, url])
            spider.Q.put(loginfo)
        elif "AttributeError: 'LGEOS360' object has no attribute 'GEOSGeom_destroy'" in logs:
            pass
        elif 'Error' in logs:
            spider.Q.put("采集过程出现异常！异常详情:\n %s" % logs)


if __name__ == "__main__":
    obj = WebApiCrawler()
