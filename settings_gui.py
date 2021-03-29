import codecs
import configparser
import io
import shlex
import threading
import traceback

from PyQt5.QtCore import *
from PyQt5.QtGui import QColor

import os

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QWidget, QColorDialog

from ui.Ui_settings import Ui_Form


class SettingsGui(QWidget, Ui_Form):
    '''软件的设置界面'''
    config_fp = "./data/config.ini"

    def __init__(self, parent=None,suggested_fname=None):
        super(SettingsGui, self).__init__(parent)
        self.setupUi(self)
        self.suggested_fname=suggested_fname
        self.read_config()

        # 将 应用按钮 与 保存配置文件 关联
        self.pushButton_save.clicked.connect(self.write_config)
        # self.toolButton.clicked.connect(self.clickOnChoose)
        # self.reset.clicked.connect(self.clickOnReset)
        # self.submit.clicked.connect(self.clickOnSubmit)

    def read_config(self):
        '''读取配置，在创建配置界面时触发'''
        if not os.path.exists(self.config_fp):
            self.create_config()

        config = configparser.ConfigParser()
        # windows 记事本保存时只支持带BOM格式，为了兼容用记事本编辑过的文件能被正确读取，
        # 最好把编码指定为 utf-8-sig
        config.read(self.config_fp, encoding="utf-8-sig")
        try:
            storages = ['csv文件', 'mysql', 'sqlite']
            self.comboBox_storage.addItems(storages)
            # 存储方式
            current_st = config.get('common', 'storage')

            if current_st in storages:
                self.comboBox_storage.setCurrentText(current_st)
            self.lineEdit_csv_name.setText(self.suggested_fname)
            # 百度地图ak 列表
            ak = config.get('common', 'ak')
            self.lineEdit_ak.setText(ak)

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


        except Exception as e:
            print(e)
            return None

    def create_config(self):
        '''默认的配置'''
        config = configparser.ConfigParser()
        config.read(self.config_fp, encoding='utf8')
        for item in ['common', 'db']:
            if item not in config.sections():
                config.add_section(item)

        common_default = {
            'ak': '',
            'regions': '成都市',
            'keywords': '大学',
            'storage': 'csv'
        }
        db_default = {
            'db_host': 'localhost',
            'db_name': '',
            'db_user': '',
            'db_passd': '',
            'tb_name': 'pois'
        }
        for key in common_default.keys():
            config.set('common', key, common_default[key])
        for key in db_default.keys():
            config.set('db', key, db_default[key])

        curdir = os.getcwd()
        folderName = 'data'
        path = curdir + os.path.sep + folderName
        if not os.path.exists(path):
            os.makedirs(path)
        f = open(self.config_fp, 'w', encoding='utf-8')
        config.write(f)
        f.close()

    def write_config(self):
        '''将用户的配置修改保存下来'''
        if not os.path.exists(self.config_fp):
            self.create_config()
        config = configparser.ConfigParser()
        config.read(self.config_fp, encoding="utf-8-sig")

        ak = self.lineEdit_ak.text()
        config.set('common', 'ak', ak)

        storage = self.comboBox_storage.currentText()
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
        QMessageBox.information(self, '提示', '保存成功！')

    def clickOnChoose(self):
        '''通过文件对话框，确定文件保存路径'''
        absolute_path = QFileDialog.getExistingDirectory(self, '选择保存路径', '/')
        self.filePath.setText(absolute_path)

    def clickOnReset(self):
        '''点击重置按钮，触发'''
        self.groupcommon.setChecked(False)
        self.databaseType.setCurrentIndex(0)
        self.HostName.setText('')
        self.DatabaseName.setText('')
        self.userName.setText('')
        self.password.setText('')
        self.filePath.setText('新闻正文')
        self.groupUpdate.setChecked(False)
        self.checkBox.setChecked(False)
        self.spinBox.setValue(24)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = SettingsGui()
    # 采用 型号 和 槽的方式 , 将 日志 实时输出
    ui.show()
    # ui.create_config()

    sys.exit(app.exec_())
