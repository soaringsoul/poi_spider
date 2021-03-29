import requests
import base64
from datetime import datetime
import uuid
import configparser


def read_uid(config_fp=None):
    config = configparser.ConfigParser()
    # windows 记事本保存时只支持带BOM格式，为了兼容用记事本编辑过的文件能被正确读取，
    # 最好把编码指定为 utf-8-sig
    try:
        config.read(config_fp, encoding="utf-8-sig")
        uid = config.get('common', 'uid')
    except Exception as e:
        print('getting uid error:', e)
        uid = uuid.uuid1()
    return uid


def get_cloud_data(filename="easypoi.txt"):
    url = "https://gitee.com/api/v5/repos/soaringsoul/" \
          "pc_buried_data/contents/%s?" \
          "access_token=74e0aafb2534adfc6e4429e4e6ee8711" % filename
    resq = requests.get(url)
    print(resq.status_code)
    _json = resq.json()

    content = _json['content']
    content = base64.b64decode(content).decode('utf8')

    _sha = _json['sha']
    print(content)
    print(_sha)

    return _json


def update(filename='easypoi.txt', content=r'test', sha=None):
    url = "https://gitee.com/api/v5/repos/soaringsoul/pc_buried_data/contents/%s" % filename
    dt = datetime.now()
    dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
    print(dt_str)
    content = bytes(content, encoding="utf8")
    data = {
        "access_token": "74e0aafb2534adfc6e4429e4e6ee8711",
        "content": base64.b64encode(content),
        "sha": sha,
        "message": "userid update at: %s" % dt_str}
    resq = requests.put(url, data=data)
    print(resq.status_code)


def upload_buried_data(config_op=None):
    # 读取本地用户标识
    uid = read_uid(config_op)
    cloud_data = get_cloud_data()
    print(cloud_data)


if __name__ == "__main__":
    upload_buried_data('../data/config.ini')

