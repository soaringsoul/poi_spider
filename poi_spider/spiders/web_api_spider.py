import logging
import scrapy
import os

from scrapy.spiders import Spider
from datetime import datetime
from pandas import DataFrame
import pandas as pd

import json
from multiprocessing.dummy import Pool as ThreadPool

from poi_spider.util.geo.district import get_region_polyline
from poi_spider.util.geo.GetRegionBounds import SplitRectangularArea

from poi_spider.items import BaidumapwebapispierItem
# from poi_spider.util.email.send_email import send_email_163
from poi_spider.util.geo.change_position import ChangePosition


class WebApiCrawler(Spider):
    name = 'bd_map_spider'

    def __init__(self, Q=None, settings=None):
        self.settings = settings
        self.storage = settings.get("storage")
        self.csv_fname = settings.get("csv_fname")
        self.regions = settings.get('regions')
        self.ak_lst = settings.get('ak_list')
        self.gd_key = settings.get('gd_key')
        self.keywords = settings.get('keywords')
        self.Q = Q
        self.error_code_list = [x for x in range(201, 500)] + [2, 3, 4, 5, 101, 102]

    def start_requests(self):
        """
        将符合城市的坐标遍历进url
        """
        log_info = """采集程序启动中！目标区域：【%s】;关键词：【%s】""" % (self.regions, self.keywords)
        self.Q.put(log_info)
        for region_name in self.regions:
            log_info = """正在获取【%s】的边界坐标""" % region_name
            self.Q.put(log_info)
            poly = get_region_polyline(region_name, gd_key=self.gd_key)

            change_pt = ChangePosition(ak=self.ak_lst[0], Q=self.Q)
            self.Q.put("获取目标区域的经纬度坐标成功，将要进行经纬度转换，此过程可能耗时较长，如果1分未响应，请停止后重新启动！")
            bd_poly = change_pt.geo_convert_no_limit_return_polygon(poly)

            # self.crawler.engine.close_spider(self, "失效")
            # raise CloseSpider()
            params_tuple_lst = []
            for keyword in self.keywords:
                self.Q.put("开始在【%s】获取关键词为【%s】的兴趣点" % (self.regions, keyword))
                params_tuple = (region_name, keyword, bd_poly)
                params_tuple_lst.append(params_tuple)
            p = ThreadPool(processes=20)
            yield_urls = p.map(self.get_query_word_request_urls, params_tuple_lst)

            url_lists = list(self.yield_from_iter(yield_urls))
            logging.info('当前需要解析的url共有%s个' % len(url_lists))
            for url_query_word in url_lists:
                url, keyword = url_query_word
                yield self.make_requests_from_url(url, keyword, region_name, poly)

    def yield_from_iter(self, yield_iters):
        for yield_iter in yield_iters:
            yield from yield_iter

    def get_query_word_request_urls(self, params_tuple):
        region_name, keyword, poly = params_tuple
        log_info = '获取区域边界坐标成功，当前关键词：%s，将根据该关键词在各个矩形区域内的pois数量切割区域' % keyword
        self.Q.put(log_info)
        obj = SplitRectangularArea(keyword=keyword, region_poly=poly, ak=self.ak_lst[0], Q=self.Q)
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

        ak = self.ak_lst[0]
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

    def bad_ak_process(self, ak, status_code, message):

        # ak使用异常会通过邮件提醒
        email_subject = '百度地图PlaceAPi ak异常状态通知'
        email_body = """
                                   Mr Xu:
                                       当前使用的ak：{ak} 状态码为 {status}；异常信息为：{message}!
                                       使用异常！请知悉！

                                   """.format(ak=ak, status=status_code, message=message)

        try:
            bad_ak_df = pd.read_csv(r'bad_ak_lst.csv')
            bad_ak_lst = [x for x in bad_ak_df['bad_ak']]
            # if ak not in bad_ak_lst:
            #     send_email_163(email_subject, email_body, 'bad_ak_lst.csv')
        except Exception as e:
            logging.info(e)

        write_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df_bad_ak = DataFrame([[ak, status_code, message, write_time]],
                              columns=['bad_ak', 'status_code', 'message', '写入时间'])
        df_bad_ak.to_csv('bad_ak_lst.csv', mode='a+', index=False)

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
        if "ERROR" in logs:
            spider.Q.put('采集过程出现异常！异常详情：\n%s' % logs)
        else:
            spider.Q.put("采集完成！，正在将csv文件转为excel，请耐心等待！")
            try:
                csv_fname = spider.settings.get('csv_fname')
                df = pd.read_csv('./result/%s' % csv_fname, encoding='utf8')
                df = df[df['name'] != 'name']
                print(df.shape)
                df.to_excel(r"./result/%s.xlsx" % os.path.basename(csv_fname).strip('.csv'), index=False)
                spider.Q.put("转换完成！你现在可以到程序根目录下查看采集结果文件了！")
            except Exception as e:
                print(e)


if __name__ == "__main__":
    obj = WebApiCrawler()
