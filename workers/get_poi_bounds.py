import pandas as pd
from PyQt5 import QtCore
import requests
import re
from shapely.geometry import shape, Point, Polygon

import logging
from poi_spider.util.geo.split_rectangle_area import split_rectanle_area
from poi_spider.spiders.PlaceApi import PlaceApiByBounds
from poi_spider.TailRecurseException import tail_call_optimized


from multiprocessing.dummy import Pool

MAX_TOTAL = 150


class SplitRectangularArea(QtCore.QThread):

    result_signal = QtCore.pyqtSignal(list)

    def __init__(self, keyword, region, ak, gd_key):
        super(SplitRectangularArea, self).__init__()
        self.keep_bounds_lst = []
        self.region = region
        self.poly = self.get_region_polyline(region=region, gd_key=gd_key)
        self.keyword = keyword
        self.ak = ak

        minx, miny, maxx, maxy = self.poly.bounds
        self.bounds = ','.join([str(x) for x in [miny, minx, maxy, maxx]])

        self.global_poly_lst = []

    def run(self):
        # 首次分割
        poly_lst = split_rectanle_area(self.poly)
        params_tuple = poly_lst, self.keyword
        global_poly_lst = self.get_bounds_lst_iter(params_tuple)
        self.keep_bounds_lst = [self.poly_lst_convert2_bounds_lst(x) for x in global_poly_lst]
        return self.keep_bounds_lst

    def get_region_polyline(self,region, gd_key):
        """
        :param region:需要查询的城市（代码）或者省份（代码），eg:成都市
        :return:该区域的经纬度边界线坐标字符串，eg:114.2134521,29.59778924;114.281,29.575924
        """

        _parms = {
            'keywords': '%s' % region,
            'key': '%s' % gd_key,
            'subdistrict': '3',
            'extensions': 'all',
            'output': 'JSON',
        }
        url = 'http://restapi.amap.com/v3/config/district'
        try:
            response = requests.get(url, params=_parms)
            data = response.json()
            print(response.url)
            # 获得城市边界坐标
            polyline = data['districts'][0]['polyline']
            # 匹配岛屿 ,polyline中若一个区域或者城市存在多个孤岛，则坐标以|lat,lng;lat,lng|分割
            """
            例如：polyline=113.823338,22.543809;113.823183,22.543825;113.823087,22.543947;
            """
            polyline = re.sub('\|', ';', polyline)
            points = [(float(x.split(',')[0]), float(x.split(',')[1])) for x in polyline.split(';')]
            print(points)
            poly = Polygon(points)
            return poly
        except Exception as e:
            print('从高德地图api获取行政区域失败，错误详情：%s' % e)
            return None

    def poly_lst_convert2_bounds_lst(self, poly):
        minx, miny, maxx, maxy = poly.bounds
        # 调整矩形分割精度, 后续再设置
        # 在原有分割矩形的基础上扩大10%
        deviation_x = (maxx - minx) * 0
        deviation_y = (maxy - miny) * 0
        bounds = ','.join(
            [str(x) for x in [miny - deviation_y, minx - deviation_x, maxy + deviation_y, maxx + deviation_x]])
        return bounds

    @tail_call_optimized
    def get_single_poly_bounds(self, params_tuple):
        """
        :param params_tuple: (poly, keyword)
        :return: [bounds1,bounds2, ……]
        """
        # bounds_lst默认为空列表
        poly, keyword = params_tuple
        minx, miny, maxx, maxy = poly.bounds
        # 调整矩形分割精度, 后续再设置
        # 在原有分割矩形的基础上扩大10%
        deviation_x = (maxx - minx) * 0.1
        deviation_y = (maxy - miny) * 0.1
        bounds = ','.join(
            [str(x) for x in [miny - deviation_y, minx - deviation_x, maxy + deviation_y, maxx + deviation_x]])
        url = "http://api.map.baidu.com/place/v2/search?output=json" \
              "&query={keyword}" \
              "&page_size=20" \
              "&scope=2" \
              "&bounds=%s" \
              "&ak={ak}" \
              "&page_num={page_num}" % bounds
        print('bounds:', bounds)
        data = PlaceApiByBounds(keyword=keyword, url=url, ak=self.ak).get_response()
        try:
            total = data['total']
            print("当前关键词下找到%s个兴趣点" % total)

            if total >= MAX_TOTAL:

                print('当前区域的兴趣点数量:%s，>=150,将再次进行分割' % total)
                return False, poly, total
            elif total > 0 and total < MAX_TOTAL:
                self.global_poly_lst.append(poly)
                return True, poly, total
            else:
                print('当前区域的兴趣点数量:%s,不再分割' % bounds)
                return True, poly, total

        except Exception as e:
            logging.info(e)

    def get_polys_bounds(self, params_tuple):
        poly, keyword = params_tuple
        poly_lst = split_rectanle_area(poly)
        params_tuple_lst = []
        for poly2 in poly_lst:
            params_tuple = poly2, keyword
            params_tuple_lst.append(params_tuple)
        p = Pool(processes=12)
        p.map(self.get_single_poly_bounds, params_tuple_lst)
        print('当前bounds_lst数量：%s' % len(self.keep_bounds_lst))

    @tail_call_optimized
    def get_bounds_lst_iter(self, params_tuple):
        poly_lst, keyword = params_tuple
        new_poly_lst = []
        poly_lst_iter = []
        # 将列表中的poly分割，一个变4个
        for poly in poly_lst:
            tmp_lst = split_rectanle_area(poly)
            poly_lst_iter.extend(tmp_lst)
        # 定义传入的参数列表
        params_tuple_lst = []
        for poly2 in poly_lst_iter:
            params_tuple = poly2, keyword
            params_tuple_lst.append(params_tuple)
        # 使用多线程
        p = Pool(processes=len(poly_lst_iter))
        results = p.map(self.get_single_poly_bounds, params_tuple_lst)
        for result in results:
            # check==false 不用再分割，total表示兴趣点数量
            check, poly, total = result
            # 若poly区域内兴趣点小于150个
            if check and total > 0:
                self.global_poly_lst.append(poly)
            # 若大于150个，加入新列表中准备递归分割
            elif not check and total >= MAX_TOTAL:
                new_poly_lst.append(poly)
        print('当前global_poly_list数量：%s' % len(self.global_poly_lst))
        if new_poly_lst:
            # 开始递归分割
            new_params_tuple = (new_poly_lst, keyword)
            return self.get_bounds_lst_iter(new_params_tuple)
        else:
            return self.global_poly_lst


if __name__ == "__main__":
    region = '温江区'
    ak='dASz7ubuSpHidP1oQWKuAK3q'
    gd_key='531087dfde1430ebe715db1176657dfd'

    obj = SplitRectangularArea(
        keyword='商场',
        region=region,
        ak=ak,
        gd_key=gd_key
    )
    bounds = obj.run()
