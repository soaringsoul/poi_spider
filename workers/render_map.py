from PyQt5 import QtCore
import pandas as pd
import codecs
import os
import sqlite3
import mysql


class RenderMap(QtCore.QThread):
    finished_signal = QtCore.pyqtSignal(str)
    error_signal = QtCore.pyqtSignal(str)
    result_signal = QtCore.pyqtSignal(str)
    progress_signal = QtCore.pyqtSignal(str)

    def __init__(self, csv_fname, regions):
        super(RenderMap, self).__init__()
        self.csv_fname = csv_fname
        self.regions = regions



    def get_center(self):
        prov = self.regions['prov']
        city = self.regions['city']
        district = self.regions['district']
        print('district【%s】' % district, type(district))
        if district == "全部区县":
            district = ""
        if city == "全部城市":
            city = ""
        query = """
                select * from china_areas
                where district like '%{district}%'
                and province like '%{prov}%'
                and city like '%{city}%'
                """.format(district=district, prov=prov, city=city)
        # df = pd.read_sql(query)
        # if district not in ['',None,"全部区县"]:
        print(query)
        result = mysql.query_str(q_str=query)
        print(result)
        if result:
            if district not in ['全部区县', '']:
                # 取区县中心
                point_str = result[0][9]
            else:
                if city == "全部城市":
                    # 取省中心
                    point_str = result[0][2]
                else:
                    # 取市中心
                    point_str = result[0][6]
            x = point_str.split(',')
            point = [float(x[0]), float(x[1])]
            return point
        else:
            return None

    def clean(self, df):
        # 去重
        df = df.drop_duplicates()
        # 区域筛选

        df = df[df['isin_region'] == "True"]
        df = df[df['isin_region'] != "isin_region"]
        return df

    def gen_js(self, df, js_name):
        points_lst = []
        for index, row in df.iterrows():
            location = row['location']
            name = row['name']
            address = row['address']

            if location != "None":
                location = eval(location)
                tmp_lst = [location['lng'], location['lat'], name, address]
                points_lst.append(tmp_lst)
                points_lst.append(tmp_lst)
        center_point = self.get_center()
        print("中心点坐标", center_point)
        if center_point is None:
            center_point = points_lst[0]

        fl = codecs.open('%s' % js_name, 'w', 'utf-8')
        for file in ['var data= {"data":%s,"center_point":%s}' % (str(points_lst), str(center_point))]:
            fl.write(file)
            fl.write("\n")
        fl.close()

    def run(self):
        try:
        #读取csv数据
        # self.get_regions()
            print(self.csv_fname)
            self.progress_signal.emit("正在读取采集到的poi csv文件：【%s】" % self.csv_fname)
            file_path = r'./result/%s' % self.csv_fname
            # df = pd.read_excel(excel_fp)
            df = pd.read_csv(r'%s' % file_path)

            df = self.clean(df)
            js_fp = r'./html/address.js'
            html_fp = r"./html/template.html"
            self.gen_js(df, js_name=js_fp)

            abs_path = os.path.abspath(html_fp)
            abs_path = r'file:///%s' % abs_path
            # webbrowser.open()
            self.result_signal.emit(
                '成功生成地图文件！<a href="%s" style="color:#0000ff;"><b> 点击在浏览器中打开</b></a>' % abs_path)
        except Exception as e:
            self.error_signal.emit("生成地图数据失败，错误详情：%s" % e)
            self.progress_signal.emit("生成地图数据失败，错误详情：%s" % e)
