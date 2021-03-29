# encoding = utf-8
# =====================================================
#   Copyright (C) 2021 All rights reserved.
#   author   : gongzi.xu / 95168339@qq.com
#   date     : 2021/01/09
# =====================================================
from multiprocessing import Process, Manager, freeze_support
import uuid
import pypinyin

import os, json, time
import platform
import requests
import configparser
from PyQt5.QtGui import QFont
from PyQt5 import QtGui
from PyQt5.QtCore import QUrl, QFileInfo, pyqtSlot
from PyQt5.QtWidgets import *

from ui.ImageWindow import ImageWindow

from workers.log_thread import LogThread
from workers.update_check import UpdateCheck
from workers.csv_to_excel import CsvToExcel
from workers.render_map import RenderMap

from settings_gui import SettingsGui

from ui import images_rc
from multiprocessing import Process, Manager, freeze_support

from scrapy.crawler import CrawlerProcess
from poi_spider.spiders.web_api_spider import WebApiCrawler
from scrapy.utils.project import get_project_settings

from ui.Ui_main import Ui_MainWindow
from china_areas import areas

from ImageWindow import ImageWindow
from PyQt5 import QtWidgets, QtCore
from generate_cfg import gen_scrapycfg
import webbrowser
import urllib.robotparser

import scrapy.spiderloader
import scrapy.statscollectors
import scrapy.logformatter
import scrapy.dupefilters
import scrapy.squeues

import scrapy.extensions.spiderstate
import scrapy.extensions.corestats
import scrapy.extensions.telnet
import scrapy.extensions.logstats
import scrapy.extensions.memusage
import scrapy.extensions.memdebug
import scrapy.extensions.feedexport
import scrapy.extensions.closespider
import scrapy.extensions.debug
import scrapy.extensions.httpcache
import scrapy.extensions.statsmailer
import scrapy.extensions.throttle

import scrapy.core.scheduler
import scrapy.core.engine
import scrapy.core.scraper
import scrapy.core.spidermw
import scrapy.core.downloader

import scrapy.downloadermiddlewares.stats
import scrapy.downloadermiddlewares.httpcache
import scrapy.downloadermiddlewares.cookies
import scrapy.downloadermiddlewares.useragent
import scrapy.downloadermiddlewares.httpproxy
import scrapy.downloadermiddlewares.ajaxcrawl
# import scrapy.downloadermiddlewares.chunked
import scrapy.downloadermiddlewares.decompression
import scrapy.downloadermiddlewares.defaultheaders
import scrapy.downloadermiddlewares.downloadtimeout
import scrapy.downloadermiddlewares.httpauth
import scrapy.downloadermiddlewares.httpcompression
import scrapy.downloadermiddlewares.redirect
import scrapy.downloadermiddlewares.retry
import scrapy.downloadermiddlewares.robotstxt

import scrapy.spidermiddlewares.depth
import scrapy.spidermiddlewares.httperror
import scrapy.spidermiddlewares.offsite
import scrapy.spidermiddlewares.referer
import scrapy.spidermiddlewares.urllength

import scrapy.pipelines

import scrapy.core.downloader.handlers.http
import scrapy.core.downloader.handlers.datauri
import scrapy.core.downloader.handlers.file
import scrapy.core.downloader.handlers.s3
import scrapy.core.downloader.handlers.ftp
import scrapy.core.downloader.contextfactory

CURRENT_VERSION = 2.4
SETTINGS_JSON_PATH = "./data/settings.json"
config_fp = "./data/config.ini"


