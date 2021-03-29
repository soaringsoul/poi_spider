import requests
import re
from shapely.geometry import Polygon


def get_region_polyline(region,gd_key):
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
        points = [[float(x.split(',')[0]), float(x.split(',')[1])] for x in polyline.split(';')]
        print(points)
        poly = Polygon(points)
        return poly
    except Exception as e:
        print('从高德地图api获取行政区域失败，错误详情：%s' % e)
        return None



if __name__ == "__main__":
    region = '深圳市'
    polyline = get_region_polyline(region,gd_key="e3b81819a4f03cd2d4d66cb1b9646283")
    print(polyline.bounds)