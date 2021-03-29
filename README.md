

<img align="right" width="200" height="200" src="https://pic4.zhimg.com/v2-78d1472351272f41d8dd76a6d8a635c7_xll.jpg">

# EasyPoi
### 原理

[获取中国指定行政区域内所有POIS(兴趣点)的方法](https://zhuanlan.zhihu.com/p/48081408)

### 功能
1. 获取中国境内指定行政区域内（最小可精确到街道）的指定关键词的所有兴趣点
例如可以获取一个城市内所有的便利店、商场、超市、咖啡店等兴趣点信息
2. 组合批量获取中国境内多个行政区域内多个关键词的所有兴趣点信息
3. 将所有采集到兴趣点数据存储到csv文件或者指定的`mysql`数据库中


----------

## 运行

![run](https://mmbiz.qpic.cn/mmbiz_gif/zFSfia9fsoicFQtbKIdQTEH3BtLE2WibF41zFhib0x70uSiayaiaWkLArzupB4xqCU2g4bonWhjZRVib3wibjoanu2uVdQ/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)



## 准备工作


使用`pip install requirements.txt`安装依赖库

## 启动

`python easy_poi.py`

启动后在窗口里进行相应的设置后，点击启动开始采集。

![main](https://mmbiz.qpic.cn/mmbiz_png/zFSfia9fsoicFQtbKIdQTEH3BtLE2WibF41Zze0anzUIEg6VVEkUzbmaCDsFNCQIlUhdKcGhbXzkZCK866k8hibjMw/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1)

## 设置说明

#### 1 设置高德地图开发平台api_key

用于调用高德地图行政区域服务（有次数限制：3万次/天），每个行政区域只调用一次，3万次/理论是足够了的。

高德地图开发者key申请链接：	https://lbs.amap.com/


#### 2 设置百度地图开发平台ak

申请地址：[百度地图开放平台](http://lbsyun.baidu.com/)

API设置



#### 3 设置需要获取的区域 列表,可以填写多个省、市、区县，也可以填写省、市、区县的代码，具体可参考高德地图开放平台：行政区划查询接口

"成都市", "德阳市", '成都市武侯区'


#### 4 设置需要获取的兴趣点关键词，同样是列表，可填写多个

'超市', '咖啡馆'
#### 5  设置存储方式

默认使用csv文件进行存储，每次采集结束会将csv文件写转为excel。
csv的写入模式为追加模式，如果经常使用，注意下这个csv文件，否则转换为excel时会耗时较长。

#### 6 采集结果示例

* csv

![result_csv](https://pic3.zhimg.com/80/v2-f5f25aa2ad2c7fe1fd20f89069921aee_720w.jpg)

* excel

![result_excel](https://pic3.zhimg.com/80/v2-03befe01d1f890ac48f12b42f513e13e_720w.jpg)

* mysql

![result_excel](https://pic3.zhimg.com/80/v2-aacdf72a7f5611ef8bf8e9b45db6ff66_720w.jpg)



## 联系我

如果在使用过程中遇到无法解决的问题，你可以通过关注我的个人公众号找到我。

另外，也可以通过提交issue的方式提交问题。

![supportme](https://mmbiz.qpic.cn/mmbiz_jpg/zFSfia9fsoicFGymqxJTNf5TqjyVyRHmyUfF78ibS53UibZ4FbFCdtpDropg2NrWaBltyyj3NdvMI1b5XC7fJibsIbA/640?wx_fmt=jpeg&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1)


## License


[Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0.html).



