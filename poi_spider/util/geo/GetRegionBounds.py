import logging
from poi_spider.util.geo.split_rectangle_area import split_rectanle_area
from poi_spider.spiders.PlaceApi import PlaceApiByBounds
from poi_spider.TailRecurseException import tail_call_optimized

from multiprocessing.dummy import Pool

MAX_TOTAL = 150


class SplitRectangularArea(object):
    def __init__(self, keyword, region_poly, ak,Q):
        self.keep_bounds_lst = []
        self.poly = region_poly
        self.keyword = keyword
        self.ak = ak
        self.Q=Q
        minx, miny, maxx, maxy = self.poly.bounds
        self.bounds = ','.join([str(x) for x in [miny, minx, maxy, maxx]])


        self.global_poly_lst = []

    def get_bounds_lst(self):
        # 首次分割
        poly_lst = split_rectanle_area(self.poly)
        params_tuple = poly_lst, self.keyword
        global_poly_lst = self.get_bounds_lst_iter(params_tuple)
        self.keep_bounds_lst = [self.poly_lst_convert2_bounds_lst(x) for x in global_poly_lst]
        return self.keep_bounds_lst

    def poly_lst_convert2_bounds_lst(self, poly):
        minx, miny, maxx, maxy = poly.bounds
        # 调整矩形分割精度, 后续再设置
        # 在原有分割矩形的基础上扩大10%
        deviation_x = (maxx - minx) * 0
        deviation_y = (maxy - miny) * 0
        bounds = ','.join(
            [str(x) for x in [miny - deviation_y, minx - deviation_x, maxy + deviation_y, maxx + deviation_x]])
        return bounds

    @tail_call_optimized
    def get_single_poly_bounds(self, params_tuple):
        """
        :param params_tuple: (poly, keyword)
        :return: [bounds1,bounds2, ……]
        """
        # bounds_lst默认为空列表
        poly, keyword = params_tuple
        minx, miny, maxx, maxy = poly.bounds
        # 调整矩形分割精度, 后续再设置
        # 在原有分割矩形的基础上扩大10%
        deviation_x = (maxx - minx) * 0.1
        deviation_y = (maxy - miny) * 0.1
        bounds = ','.join(
            [str(x) for x in [miny - deviation_y, minx - deviation_x, maxy + deviation_y, maxx + deviation_x]])
        url = "http://api.map.baidu.com/place/v2/search?output=json" \
              "&query={keyword}" \
              "&page_size=20" \
              "&scope=2" \
              "&bounds=%s" \
              "&ak={ak}" \
              "&page_num={page_num}" % bounds
        print('bounds:', bounds)
        data = PlaceApiByBounds(keyword=keyword, url=url, ak=self.ak).get_response()
        try:
            total = data['total']
            print("当前关键词下找到%s个兴趣点" % total)
            self.Q.put("当前关键词下找到%s个兴趣点" % total)
            if total >= MAX_TOTAL:
                self.Q.put('当前区域的兴趣点数量:%s，将再次对该区域进行分割' % total)
                print('当前区域的兴趣点数量:%s，>=150,将再次进行分割' % total)
                return False, poly, total
            elif total > 0 and total < MAX_TOTAL:
                self.global_poly_lst.append(poly)
                return True, poly, total
            else:
                print('当前区域的兴趣点数量:%s,不再分割' % bounds)
                return True, poly, total

        except Exception as e:
            logging.info(e)
            self.Q.put("出错了，错误详情：%s" % e)


    def get_polys_bounds(self, params_tuple):
        poly, keyword = params_tuple
        poly_lst = split_rectanle_area(poly)
        params_tuple_lst = []
        for poly2 in poly_lst:
            params_tuple = poly2, keyword
            params_tuple_lst.append(params_tuple)
        p = Pool(processes=12)
        p.map(self.get_single_poly_bounds, params_tuple_lst)
        print('当前bounds_lst数量：%s' % len(self.keep_bounds_lst))

    @tail_call_optimized
    def get_bounds_lst_iter(self, params_tuple):
        poly_lst, keyword = params_tuple
        new_poly_lst = []
        poly_lst_iter = []
        # 将列表中的poly分割，一个变4个
        for poly in poly_lst:
            tmp_lst = split_rectanle_area(poly)
            poly_lst_iter.extend(tmp_lst)
        # 定义传入的参数列表
        params_tuple_lst = []
        for poly2 in poly_lst_iter:
            params_tuple = poly2, keyword
            params_tuple_lst.append(params_tuple)
        # 使用多线程
        p = Pool(processes=len(poly_lst_iter))
        results = p.map(self.get_single_poly_bounds, params_tuple_lst)
        for result in results:
            # check==false 不用再分割，total表示兴趣点数量
            check, poly, total = result
            # 若poly区域内兴趣点小于150个
            if check and total > 0:
                self.global_poly_lst.append(poly)
            # 若大于150个，加入新列表中准备递归分割
            elif not check and total >= MAX_TOTAL:
                new_poly_lst.append(poly)
        print('当前global_poly_list数量：%s' % len(self.global_poly_lst))
        if new_poly_lst:
            # 开始递归分割
            new_params_tuple = (new_poly_lst, keyword)
            return self.get_bounds_lst_iter(new_params_tuple)
        else:
            return self.global_poly_lst


if __name__ == "__main__":
    region = '温江区'
    from district import get_region_polyline

    poly = get_region_polyline(region, gd_key="531087dfde1430ebe715db1176657dfd")
    obj = SplitRectangularArea('商场', poly, ak='dASz7ubuSpHidP1oQWKuAK3q')
    bounds = obj.get_bounds_lst()
