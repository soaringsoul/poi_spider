# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from pandas import DataFrame
from sqlalchemy import create_engine


class BaidumapwebapispierPipeline(object):
    def process_item(self, item, spider):

        poly = item['poly']
        keys1 = ['name', 'province', 'city', 'area', 'address', 'telephone', 'uid', 'street_id', 'detail',
                 'detail_info', 'location']
        keys2 = ['detail_url', 'tag', 'type']
        keys3 = ['search_word', 'region']
        if item['results']:
            results = item['results']
            rows = []
            for result in results:

                row = []

                for key in keys1:
                    # d[key] = result.get(key)

                    row.append(result.get(key))

                for key in keys2:
                    detail_info = result.get('detail_info')
                    if detail_info is None:
                        row.append(None)
                    else:
                        row.append(detail_info.get(key))

                for key in keys3:
                    row.append(item[key])
                rows.append([str(x) for x in row])

            df = DataFrame(rows, columns=keys1 + keys2 + keys3)
            try:
                print_msg = '\n'.join(df['name'])
                spider.Q.put(print_msg)
                print(print_msg)
            except Exception as e:
                print(e)

            # region_pinyin = ''.join(lazy_pinyin(item['region']))

            # 判断点是否在指定poly区域内，使用到了shapely polygon.contains函数
            # try:
            #     df['isin_region'] = df['location'].apply(
            #         lambda x: poly.contains(Point(float(eval(x)['lng']), float(eval(x)['lat']))))
            # except Exception as e:
            #     logging.info('判断poi是否在目标区域内时出错', e)
            #     df['isin_region'] = 999
            if 'csv' in spider.storage:
                df.to_csv('./result/%s' % spider.settings.get('csv_fname'), encoding='utf8', mode="a+", index=False)
            elif 'mysql' in spider.storage:
                # mysql sqlalchemy引擎数据，不用修改，自动读取以上配置。
                engine = create_engine(
                    'mysql+pymysql://{user}:{passwd}@{host}:3306/{db_name}?charset=utf8'.format(
                        user=spider.settings.get('db_user'),
                        passwd=spider.settings.get('db_passd'),
                        host=spider.settings.get('db_host'),
                        db_name=spider.settings.get('db_name'),
                    ))
                tb_name = spider.settings.get('tb_name')
                df.to_sql(tb_name, engine, if_exists='append', index=False)
