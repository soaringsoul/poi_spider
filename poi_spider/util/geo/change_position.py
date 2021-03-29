import logging
from multiprocessing.dummy import Pool

import requests
from shapely.geometry import Polygon


class ChangePosition(object):
    def __init__(self, ak, Q):
        self.ak = ak
        self.Q = Q

    def check_ak_status(self, status_code):
        # 检测使用的ak是否异常
        error_code_list = [x for x in range(201, 500)] + [2, 3, 4, 5, 101, 102]
        is_ok = True
        if status_code in error_code_list:
            is_ok = False
        return is_ok

    def chunksBySize(self, arr, n):
        return [arr[i:i + n] for i in range(0, len(arr), n)]

    def gen_result(self, list_lst):
        """
        :param list_lst: 元素为列表的列表，eg:[[1,2],[3,4]]
        :return: list, yield
        """

        for list in list_lst:
            if list is not None:
                yield from list

    def geo_convert_no_limit(self, coords):
        """
        :param coords:需转换的单个源坐标，多组坐标以“；”分隔（经度，纬度),eg:114.2134521,29.59778924;114.281,29.575924
        可以转换任意多组坐标
        :return:转换后的坐标信息字符串，eg:[{"x":114.22528953969952,"y":29.60137189934183},{"x":114.29291174610977,"y":29.579087079077703}]
        """
        split_coords_lst = coords.split(';')
        length = len(split_coords_lst)
        self.Q.put('开始转换经纬度坐标为百度地图坐标，共计%s个坐标， 请耐心等待' % length)
        # 百度地图坐标转换接口一次最多接收100个坐标
        if length > 100:
            pool = Pool(10)
            split_coords_lst = self.chunksBySize(split_coords_lst, 100)
            coords_lst = [';'.join(x) for x in split_coords_lst]
            result_lst = pool.map(self.geo_convert_limit, coords_lst)
            result_coords_lst = list(self.gen_result(result_lst))
        else:
            result_coords_lst = self.geo_convert_limit(coords)
        logging.info('转换完成，共转换了%s个坐标' % len(result_coords_lst))
        print('转换完成，共转换了%s个坐标' % len(result_coords_lst))
        return result_coords_lst

    def geo_convert_limit(self, coords):
        """
        :param coords:需转换的源坐标，多组坐标以“；”分隔（经度，纬度),eg:114.2134521,29.59778924;114.281,29.575924
        注意：多组坐标不能超过100个
        :return:转换后的坐标信息字符串，eg:[{"x":114.22528953969952,"y":29.60137189934183},{"x":114.29291174610977,"y":29.579087079077703}]
        """
        url = 'http://api.map.baidu.com/geoconv/v1/?'
        params = {
            'coords': '%s' % coords,
            'ak': '%s' % self.ak,
            'from': '3',
            'to': '5',
            'output': 'json'}
        try:
            res = requests.get(url, params=params, timeout=60)

            return res.json()['result']
        except Exception as e:
            logging.info("change_position时出错，错误详情：%", e)

    def geo_convert_no_limit_return_polygon(self, poly):
        # 获取区域边界上百度地图经纬度坐标，poly是shapely.Polygon类型
        bd_coords_lst = list(poly.exterior.coords)
        bd_coords_lst = [','.join([str(x[0]), str(x[1])]) for x in bd_coords_lst]
        bd_coords = ';'.join(bd_coords_lst)
        print('将要开始转换')
        result = self.geo_convert_no_limit(coords=bd_coords)
        bd_coords_lst = result
        coords_for_polygon = [(point['x'], point['y']) for point in bd_coords_lst]
        return Polygon(coords_for_polygon)


if __name__ == "__main__":
    coords = r'114.2134521,29.59778924;114.281,29.575924'
    coords = ';'.join(['114.2134521,29.59778924' for x in range(10083)])
    obj = ChangePosition(ak='dASz7ubuSpHidP1oQWKuAK3q')
    points = obj.geo_convert_no_limit(coords)
    print(points)
    print(len(points))
