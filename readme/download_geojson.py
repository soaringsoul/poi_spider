#!/usr/bin/env python
# coding: utf-8

# In[34]:


import requests
import pandas as pd
import os


# In[35]:


url="https://geo.datav.aliyun.com/areas_v2/bound/410324.json"
_json=requests.get(url).json()
_json.keys()


def parm_url_to_json(adcode):
    _parms = {
        'keywords': '%s' % adcode,
        'key':'e3b81819a4f03cd2d4d66cb1b9646283',
        'subdistrict': '3',
        'showbiz': 'true',
        'extensions': 'all' ,
        'output': 'json',
        'filter': '' ,
        'page': '1' 
    }
    url = 'http://restapi.amap.com/v3/config/district'
    res = requests.get(url,params=_parms)
    print(res.url)
    _json =res.json()

    return _json
_json=parm_url_to_json("410324")
_json.keys()


df = pd.read_excel("中华人民共和国_各城市区县名.xlsx")
district_adcodes=set(df['区县adcode'])
adcodes_district={}
# for adcode in district_adcodes:
#     _json = parm_url_to_json(adcode)
#     name = _json['districts'][0]['name']
#     poly=_json['districts'][0]['polyline']
#     center=_json['districts'][0]['center']
#     tmp_dict= {"name":name,'polyline':poly,'center':center}
#     tmp_df = pd.DataFrame([list(tmp_dict.values())],columns=['1','2','3'])
#     print(tmp_df)

df = pd.read_csv("adcodes.csv",encoding='utf8')
print(df)



