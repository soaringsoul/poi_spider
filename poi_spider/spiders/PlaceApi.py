import requests
import time
from numpy.random import randint
import logging


class PlaceApiByBounds(object):
    def __init__(self, keyword, url, ak):
        self.keyword = keyword
        self.ak = ak
        self.url = url

    def check_ak_status(self, status_code):
        # 检测使用的ak是否异常
        error_code_list = [x for x in range(201, 500)] + [2, 3, 4, 5, 101, 102]
        is_ok = True
        if status_code in error_code_list:
            is_ok = False
        return is_ok

    def get_response(self, page_num=0, ak=None):
        # 根据输入的页数，返回第page_num页面的解析数据，返回的是一个字典
        url = self.url.format(keyword=self.keyword, ak=self.ak, page_num=page_num)
        print(url)
        try:
            response = requests.get(url, timeout=20)
        except Exception as e:
            print(e)
            time.sleep(2)
            ak = self.ak
            return self.get_response(page_num=page_num, ak=ak)

        data = response.json()
        status_code = data['status']
        is_ak_ok = self.check_ak_status(status_code)
        if not is_ak_ok:
            logging.info('异常ak:%s' % ak)
            ak = 'dASz7ubuSpHidP1oQWKuAK3q'

            return self.get_response(page_num=page_num, ak=ak)
        else:
            # print('传入的关键词为【%s】' % self.keyword)
            # print('当前请求地址：%s' % response.url)
            return data
