import requests
import re
from shapely.geometry import Polygon


def get_region_polyline(region_adcode):
    """
    :param region:需要查询的城市（代码）或者省份（代码），eg:成都市
    :return:该区域的经纬度边界线坐标字符串，eg:114.2134521,29.59778924;114.281,29.575924
    """
    url = "https://geo.datav.aliyun.com/areas_v2/bound/%s.json" % region_adcode
    resq = requests.get(url)
    print(resq.json())
    try:
        _json = resq.json()
        feature = _json['features'][0]

        coords = feature['geometry']['coordinates'][0][0]
        print(coords)
        polyline = Polygon(coords)

        prop = feature['properties']
        # new_coords = [','.join([str(x[0]), str(x[1])]) for x in coords]
        # polyline = ";".join(new_coords)

        region_name = prop['name']
        print(region_name, polyline)
        return prop, polyline
    except Exception as e:
        print(url)
        print(e)
        return None,None

if __name__ == "__main__":
    region_adcode = "310151"
    result = get_region_polyline(region_adcode)

