# -*- coding: utf-8 -*-
# Author: lizhenyang_2008@163.com
import math
import sys

lat = 'lat'
lon = 'lon'

EARTH_R = 6371000

def angle2radian(angle):
    return (1.0 * math.pi * angle) / 180


def haversine(theta):
    #theta = angle2radian(angle)
    return (1 - math.cos(theta)) * 1.0 / 2

def deltaLongtitude(point1, point2, distance, radius):
    # points are dictionary {lat: num, lon: num}
    hav_d_r = haversine(distance / radius)


    phi_1 = angle2radian(point1[lat])
    phi_2 = angle2radian(point2[lat])

    hav_phi_delta = haversine(phi_2 - phi_1)


    cos_phi_1 = math.cos(phi_1)
    cos_phi_2 = math.cos(phi_2)

    hav_lambda_delta = (hav_d_r - hav_phi_delta) / (cos_phi_1 * cos_phi_2)

    cos_lambda_delta = 1 - 2 * hav_lambda_delta

    delta_theta = math.acos(cos_lambda_delta)

    delta_angle = delta_theta * 180 / math.pi

    print('东：{},{}'.format(point1[lon] + delta_angle, point1[lat]))
    print('西：{},{}'.format(point1[lon] - delta_angle, point1[lat]))

    print('北：{},{}'.format(point1[lon], point1[lat] + delta_angle))
    print('南：{},{}'.format(point1[lon], point1[lat] - delta_angle))

    print('lngs=({} {})'.format(point1[lon] - delta_angle, point1[lon] + delta_angle))
    print('lats=({} {})'.format(point1[lat] - delta_angle, point1[lat] + delta_angle))
    # print(point1[lon] - delta_angle, point1[lat])
    return {lat: point1[lat], lon: point1[lon] + delta_angle }


if __name__ == '__main__':
    tmp = [float(sys.argv[1]), float(sys.argv[2])]
    distance = sys.argv[3] if len(sys.argv) == 4 else 5000 # meter
    distance = float(distance)
    print ('distance:', distance)

    print (tmp)
    point1 = {lon: tmp[0],lat: tmp[1]}
    point2 = point1


    deltaLongtitude(point1, point2, distance, EARTH_R)