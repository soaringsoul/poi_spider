import requests

from PyQt5 import QtCore


class UpdateCheck(QtCore.QThread):
    result_signal = QtCore.pyqtSignal(dict)
    finished_signal = QtCore.pyqtSignal(str)
    error_signal = QtCore.pyqtSignal(str)

    def __init__(self, current_verison):
        super(UpdateCheck, self).__init__()
        self.current_version = current_verison

    def get_cloud_settings_json(self):
        url = "https://gitee.com/soaringsoul/program_cloud_settings/raw/master/easycharts_settings.json"
        resq = requests.get(url)
        return resq.json()

    def run(self):

        # 拉取云数据
        try:
            self.settings_json = self.get_cloud_settings_json()
            self.result_signal.emit(self.settings_json)
        except Exception as e:
            print("拉取云端数据失败")
        self.finished_signal.emit("done")