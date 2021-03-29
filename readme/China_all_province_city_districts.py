import requests
import pandas as pd
from pandas import DataFrame
import json
from sqlalchemy import create_engine
import re
import os


class Get_all_districts_in_China(object):
    def __init__(self,keyword):
        """
        规则：只支持单个关键词语搜索关键词支持：行政区名称、citycode、adcode
        例如，在subdistrict=2且showbiz=false时，搜索省份（例如山东），能够显示市（例如济南），区（例如历下区）
        在subdistrict=1且showbiz=false时，搜索区（例如历下区）能够显示街道信息（例如舜华路街道）"""
        self.keywords = keyword
        if self.keywords == '中国' or self.keywords == '中华人民共和国':
            self.col_name = ['country', 'country_adcode', 'country_center'] \
                              + ['province', 'province_adcode', 'province_center'] \
                              + ['city', 'city_adcode', 'citycode', 'city_center'] + \
                              ['district', 'district_adcode', 'district_center']
        else:
            self.col_name = ['province', 'province_adcode', 'province_center'] \
                            + ['city', 'city_adcode', 'citycode', 'city_center'] + \
                            ['district', 'district_adcode', 'district_center']+\
                            ['street','street_adcode','street_center']
        self.key = 'e3b81819a4f03cd2d4d66cb1b9646283'
        """
        规则：设置显示下级行政区级数（行政区级别包括：国家、省/直辖市、市、区/县、商圈、街道多级数据），
        其中街道数据仅在keywords为区/县、商圈的时候显示
        可选值：0、1、2、3等数字，并以此类推
        0：不返回下级行政区；
        1：返回下一级行政区；
        2：返回下两级行政区；
        3：返回下三级行政区；
        """
        self.subdistrict = '3'
        # 是否显示商圈
        self.showbiz = 'true'
        # 最外层返回数据个数,最大20
        self.offset = '20'
        """此项控制行政区信息中返回行政区边界坐标点； 可选值：base、all;
            base:不返回行政区边界坐标点；
            all:只返回当前查询district的边界值，不返回子节点的边界值；"""
        self.extensions = 'all'
        self.output = 'JSON'
        # 按照指定行政区划进行过滤，填入后则只返回该省/直辖市信息,需填入adcode，为了保证数据的正确，强烈建议填入此参数
        self.filter= ''
        self.page = '1'
        # self.engine = create_engine('mysql+pymysql://root:123456@localhost:3306/data_from_map_api?charset=utf8', echo=False)
        self.parm_url_to_json()

    def parm_url_to_json(self):
        _parms = {
            'keywords': '%s' % self.keywords,
            'key': '%s'% self.key,
            'subdistrict': '%s' % self.subdistrict,
            'showbiz': '%s' % self.showbiz,
            'extensions': '%s' % self.extensions,
            'output': '%s' % self.output,
            'filter': '%s' % self.filter,
            'page': '%s' % self.page
        }
        url = 'http://restapi.amap.com/v3/config/district'
        res = requests.get(url,params=_parms)
        print(res.url)
        data_json =res.json()
        self.data_json = data_json
        return self.data_json

    def parse_json_to_excel(self):
        data_json = self.data_json
        """data_json_里的数据:
        {
        'count':1,
        'districts':[{中华人民共和国，……}]

        }
        """
        base_info_list_name=['country','country_adcode','country_center']
        base_info_list = []
        districts_with_country = data_json['districts'][0]
        keys=['name','adcode','center']
        for key in keys:
            base_info_list.append(districts_with_country[key])
        data_list = []
        districts_with_province = districts_with_country['districts']
        """districts_with_province里的数据:
               {
               'count':1,
               'districts':[{省1},{省2}，……]
               }
               """
        for result in districts_with_province:
            print('正在处理【{0}】'.format(result['name']))
            province_info_lst = [x for x in base_info_list]
            keys = ['name', 'adcode', 'center']
            for key in keys:
                province_info_lst.append(result[key])
            print('该省的基本信息为:\n{0}'.format(province_info_lst))
            base_info_list_name = ['country', 'country_adcode', 'country_center'] \
                                      + ['province','province_adcode','province_center']


            districts_with_city = result['districts'] #列表，元素为各省各城市的城市信息
            for result in districts_with_city:
                city_info_list =[x for x in province_info_lst]
                keys = ['name', 'adcode', 'citycode','center']
                for key in keys:
                    city_info_list.append(result[key])
                # base_info_list_name = ['country', 'country_adcode', 'country_center']\
                #                               +['province', 'province_adcode', 'province_center']\
                #                               +['city','city_adcode','citycode','city_center']
                districts_with_district = result['districts']
                for result in districts_with_district:
                    district_info_list = [x for x in city_info_list]
                    keys = ['name', 'adcode','center']
                    for key in keys:
                        district_info_list.append(result[key])
                    base_info_list_name = ['country', 'country_adcode', 'country_center'] \
                                                      + ['province', 'province_adcode', 'province_center'] \
                                                      + ['city', 'city_adcode', 'citycode', 'city_center']+\
                                                      ['district','district_adcode','district_center']

                    data_list.append(district_info_list)
                    print(district_info_list)
                    print(len(district_info_list))


        df = DataFrame(data_list,columns=self.col_name)
        # if os.path.exists(r'G:\Get_City_All_Streetname_Project\全国各城市区县名获取\%s' % self.keywords) is False:
        #     os.makedirs(r'G:\Get_City_All_Streetname_Project\全国各城市区县名获取\%s' % self.keywords)
        # df.to_excel(r'%s_各城市区县名.xlsx' % self.keywords, index=False)
        # df.to_csv('China.csv', encoding='utf8')
        return df




if __name__ == "__main__":
    # 可以输入省名，或者直接输入中国，查询全国所有的省市区县，若输入为省，则会精确到道路
    keyword = '中国'
    # df_prov = pd.read_excel("中华人民共和国_各城市区县名.xlsx")
    # df_lst = []
    #
    # city_lst = [x for x in set(df_prov['区县adcode'])]
    # for keyword in ['太康县']:
    obj = Get_all_districts_in_China(keyword)
    df = obj.parse_json_to_excel()



    print(df)
    # file_name = '_'.join(city_lst)
    df.to_excel(r'%s_各城市区县名.xlsx' % keyword, index=False)







