#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math


def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Naive':
        if x0 == x1:
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
                result.append((x, int(y0 + k * (x - x0))))
    elif algorithm == 'DDA':
        if x0 == x1:
            if y0 > y1:
                y0, y1 = y1, y0
            x = x0
            y = y0
            dis = y1 - y0
            while dis >= 0:
                result.append([x,int(y+0.5)])
                y = y + 1
                dis = dis -1
        else: # k存在
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            if k <= 1 and k >= -1:
                y = y0
                for x in range(x0, x1 + 1):
                    result.append([x,int(y+0.5)])
                    y = y + k
            elif k > 1:
                x = x0
                for y in range(y0, y1 + 1):
                    result.append([int(x+0.5),y])
                    x = x + 1/k
            elif k < -1:
                x = x1 #match the range
                for y in range(y1, y0 + 1):
                    result.append([int(x+0.5),y])
                    x = x + 1/k
    elif algorithm == 'Bresenham':
        if x0 > x1:
            x0, y0, x1, y1 = x1, y1, x0, y0
        dx = x1 - x0
        dy = y1 - y0
        if dy >= 0 and dy <= dx:
            # 0<=k<=1
            y = y0
            p = 2*dy - dx
            for x in range(x0, x1 + 1):
                result.append([x, y])
                if p < 0:
                    p = p + 2*dy
                else:
                    p = p + 2*dy - 2*dx
                    y = y + 1
        elif dy <= 0 and -dy <= dx:
            # -1<=k<=0
            # need to add a minus before dy
            y = y0
            p = 2*(-dy)-dx
            for x in range(x0, x1 + 1):
                result.append([x, y])
                if p < 0:
                    p = p + 2*(-dy)
                else:
                    p = p + 2*(-dy) - 2*dx
                    y = y - 1
        elif dy >= 0 and dy > dx:
            # k > 1
            x = x0
            p = 2*dx - dy
            for y in range(y0, y1 + 1):
                result.append([x, y])
                if p < 0:
                    p = p + 2*dx
                else:
                    p = p + 2*dx - 2*dy
                    x = x + 1
        elif dy <= 0 and -dy > dx:
            # k < -1
            # need to add a minus before dy
            x = x1
            p = 2*dx - (-dy)
            for y in range(y1, y0 + 1):
                result.append([x, y])
                if p < 0:
                    p = p + 2*dx
                else:
                    p = p + 2*dx - 2*(-dy)
                    x = x - 1
    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result


def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    assert x0 <= x1 and y0 <= y1
    rx = (x1 - x0)/2
    ry = (y1 - y0)/2
    xc, yc = int((x1 + x0)/2), int((y1 + y0)/2)
    print(rx,ry,xc,yc)
    if(rx >= ry):
        x, y = 0, int(ry)
        p1 = ry*ry - rx*rx*ry + rx*rx/4
        while 2*ry*ry*x < 2*rx*rx*y:
            # still in area one
            result.append([x + xc, y + yc])
            if p1 < 0:
                x = x + 1
                p1 = p1 + 2*ry*ry*x + ry*ry
            else:
                x = x + 1
                y = y - 1
                p1 = p1 + 2*ry*ry*x - 2*rx*rx*y + ry*ry
        p2 = ry*ry*(x+1/2)*(x+1/2) + rx*rx*(y-1)*(y-1) - rx*rx*ry*ry
        while x != rx or y != 0:
            # area two
            result.append([x + xc, y + yc])
            if p2 > 0:
                y = y - 1
                p2 = p2 - 2*rx*rx*y + rx*rx
            else:
                x = x + 1
                y = y - 1
                p2 = p2 + 2*ry*ry*x - 2*rx*rx*y + rx*rx
        result.append([x + xc, y + yc]) # the last one (rx,0)
    else:
        x, y = int(rx), 0
        p1 = rx * rx - ry * ry * rx + ry * ry / 4
        while 2 * rx * rx * y < 2 * ry * ry * x:
            # still in area one
            result.append([x + xc, y + yc])
            if p1 < 0:
                y = y + 1
                p1 = p1 + 2 * rx * rx * y + rx * rx
            else:
                y = y + 1
                x = x - 1
                p1 = p1 + 2 * rx * rx * y - 2 * ry * ry * x + rx * rx
        p2 = rx * rx * (y + 1 / 2) * (y + 1 / 2) + ry * ry * (x - 1) * (x - 1) - ry * ry * rx * rx
        while y != ry or x != 0:
            # area two
            result.append([x + xc, y + yc])
            if p2 > 0:
                x = x - 1
                p2 = p2 - 2 * ry * ry * x + ry * ry
            else:
                y = y + 1
                x = x - 1
                p2 = p2 + 2 * rx * rx * y - 2 * ry * ry * x + ry * ry
        result.append([x + xc, y + yc])  # the last one (rx,0)

    # Symmetry
    tmp = result.copy()
    for p in tmp:
        xx, yy = p[0] - xc, p[1] - yc
        result.append([xx + xc, -yy + yc])
        result.append([-xx + xc, -yy + yc])
        result.append([-xx + xc, yy + yc])
    return result


def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    pass


def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    pass


def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    pass


def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    pass


def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    pass