def scrapy_spider_run(Q, config_dict):
    # CrawlerProcess
    settings = get_project_settings()
    for k, v in config_dict.items():
        settings[k] = v

    process = CrawlerProcess(settings)
    process.crawl(WebApiCrawler, Q=Q, settings=settings)
    process.start()


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):

        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.log_browser.setOpenExternalLinks(True)
        self.label_progress.setOpenExternalLinks(True)

        self.config_fp = config_fp
        # 保存配置项时是否弹窗提示标识 ，若为保存按钮触发有弹窗，否则无弹窗
        self.setWindowTitle("EasyPoi_v%s" % CURRENT_VERSION)

        self.init_sign()
        self.init_data()

        # self.label_progress.setOpenExternalLinks(True)

        # 多进程初始化
        self.p = None
        self.Q = Manager().Queue()
        self.log_thread = LogThread(self)
        self.log_thread.sinOut.connect(self.getLogContent)  # pyqt5信号，用于子线程和主页面通信

    def init_sign(self):
        # 添加关注公众号弹窗
        self.support_me_window = ImageWindow(':/main/img/supportme.jpg', '支持我一下吧！')

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/img/easypoi.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.support_me_window.setWindowIcon(icon)


        # self.toolButton_search.clicked.connect(lambda: self.crawl_slot(self.toolButton_search))
        self.toolButton_search.clicked.connect(self.crawl_slot)
        # self.toolButton_supportme.clicked.connect(self.show_support_me)
        # self.toolButton_help.clicked.connect(self.help)
        # self.toolButton_update.clicked.connect(self.check_update_version)
        # self.toolButton_setting.clicked.connect(self.show_settings_frame)
        self.action_settings.triggered.connect(self.open_settings_gui)

        self.action_support_me.triggered.connect(self.show_support_me)
        self.action_help_2.triggered.connect(self.help)
        self.action_update_doc.triggered.connect(self.released_doc)
        self.action_check_update_2.triggered.connect(self.check_update_version)

        # self.toolButton_save.clicked.connect(self.write_config)

        self.action_open_result_dir.triggered.connect(self.open_result_file_dir)
        self.action_to_excel.triggered.connect(self.csv2excel)

        # keywords实时显示在启动框
        # self.lineEdit_keywords.textChanged.connect(self.show_keywords)
        # self.lineEdit_keywords.textChanged.connect(lambda x: self.lineEdit_search.setText(x))
        # self.lineEdit_search.textChanged.connect(lambda x: self.lineEdit_keywords.setText(x))
        # self.ComboBox_storage.currentTextChanged.connect(self.show_while_combox_change)
        # self.LineEdit_regions.textChanged.connect(lambda x: self.lineEdit_csv_name.setText(self.topinyin(x)))
        # tab切换信号
        self.tabWidget.currentChanged.connect(self.change_tab)

    def open_settings_gui(self):
        prov = self.comboBox_prov.currentText()
        city = self.comboBox_city.currentText()
        district = self.comboBox_district.currentText()
        if district == "全部区县":
            district = ""
        if city == "全部城市":
            city = ""
        if prov == "请选择":
            prov = ""
        regions = [x for x in [prov, city, district] if x != '']
        if regions:
            suggested_fname = self.topinyin('_'.join(regions))
            print(suggested_fname)
        else:
            suggested_fname = "poi_data.csv"

        self.settings_gui = SettingsGui(suggested_fname=suggested_fname)
        self.settings_gui.show()

    def topinyin(self, s):
        s = s.strip()
        split = pypinyin.lazy_pinyin(s)
        if split:
            s_str = "".join(split)
            name = "%s.csv" % s_str

        else:
            name = "poi_data.csv"
        return name

    def init_data(self):
        # 生成scrapy cfg
        self.init_area_combox()
        url = "https://mp.weixin.qq.com/s?__biz=Mzg5NzIyODU3Mg==&mid=100002690&idx=1&sn=1a5ebb081b9546a1e9564195f1480d9b"
        self.webview_todo.load(QUrl(url))
        easypoi_mainpage="http://soaringsoul.gitee.io/easypoi/"
        self.web_engine_view.load(QUrl(easypoi_mainpage))

        try:
            if not os.path.exists('./scrapy.cfg'):
                gen_scrapycfg()
            if not os.path.exists('./result'):
                os.mkdir('result')
            self.read_config()
        except Exception as e:
            MyQMessageBox('温馨提示', '数据初始化失败！请以管理员身份运行此程序！%s' % e, '确定', '取消')

        self.settings_json = self.read_local_json(fp=SETTINGS_JSON_PATH)
        # 从云端拉取settings_json
        self.update = UpdateCheck(current_verison=CURRENT_VERSION)
        self.update.result_signal.connect(self.refresh_settings_json)
        self.update.start()

    def init_area_combox(self):
        provs = areas['province']
        self.comboBox_prov.clear()
        self.comboBox_prov.addItem('请选择')
        self.comboBox_prov.addItems(provs.keys())

    # 初始化城市
    @pyqtSlot(int)
    def on_comboBox_prov_activated(self, index):
        provs = areas['province']
        prov = self.comboBox_prov.currentText()
        if prov != "请选择":
            self.comboBox_city.clear()
            self.comboBox_city.addItem('全部城市')
            cities = provs[prov]
            self.comboBox_city.addItems(cities)

    # 初始化区县
    @pyqtSlot(int)
    def on_comboBox_city_activated(self, index):
        city = self.comboBox_city.currentText()
        self.comboBox_district.clear()
        if city not in [None, "请选择", '全部城市']:
            self.comboBox_district.addItem('全部区县')
            district_names = areas['district_names']
            districts = district_names.get(city)
            self.comboBox_district.addItems(districts)

    def check_api_key(self, bd_ak):
        valid = False
        valid_words = []
        # gd_url = "https://restapi.amap.com/v3/config/district?keywords=成都&subdistrict=0&key=%s" % gd_key
        bd_url = "http://api.map.baidu.com/place/v2/search?query=ATM机&tag=大学&region=成都&output=json&ak=%s" % bd_ak
        print(bd_url)
        try:
            bd_res = requests.get(bd_url, timeout=3)
            bd_status_code = bd_res.json()['status']
            if bd_status_code == 0:
                valid = True
            # if gd_status_code != "10000":
            #     valid_words.append('高德地图apikey:%s无效' % gd_key)
            if bd_status_code != 0:
                print(bd_url)
                valid_words.append('当前设置的百度ak【%s】无效' % bd_ak)
            return valid, '\n'.join(valid_words)
        except Exception as e:
            return False, '你好像断网了！,错误详情：\n%s' % e

    def read_config(self):
        '''读取配置，在创建配置界面时触发'''
        # if not os.path.exists(self.config_fp):
        #     self.create_config()

        config = configparser.ConfigParser()
        # windows 记事本保存时只支持带BOM格式，为了兼容用记事本编辑过的文件能被正确读取，
        # 最好把编码指定为 utf-8-sig
        config.read(self.config_fp, encoding="utf-8-sig")

        # 生成用户唯一标识
        try:
            uid = config.get('common', 'uid')
            if uid in [None, ""]:
                uid = uuid.uuid1()
            else:
                pass
            config.set('common', 'uid', str(uid))
            f = open("data/Config.ini", 'w', encoding='utf-8')
            config.write(f)
            f.close()
            print('userid is %s' % uid)
        except Exception as e:
            print('userid genning error', e)

        # try:

        current_st = config.get('common', 'storage')
        csv_fname = config.get('common', 'csv_fname')

        # 百度地图ak 列表
        ak = config.get('common', 'ak')

        # 启动限定的关键词列表
        key_words = config.get('common', 'keywords')
        self.lineEdit_keywords.setText(key_words)
        # 数据库信息
        db_host = config.get('db', 'db_host')
        db_name = config.get('db', 'db_name')
        db_user = config.get('db', 'db_user')
        db_passd = config.get('db', 'db_passd')
        tb_name = config.get('db', 'tb_name')
        # 读取区域信息
        prov = config.get('regions', 'prov')
        city = config.get('regions', 'city')
        district = config.get('regions', 'district')

        return {

            'regions': {'prov': prov, 'city': city, 'district': district},
            'ak': ak,
            'keywords': key_words.split(','),
            'storage': current_st,
            'csv_fname': csv_fname,
            'db_host': db_host,
            'db_name': db_name,
            'db_user': db_user,
            'db_passd': db_passd,
            'tb_name': tb_name
        }
        # except Exception as e:
        #     print('read config error', e)
        #     return None

    def write_config(self):
        '''将用户的配置修改保存下来'''

        if not os.path.exists(self.config_fp):
            self.create_config()
        config = configparser.ConfigParser()
        config.read(self.config_fp, encoding="utf-8-sig")

        # regions = self.LineEdit_regions.text()
        prov = self.comboBox_prov.currentText()
        city = self.comboBox_city.currentText()
        district = self.comboBox_district.currentText()
        config.set('regions', 'prov', prov)
        config.set('regions', 'city', city)
        config.set('regions', 'district', district)

        keywords = self.lineEdit_keywords.text()
        config.set('common', 'keywords', keywords)
        try:
            f = open("data/Config.ini", 'w', encoding='utf-8')
            config.write(f)
            f.close()

        except Exception as e:
            MyQMessageBox('温馨提示', '权限不足，保存失败！请以管理员身份运行此程序！%s' % e, '确定', '取消')
            if self.toolButton_search.text() == "停止":
                self.toolButton_search.setText('开始')

    def csv2excel(self):
        # 从云端拉取settings_json
        # self.write_config()
        config = self.read_config()

        csv_fname = config['csv_fname']
        self.c2e = CsvToExcel(csv_fname=csv_fname)
        self.c2e.progress_singal.connect(self.show_progress)
        self.c2e.start()

    def crawl_slot(self):
        prov = self.comboBox_prov.currentText()
        if prov != "请选择":
            self.write_config()
            config = self.read_config()
            print(config)
            bd_ak = config['ak']
            valid, valid_words = self.check_api_key(bd_ak=bd_ak)

            if not valid:
                MyQMessageBox('温馨提示', '%s' % valid_words, '确定', '取消')

            else:

                try:
                    os.remove('log.txt')
                except Exception as e:
                    print(e)

                if self.toolButton_search.text() == '启动':
                    if self.tabWidget.currentIndex() == 1:
                        self.tabWidget.setCurrentIndex(0)
                    self.log_browser.clear()
                    self.toolButton_search.setText('停止')
                    self.show_progress('开始获取数据……')
                    self.label_progress.setText('正在采集，请耐心等待...')
                    self.p = Process(target=scrapy_spider_run, args=(self.Q, config))
                    self.p.start()
                    self.log_thread.start()
                else:
                    self.toolButton_search.setText('启动')
                    self.p.terminate()
                    self.show_progress("您已终止了采集进程！")
                    self.log_thread.terminate()
        else:
            MyQMessageBox('温馨提示', '先指定一下目标城市吧', '确定', '取消')

    def getLogContent(self, pieceLog):
        self.log_browser.setHtml(pieceLog)
        if '结束' in self.log_browser.toPlainText():
            self.show_progress("采集完成!")
            self.toolButton_search.setText("启动")
        if "csv文件转换excel文件成功完成" in pieceLog:

            reply = MyQMessageBox('温馨提示', 'csv文件转excel文件成功完成!', '打开文件位置', '知道了')
            if reply == 16384:
                self.open_result_file_dir()
            else:
                pass

    def show_while_combox_change(self):
        if "csv" in self.ComboBox_storage.currentText():
            self.lineEdit_csv_name.setEnabled(True)
            self.lineEdit_csv_name.setText("pois_data.csv")
            self.groupBox_db.setChecked(False)
        elif "mysql" in self.ComboBox_storage.currentText():
            self.lineEdit_csv_name.setEnabled(False)
            self.groupBox_db.setChecked(True)

    def show_settings_frame(self):
        if self.frame_settings.isVisible():
            self.frame_settings.hide()
        else:
            self.frame_settings.show()

    def refresh_settings_json(self, settings_json):
        self.settings_json = settings_json
        self.check_update_version(is_start=True)

    def read_local_json(self, fp):
        print('当前所在目录：', os.getcwd())
        with open(fp, 'r', encoding='utf8')as f:
            _json = json.load(f)
            return _json

    def show_support_me(self):
        self.support_me_window.show()

    def closeEvent(self, QCloseEvent):
        reply = MyQMessageBox('温馨提示', '确定要退出吗？', '确定', '取消')
        if reply == 16384:
            QCloseEvent.accept()
        else:
            QCloseEvent.ignore()

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == 16777220 and self.toolButton_search.text() == "启动":
            print("你按下了回车键")
            self.crawl_slot()

    def messageBox_error_warn(self, error_str):
        QMessageBox.information(self, "错误警告", "%s" % error_str, QMessageBox.Yes)

    def show_progress(self, _str):
        if "done" in _str:
            self.label_progress.setVisible(False)
        else:
            self.label_progress.setVisible(True)
            self.label_progress.setText(_str)

    def show_html_progress(self, _str):
        self.label_html.setText(_str)

    def about(self):

        if "about_me_url" in self.settings_json.keys():
            reply = QMessageBox.information(self, "关于", "当前版本号：%s\n作者：夜雨微寒 \n需要访问作者的个人主页吗？" % CURRENT_VERSION,
                                            QMessageBox.No, QMessageBox.Yes)
            if reply == 16384:
                webbrowser.open(self.settings_json.get("about_me_url"))
            else:
                pass
        else:

            QMessageBox.information(self, "关于", "当前版本号：%s\n作者：gongli.xu " % CURRENT_VERSION,
                                    QMessageBox.Yes)

    def render_map_js(self):
        config = self.read_config()
        prov = self.comboBox_prov.currentText()
        city = self.comboBox_city.currentText()
        district = self.comboBox_district.currentText()
        csv_fname = config['csv_fname']
        regions = {'prov': prov, 'city': city, 'district': district}
        self.render_map = RenderMap(csv_fname=csv_fname, regions=regions)
        self.render_map.result_signal.connect(self.show_map)
        self.render_map.progress_signal.connect(self.show_progress)
        self.render_map.error_signal.connect(self.messageBox_error_warn)
        self.render_map.start()

    def check_update_version(self, is_start=False):

        latest_version = self.settings_json.get("latest_version")
        print(latest_version)
        released_url = self.settings_json.get("released_url")
        if latest_version > CURRENT_VERSION and released_url is not None:
            details = self.settings_json.get("details")
            self.show_progress('<a href="%s" style="color:#0000ff;"><b>发现新版本，去更新</b></a>' % released_url)

            reply = QMessageBox.information(self, "温馨提示", "发现新的版本，需要跳转到下载页面吗？" + "\n" + "更新内容：\n %s" % details,
                                            QMessageBox.No, QMessageBox.Yes)

            if reply == 16384:
                self.visit_latest_version_url(released_url)
        else:
            if not is_start:
                QMessageBox.information(self, "温馨提示", "已经是最新版本了哦！", QMessageBox.Yes)

    def help(self):
        if 'help_url' in self.settings_json.keys():
            help_url = self.settings_json.get("help_url")
        else:
            help_url = "https://mp.weixin.qq.com/mp/homepage?__biz=Mzg5NzIyODU3Mg==&hid=5&sn=66156a443cc3adfc7e0bd37c83e3d7a7&scene=18&uin=&key=&devicetype=Windows+10+x64&version=63010043&lang=zh_CN&ascene=7&fontgear=2"
        webbrowser.open(help_url)

    def released_doc(self):
        doc_url = self.settings_json.get("released_url")
        webbrowser.open(doc_url)

    def visit_latest_version_url(self, released_url):
        webbrowser.open(released_url)
        print(released_url)

    def change_tab(self):
        if self.tabWidget.currentIndex() == 0:
            pass
        elif self.tabWidget.currentIndex() == 1:
            self.render_map_js()

    def show_map(self, _str):
        self.show_progress(_str)
        self.web_engine_view.load((QUrl(QFileInfo(r".\html\template.html").absoluteFilePath())))
        # if "成功生成地图文件" in _str:
        #     self.frame_settings.hide()

    def open_result_file_dir(self):
        dir_path = os.path.join(os.getcwd(), 'result')
        if platform.system() == "Windows":
            os.system("start explorer %s" % dir_path)
        else:
            MyQMessageBox('温馨提示', '当前系统为：%s,不支持打开目标文件夹' % platform.system(), '确定', '取消')


