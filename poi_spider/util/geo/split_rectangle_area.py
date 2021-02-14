from shapely.geometry import Polygon


def split_rectanle_area(poly):
    """
    :param poly:
    A------------B
    |            |
    H            F
    |            |
    D------------C
    :return:
    A------E------B
    |      |      |
    H------O------F
    |      |      |
    D------G------C
    """
    minx, miny, maxx, maxy = poly.bounds
    lat_lst = [miny, maxy]
    lng_lst = [minx, maxx]
    lat_lst.insert(1, (miny + maxy) / 2)
    lng_lst.insert(1, (maxx + minx) / 2)

    lat_lng_lst = [(lng, lat) for lng in lng_lst for lat in lat_lst]
    poly_1 = Polygon([lat_lng_lst[x] for x in [0, 1, 3, 4]])
    poly_2 = Polygon([lat_lng_lst[x] for x in [1, 2, 4, 5]])
    poly_3 = Polygon([lat_lng_lst[x] for x in [3, 4, 6, 7]])
    poly_4 = Polygon([lat_lng_lst[x] for x in [4, 5, 7, 8]])
    return poly_1, poly_2, poly_3, poly_4


if __name__ == "__main__":
    pass
