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
            # 保证x1 >= x0 方便后续操作
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            # 计算出k
            k = (y1 - y0) / (x1 - x0)
            if k <= 1 and k >= -1:
                # x变化更大，故以x增量为步长
                y = y0
                for x in range(x0, x1 + 1):
                    result.append([x,int(y+0.5)])
                    y = y + k
            elif k > 1:
                # y变化更大，故以y增量为步长
                x = x0
                for y in range(y0, y1 + 1):
                    result.append([int(x+0.5),y])
                    x = x + 1/k
            elif k < -1:
                # y变化更大，故以y增量为步长,且此时y1 < y0
                x = x1 #match the range
                for y in range(y1, y0 + 1):
                    result.append([int(x+0.5),y])
                    x = x + 1/k
    elif algorithm == 'Bresenham':
        # 根据斜率确定以x或者y的增量为步长，假设为x,由此可以确定当(xk,yk)确定后，
        # (x_{k+1},y_{k+1})情况有(xk+1,yk),(xk+1,yk+1)两种
        # 随后根据判别式来判断取哪一个值
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

# forGuI
def draw_multilines(p_list, algorithm):
    """ 用于GUI绘制多边形过程
    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(1, len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
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
    if x0 == x1 or y1 == y0:
        return draw_line(p_list, 'DDA')
    result = []
    assert x0 <= x1 and y0 <= y1
    rx = (x1 - x0)/2
    ry = (y1 - y0)/2
    xc, yc = (x1 + x0)/2, (y1 + y0)/2
    if(rx >= ry):
        x, y = 0, ry
        p1 = ry*ry - rx*rx*ry + rx*rx/4
        while 2*ry*ry*x < 2*rx*rx*y:
            # still in area one
            result.append([int(x + xc), int(y + yc)])
            if p1 < 0:
                x = x + 1
                p1 = p1 + 2*ry*ry*x + ry*ry
            else:
                x = x + 1
                y = y - 1
                p1 = p1 + 2*ry*ry*x - 2*rx*rx*y + ry*ry
        p2 = ry*ry*(x+1/2)*(x+1/2) + rx*rx*(y-1)*(y-1) - rx*rx*ry*ry
        while y > 0 :
            # area two
            result.append([int(x + xc), int(y + yc)])
            if p2 > 0:
                y = y - 1
                p2 = p2 - 2*rx*rx*y + rx*rx
            else:
                x = x + 1
                y = y - 1
                p2 = p2 + 2*ry*ry*x - 2*rx*rx*y + rx*rx
        result.append([int(x + xc), int(y + yc)]) # the last one (rx,0)
    else:
        x, y = rx, 0
        p1 = rx * rx - ry * ry * rx + ry * ry / 4
        while 2 * rx * rx * y < 2 * ry * ry * x:
            # still in area one
            result.append([int(x + xc), int(y + yc)])
            if p1 < 0:
                y = y + 1
                p1 = p1 + 2 * rx * rx * y + rx * rx
            else:
                y = y + 1
                x = x - 1
                p1 = p1 + 2 * rx * rx * y - 2 * ry * ry * x + rx * rx
        p2 = rx * rx * (y + 1 / 2) * (y + 1 / 2) + ry * ry * (x - 1) * (x - 1) - ry * ry * rx * rx
        while x > 0:
            # area two
            result.append([int(x + xc), int(y + yc)])
            if p2 > 0:
                x = x - 1
                p2 = p2 - 2 * ry * ry * x + ry * ry
            else:
                y = y + 1
                x = x - 1
                p2 = p2 + 2 * rx * rx * y - 2 * ry * ry * x + ry * ry
        result.append([int(x + xc), int(y + yc)])  # the last one (rx,0)


    # Symmetry
    tmp = result.copy()
    for p in tmp:
        xx, yy = p[0] - xc, p[1] - yc
        result.append([int(xx + xc), int(-yy + yc)])
        result.append([int(-xx + xc), int(-yy + yc)])
        result.append([int(-xx + xc), int(yy + yc)])

    return result



def get_bino_coe(k ,n):
    """ #C_n^k
    """
    C = {}
    for row in range(n+1):
        for col in range(k+1):
            C[row,col] = C.setdefault((row,col),0)
    for row in range(n+1):
        C[row,0] = 1
        for col in range(1,k+1):
            if col <= row:
                #C_n^k = C_{n-1}^{k-1} + C_{n-1}^k
                C[row,col] = C[row-1,col-1]+C[row-1,col]
    return C[n,k]
def get_curve_points_Bezier(t, points):
    """ #求每一个t对应的点
    :param t:基函数自变量
    :param points: 控制点
    :return 对应的像素点
    """
    x, y = 0,0
    n = len(points)
    #求P(t) = sum_{i = 0}^{n} binom_k^{n-1} * t^k *(1-t)^{n-1-k} * P_i
    for k in range(0, n):
        coefficient = get_bino_coe(k, n - 1)* (t**k) * ((1-t)**(n-1-k))
        x = x + points[k][0] * coefficient
        y = y + points[k][1] * coefficient
    return [int(x), int(y)]


def get_Ncoefficent(u,i,k,n):
    """ 求N系数
    :param i: u 所对应的下界下标(int(u))
    :param k: 3(3次4阶)
    :param n: 一共有n+1个控制点(0,1,...,n)
    :return N: N系数矩阵
    """
    # 最大需要计算N[n,k+1],根据递推式可知需要N[n+1,k],N[n+2,k-1],...,N[n+k,1]
    N = {}
    # 初始化最多n+k行k+1列,全部为0
    for row in range(n+k+1):
        for col in range(1,k+2):
            N[row,col] = N.setdefault((row,col),0)
    # N_{uInt,1}(u) = 1 其它为0
    N[i,1] = 1
    #递推求解, 因为每一列所需要的行数不同，所以这里由列数来作为外循环控制行数
    for col in range(2,k+2):
        # 当列数为col时，其最多需要算到N[(k+1-col)+n,col]
        for row in range(n+2+(k-col)):
            N[row, col] = ((u - row) / (col - 1)) * N[row, col - 1] + ((row + col - u) / (col - 1)) * N[row + 1, col - 1]

    return N

def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    if algorithm == 'Bezier':
        m = 1000 #所取的点数
        for i in range(0,m+1):
            result.append(get_curve_points_Bezier( float(i)/float(m), p_list ))
    elif algorithm == 'B-spline':
        k = 3 #三次均匀B样条 k = 3
        n = len(p_list) - 1 # 一共有n+1个控制点[0,...,n]
        # 参数点集 = [0,1,2,...,k + n, k + n + 1 ], 共n+k+2个
        u = k # u可取的区间为[k,n+1]
        ujump = 0.001 # 步长
        while u <= n + 1:
            uInt = int(u) # u对应的下标

            N = get_Ncoefficent(u, uInt, k, n)
            # sum_{i = 0}^{n} P_i N[i,k+1](u), 实际上最大的为N[n,k+1]
            x, y = 0, 0
            for index in range(n + 1):
                x = x + p_list[index][0] * N[index, k + 1]
                y = y + p_list[index][1] * N[index, k + 1]
            result.append([int(x), int(y)])
            u = u + ujump

    return result


def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    ret = []
    for x,y in p_list:
        ret.append([x + dx,y + dy])
    return ret

def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 逆时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    ret = []
    for x0,y0 in p_list:
        xx = x + (x0 - x) * math.cos(r / 180 * math.pi) - (y0 - y) * math.sin(r / 180 * math.pi)
        yy = y + (x0 - x) * math.sin(r / 180 * math.pi) + (y0 - y) * math.cos(r / 180 * math.pi)
        ret.append([int(xx),int(yy)])
    return ret

def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    ret = []
    for x0,y0 in p_list:
        xx = x0 * s + x * (1 - s)
        yy = y0 * s + y * (1 - s)
        ret.append([round(xx),round(yy)])
    return ret

# forGUI
def scaleforgui(p_list, x, y, sx, sy):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param sx: (float) x缩放倍数
    :param sy: (float) y缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    ret = []
    for x0,y0 in p_list:
        xx = x0 * sx + x * (1 - sx)
        yy = y0 * sy + y * (1 - sy)
        ret.append([round(xx),round(yy)])
    return ret

def Encode(point,x_min, y_min, x_max, y_max):
    LEFT,RIGHT,UP,BOTTOM = 1,2,4,8
    x,y = point[0],point[1]
    ret = 0
    if x < x_min:
        ret = ret | LEFT
    elif x > x_max:
        ret = ret | RIGHT
    if y < y_min:
        ret = ret | BOTTOM
    elif y > y_max:
        ret = ret | UP
    return ret

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
    result = []
    if algorithm == 'Cohen-Sutherland':
        LEFT, RIGHT, UP, BOTTOM = 1, 2, 4, 8
        code1 = Encode(p_list[0], x_min, y_min, x_max, y_max)
        code2 = Encode(p_list[1], x_min, y_min, x_max, y_max)
        x1,y1,x2,y2 = p_list[0][0],p_list[0][1],p_list[1][0],p_list[1][1]
        xx1,yy1,xx2,yy2 = x1,y1,x2,y2

        if code1 != 0 or code2 != 0 :
            if (code1 & code2) != 0:
                return result
            else:
                while(code1 != 0):
                    if (code1 & LEFT) != 0:
                        k = (y2 - y1) / (x2 - x1)
                        yy1 = y1 + k*(x_min - x1)
                        xx1 = x_min
                    elif (code1 & RIGHT) != 0:
                        k = (y2 - y1) / (x2 - x1)
                        yy1 = y1 + k * (x_max - x1)
                        xx1 = x_max
                    elif (code1 & UP) != 0:
                        if x1 == x2:
                            xx1 = x1
                        else:
                            k = (y2 - y1) / (x2 - x1)
                            xx1 = x1 + (y_max - y1) / k
                        yy1 = y_max
                    elif (code1 & BOTTOM) != 0:
                        if x1 == x2:
                            xx1 = x1
                        else:
                            k = (y2 - y1) / (x2 - x1)
                            xx1 = x1 + (y_min - y1) / k
                        yy1 = y_min
                    code1 = Encode([xx1,yy1], x_min, y_min, x_max, y_max)
                while(code2 != 0):
                    if (code2 & LEFT) != 0:
                        k = (y2 - y1) / (x2 - x1)
                        yy2 = y1 + k * (x_min - x1)
                        xx2 = x_min
                    elif (code2 & RIGHT) != 0:
                        k = (y2 - y1) / (x2 - x1)
                        yy2 = y1 + k * (x_max - x1)
                        xx2 = x_max
                    elif (code2 & UP) != 0:
                        if x1 == x2:
                            xx2 = x1
                        else:
                            k = (y2 - y1) / (x2 - x1)
                            xx2 = x1 + (y_max - y1) / k
                        yy2 = y_max
                    elif (code2 & BOTTOM) != 0:
                        if x1 == x2:
                            xx2 = x1
                        else:
                            k = (y2 - y1) / (x2 - x1)
                            xx2 = x1 + (y_min - y1) / k
                        yy2 = y_min
                    code2 = Encode([xx2, yy2], x_min, y_min, x_max, y_max)
        result.append([int(xx1),int(yy1)])
        result.append([int(xx2), int(yy2)])
        return result
    elif algorithm == 'Liang-Barsky':
        x1, y1, x2, y2 = p_list[0][0], p_list[0][1], p_list[1][0], p_list[1][1]
        dx = x2 - x1
        dy = y2 - y1
        p = [-dx, dx, -dy, dy]
        q = [x1 - x_min, x_max - x1, y1 - y_min, y_max - y1]
        u1,u2 = 0,1
        for i in range(4):
            if p[i] < 0:
                r = q[i] / p[i]
                u1 = max(u1, r)
            elif p[i] > 0:
                r = q[i] / p[i]
                u2 = min(u2, r)
            else:
                if q[i] < 0:
                    return []

        if u1 <= u2:
            xx1 = x1 + u1*(x2 - x1)
            yy1 = y1 + u1*(y2 - y1)
            xx2 = x1 + u2*(x2 - x1)
            yy2 = y1 + u2*(y2 - y1)
            result.append([int(xx1),int(yy1)])
            result.append([int(xx2),int(yy2)])
        return result


