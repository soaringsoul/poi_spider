from PyQt5 import QtCore
import pandas as pd


class CsvToExcel(QtCore.QThread):
    result_signal = QtCore.pyqtSignal(dict)
    finished_signal = QtCore.pyqtSignal(str)
    error_signal = QtCore.pyqtSignal(str)
    progress_singal = QtCore.pyqtSignal(str)

    def __init__(self, csv_fname):
        super(CsvToExcel, self).__init__()
        self.csv_fname = csv_fname

    def clean(self, df):
        # 去重
        df = df.drop_duplicates()
        # 区域筛选

        df = df[df['isin_region'] == "True"]
        df = df[df['isin_region'] != "isin_region"]
        return df

    def run(self) -> None:
        try:
            self.progress_singal.emit("开始读取csv文件……")
            df = pd.read_csv(r'./result/%s' % self.csv_fname, encoding='utf8')
            self.progress_singal.emit("读取成功，当前csv文件共有%s列%s行,正对数据进行必要的清洗！请耐心等待！" % (df.shape[1], df.shape[0]))
            df = self.clean(df)
            csv_fname = self.csv_fname.split(".csv")[0]
            df.to_excel(r"./result/%s.xlsx" % csv_fname, index=False)
            self.progress_singal.emit("csv文件转换excel文件成功完成！你现在可以到程序根目录下查看采集结果文件了！")
        except Exception as e:
            self.progress_singal.emit("转换失败！错误详情：\n%s" % e)
