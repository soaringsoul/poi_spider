

def get_area_coords(polygon):
    """
    :param polygon:多边形上经纬度列表，eg:[(127.23,39.12),(126.23,36.45)]
    :return:多边形外切矩形四个点的经纬度坐标信息元组，eg:(max_lng,min_lng,max_lat, min_lat)
    """
    # 边界上的坐标列表化
    lng_lst = [x[0] for x in polygon]
    lat_lst = [x[1] for x in polygon]

    # 将坐标进行处理，获得四个角落的坐标，构造一个矩形网络
    max_lng, min_lng = max(lng_lst), min(lng_lst)
    max_lat, min_lat = max(lat_lst), min(lat_lst)
    return max_lng, min_lng, max_lat, min_lat
