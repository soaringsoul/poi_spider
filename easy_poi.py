# encoding = utf-8
# =====================================================
#   Copyright (C) 2021 All rights reserved.
#   author   : gongzi.xu / 95168339@qq.com
#   date     : 2021/01/09
# =====================================================
from multiprocessing import Process, Manager, freeze_support

import os, json, time
import platform
import requests
import configparser
from PyQt5.QtGui import QFont
from PyQt5 import QtGui
from PyQt5.QtWidgets import *

from ui.ImageWindow import ImageWindow

from workers.log_thread import LogThread
from workers.update_check import UpdateCheck

from ui import images_rc
from multiprocessing import Process, Manager, freeze_support

from scrapy.crawler import CrawlerProcess
from poi_spider.spiders.web_api_spider import WebApiCrawler
from scrapy.utils.project import get_project_settings

from ui.Ui_main import Ui_MainWindow

from ImageWindow import ImageWindow
from PyQt5 import QtWidgets, QtCore

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

CURRENT_VERSION = 1.0
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

        self.config_fp = config_fp
        # 保存配置项时是否弹窗提示标识 ，若为保存按钮触发有弹窗，否则无弹窗
        # 
        # self.save_way = 1

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
        self.toolButton_supportme.clicked.connect(self.show_support_me)

        # self.toolButton_search.clicked.connect(lambda: self.crawl_slot(self.toolButton_search))
        self.toolButton_search.clicked.connect(self.crawl_slot)

        self.toolButton_help.clicked.connect(self.help)
        self.toolButton_update.clicked.connect(self.check_update_version)

        self.toolButton_save.clicked.connect(self.write_config)
        self.toolButton_hide.clicked.connect(self.show_settings_frame)
        self.toolButton_setting.clicked.connect(self.show_settings_frame)
        self.pushButton_open_filepath.clicked.connect(self.open_result_file_dir)

        # keywords实时显示在启动框
        # self.LineEdit_keywords.textChanged.connect(self.show_keywords)
        self.LineEdit_keywords.textChanged.connect(lambda x: self.lineEdit_search.setText(x))
        self.lineEdit_search.textChanged.connect(lambda x: self.LineEdit_keywords.setText(x))
        self.ComboBox_storage.currentTextChanged.connect(self.show_while_combox_change)

    def init_data(self):
        self.read_config()
        self.settings_json = self.read_local_json(fp=SETTINGS_JSON_PATH)
        # 从云端拉取settings_json
        self.update = UpdateCheck(current_verison=CURRENT_VERSION)
        self.update.result_signal.connect(self.refresh_settings_json)
        self.update.start()

    def check_api_key(self, gd_key, bd_ak):
        valid = False
        valid_words = []
        gd_url = "https://restapi.amap.com/v3/config/district?keywords=成都&subdistrict=0&key=%s" % gd_key
        bd_url = "http://api.map.baidu.com/place/v2/search?query=ATM机&tag=大学&region=成都&output=json&ak=%s" % bd_ak
        try:
            gd_res = requests.get(gd_url, timeout=3)
            bd_res = requests.get(bd_url, timeout=3)
            gd_status_code = gd_res.json()['infocode']
            bd_status_code = bd_res.json()['status']

            if gd_status_code == "10000" and bd_status_code == 0:
                valid = True
            if gd_status_code != "10000":
                valid_words.append('高德地图apikey:%s无效' % gd_key)
            if bd_status_code != 0:
                valid_words.append('百度地图ak：%s 无效' % bd_ak)

            return valid, '\n'.join(valid_words)
        except Exception as e:
            return False, '你好像断网了！,错误详情：\n%s' % e

    def read_config(self):
        '''读取配置，在创建配置界面时触发'''
        if not os.path.exists(self.config_fp):
            self.create_config()

        config = configparser.ConfigParser()
        # windows 记事本保存时只支持带BOM格式，为了兼容用记事本编辑过的文件能被正确读取，
        # 最好把编码指定为 utf-8-sig
        config.read(self.config_fp, encoding="utf-8-sig")
        try:
            storages = ['csv文件', 'mysql']
            self.ComboBox_storage.clear()
            self.ComboBox_storage.addItems(storages)

            # 存储方式
            current_st = config.get('common', 'storage')

            if current_st in storages:
                self.ComboBox_storage.setCurrentText(current_st)
            csv_fname = config.get('common', 'csv_fname')
            self.lineEdit_csv_name.setText(csv_fname)

            # 高德地图api key
            gd_key = config.get('common', 'gd_key')
            self.lineEdit_gd_key.setText(gd_key)
            # 百度地图ak 列表
            ak_list = config.get('common', 'ak_list')
            self.lineEdit_ak.setText(ak_list)
            # 启动限定的区域列表
            regions = config.get('common', 'regions')
            self.LineEdit_regions.setText(regions)
            # 启动限定的关键词列表
            key_words = config.get('common', 'keywords')
            self.LineEdit_keywords.setText(key_words)
            # 数据库信息
            db_host = config.get('db', 'db_host')
            self.LineEdit_db_host.setText(db_host)

            db_name = config.get('db', 'db_name')
            self.LineEdit_db_name.setText(db_name)

            db_user = config.get('db', 'db_user')
            self.LineEdit_db_user.setText(db_user)

            db_passd = config.get('db', 'db_passd')
            self.LineEdit_db_passd.setText(db_passd)

            tb_name = config.get('db', 'tb_name')
            self.lineEdit_tb_name.setText(tb_name)
            return {
                'gd_key': gd_key,
                'ak_list': ak_list.split(','),
                'regions': regions.split(','),
                'keywords': key_words.split(','),
                'storage': current_st,
                'csv_fname': csv_fname,

                'db_host': db_host,
                'db_name': db_name,
                'db_user': db_user,
                'db_passd': db_passd,
                'tb_name': tb_name
            }
        except Exception as e:
            print(e)
            return None

    def write_config(self):
        '''将用户的配置修改保存下来'''

        if not os.path.exists(self.config_fp):
            self.create_config()
        config = configparser.ConfigParser()
        config.read(self.config_fp, encoding="utf-8-sig")
        gd_key = self.lineEdit_gd_key.text()
        config.set('common', 'gd_key', gd_key)

        ak_list = self.lineEdit_ak.text()
        config.set('common', 'ak_list', ak_list)

        regions = self.LineEdit_regions.text()
        config.set('common', 'regions', regions)

        keywords = self.LineEdit_keywords.text()
        config.set('common', 'keywords', keywords)

        storage = self.ComboBox_storage.currentText()
        config.set('common', 'storage', storage)

        csv_fname = self.lineEdit_csv_name.text()
        config.set('common', 'csv_fname', csv_fname)

        # 数据库信息
        db_host = self.LineEdit_db_host.text()
        config.set('db', 'db_host', db_host)

        db_name = self.LineEdit_db_name.text()
        config.set('db', 'db_name', db_name)

        db_user = self.LineEdit_db_user.text()
        config.set('db', 'db_user', db_user)

        db_passd = self.LineEdit_db_passd.text()
        config.set('db', 'db_passd', db_passd)

        tb_name = self.lineEdit_tb_name.text()
        config.set('db', 'tb_name', tb_name)

        f = open("data/Config.ini", 'w', encoding='utf-8')
        config.write(f)
        f.close()
        if self.save_way == 1:
            QMessageBox.information(self, '温馨提示', '保存成功！')
        else:
            self.save_way = 1

    def crawl_slot(self):
        gd_key = self.lineEdit_gd_key.text()
        bd_ak = self.lineEdit_ak.text()
        valid, valid_words = self.check_api_key(gd_key, bd_ak)

        if not valid:
            MyQMessageBox('温馨提示', '%s' % valid_words, '确定', '取消')

        else:
            self.save_way = 0
            self.write_config()
            config = self.read_config()
            try:
                os.remove('log.txt')
            except Exception as e:
                print(e)

            if self.toolButton_search.text() == '启动':
                self.log_browser.clear()
                self.toolButton_search.setText('停止')
                self.label_progress.setText('正在采集，请耐心等待...')
                self.p = Process(target=scrapy_spider_run, args=(self.Q, config))
                self.p.start()
                self.log_thread.start()
            else:
                self.toolButton_search.setText('启动')
                self.p.terminate()
                self.show_progress("您已终止了采集进程！")
                self.log_thread.terminate()

    def getLogContent(self, pieceLog):
        self.log_browser.setText(pieceLog)
        if '结束' in self.log_browser.toPlainText():
            self.show_progress("采集完成!")
            self.toolButton_search.setText("启动")

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

    def check_update_version(self, is_start=False):

        latest_version = self.settings_json.get("latest_version")
        print(latest_version)
        released_url = self.settings_json.get("released_url")
        if latest_version > CURRENT_VERSION and released_url is not None:
            details = self.settings_json.get("details")

            reply = QMessageBox.information(self, "温馨提示", "发现新的版本，需要跳转到下载页面吗？" + "\n" + "更新内容：\n %s" % details,
                                            QMessageBox.No, QMessageBox.Yes)
            print(reply)
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

    def visit_latest_version_url(self, released_url):
        webbrowser.open(released_url)
        print(released_url)

    def change_tab(self):
        if self.tabWidget.currentIndex() == 0:
            pass
        elif self.tabWidget.currentIndex() == 1:
            pass

    def open_result_file_dir(self):
        dir_path = os.path.join(os.getcwd(), 'result')
        if platform.system() == "Windows":
            os.system("start explorer %s" % dir_path)
        else:
            MyQMessageBox('温馨提示', '当前系统为：%s,不支持打开目标文件夹' % platform.system(), '确定', '取消')


def MyQMessageBox(title, text, button1, button2=None):
    messageBox = QMessageBox()
    messageBox.setWindowTitle(title)
    messageBox.setWindowIcon(QtGui.QIcon(':/icon/img/charts.png'))
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
    with open("./themes/ui.qss", 'r', encoding='utf8') as f:
        style = f.read()
    MainWindow.setStyleSheet(style)
    # 显示启动加载页面
    show_loading()
    # 当主界面显示后销毁启动画面
    MainWindow.show()
    sys.exit(app.exec_())
