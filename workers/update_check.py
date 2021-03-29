import requests
import os

from PyQt5 import QtCore
from workers.bury_data import upload_buried_data

class UpdateCheck(QtCore.QThread):
    result_signal = QtCore.pyqtSignal(dict)
    finished_signal = QtCore.pyqtSignal(str)
    error_signal = QtCore.pyqtSignal(str)

    def __init__(self, current_verison):
        super(UpdateCheck, self).__init__()
        self.current_version = current_verison

    def get_cloud_settings_json(self):
        url = "https://gitee.com/soaringsoul/program_cloud_settings/raw/master/easypoi_settings.json"
        resq = requests.get(url)
        return resq.json()

    def run(self):

        # 拉取云数据
        try:
            self.settings_json = self.get_cloud_settings_json()
            self.result_signal.emit(self.settings_json)
            gitee_url = "https://soaringsoul.gitee.io/easypoi/"
            requests.get(gitee_url,timeout=3)
        except Exception as e:
            print("拉取云端数据失败:", e)
        self.finished_signal.emit("done")



        # print('当前的文件路径：',os.getcwd())
        # upload_buried_data(config_op=os.getcwd())