def MyQMessageBox(title, text, button1, button2=None):
    messageBox = QMessageBox()
    messageBox.setWindowTitle(title)
    messageBox.setWindowIcon(QtGui.QIcon(':/icon/img/easypoi.png'))
    messageBox.setText(text)
    if button2:
        messageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        buttonY = messageBox.button(QMessageBox.Yes)
        buttonY.setText(button1)
        buttonN = messageBox.button(QMessageBox.No)
        buttonN.setText(button2)
    else:
        messageBox.setStandardButtons(QMessageBox.Yes)
        buttonY = messageBox.button(QMessageBox.Yes)
        buttonY.setText(button1)

    messageBox.exec_()
    if messageBox.clickedButton() == buttonY:
        return 16384
    else:
        return 0


def show_loading():
    # 创建QSplashScreen对象实例
    splash = QtWidgets.QSplashScreen(QtGui.QPixmap(":/icon/img/easypoi256.png"))
    # 设置画面中的文字的字体
    splash.setFont(QFont('Microsoft YaHei UI', 10))
    # 显示画面
    splash.show()
    # 显示信息
    # splash.showMessage("人文互联网\n一个有用有趣的公众号！", QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom, QtCore.Qt.yellow)
    splash.finish(MainWindow)


if __name__ == "__main__":
    import sys

    # freeze_support用于pyinstaller打包，否则打包后无法显示窗口
    freeze_support()
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MainWindow()
    with open("./themes/macos.qss", 'r', encoding='utf8') as f:
        style = f.read()
    MainWindow.setStyleSheet(style)
    # 显示启动加载页面
    show_loading()
    # 当主界面显示后销毁启动画面
    MainWindow.show()
    sys.exit(app.exec_())
