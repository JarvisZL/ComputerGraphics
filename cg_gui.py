#!/usr/bin/env python
# -*- coding:utf-8 -*-
import copy
import sys
import os
import time
from math import sqrt

import cg_algorithms as alg
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    qApp,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QStyleOptionGraphicsItem, QColorDialog, QInputDialog, QFileDialog)
from PyQt5.QtGui import QPainter, QMouseEvent, QColor, QIcon, QPen, QKeyEvent, QTransform
from PyQt5.QtCore import QRectF, QPoint, Qt


class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.color = QColor(0, 0, 0)
        self.pensize = 2
        self.painting = False # 多边形和曲线绘制过程中控制
        self.edgenum = 0 # 多边形和曲线绘制过程中控制

        self.editstatus = ''
        self.editoriginpoint = []
        self.rotate_angle = 30
        self.oldplist = []
        self.oldbdrect = []
        self.clip_item = None
        self.cpx_item = None


    # 开始绘制操作
    def start_draw_line(self, algorithm, item_id):
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_polygon(self, status, algorithm, item_id):
        self.status = status # 分为 'triangle', 'rectangle', 'otherpolygon'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_ellipse(self, item_id):
        self.status = 'ellipse'
        self.temp_id = item_id

    def start_draw_curve(self, algorithm, item_id):
        self.status = 'curve'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    # 绘制结束
    def finish_draw(self):
        self.status = ''
        self.painting = False
        self.edgenum = 0
        self.click_selection(self.temp_item)

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''
        # 取消鼠标追踪
        self.setMouseTracking(False)
        self.unsetCursor()
        self.releaseKeyboard()
        self.oldplist.clear()
        self.oldbdrect.clear()
        self.main_window.statusBar().showMessage('')

    def selection_changed(self, selectedItem):
        selected = selectedItem.text()
        self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        self.selected_id = selected
        self.item_dict[selected].selected = True
        self.item_dict[selected].update()  # 调用paint
        self.status = ''
        self.updateScene([self.sceneRect()])  # 调用paint

        # 选中后进入编辑阶段，开始追踪鼠标移动的位置，并将当前item设为选中的item
        self.setMouseTracking(True)
        self.grabKeyboard()
        self.temp_item = self.item_dict[selected]
        self.oldplist = copy.deepcopy(self.temp_item.p_list)
        self.oldbdrect = self.temp_item.boundingrect.copy()

    def click_selection(self, selecteditem):
        if selecteditem is None:
            return
        self.main_window.statusBar().showMessage('图元选择: %s' % selecteditem.id)
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        self.selected_id = selecteditem.id
        self.item_dict[selecteditem.id].selected = True
        self.item_dict[selecteditem.id].update()  # 调用paint
        self.status = ''
        self.updateScene([self.sceneRect()])  # 调用paint

        # 选中后进入编辑阶段，开始追踪鼠标移动的位置，并将当前item设为选中的item
        self.setMouseTracking(True)
        self.grabKeyboard()
        self.temp_item = self.item_dict[selecteditem.id]
        self.oldplist = copy.deepcopy(self.temp_item.p_list)
        self.oldbdrect = self.temp_item.boundingrect.copy()


    # 旋转操作
    def clockwise_rotate(self):
        if self.painting == True:
            self.main_window.statusBar().showMessage('请完成当前绘制')
        else:
            if self.selected_id != '':
                if self.temp_item.item_type == 'ellipse' and self.rotate_angle % 90 != 0:
                    self.main_window.statusBar().showMessage('椭圆图元只能旋转90°及其倍数, 当前角度: '+str(self.rotate_angle))
                    return
                self.main_window.statusBar().showMessage('顺时针旋转'+ str(self.rotate_angle) +'度')
                xc = round((self.temp_item.boundingrect[0] + self.temp_item.boundingrect[2])/2)
                yc = round((self.temp_item.boundingrect[1] + self.temp_item.boundingrect[3])/2)
                self.temp_item.p_list = alg.rotate(self.temp_item.p_list,xc,yc,self.rotate_angle)
                self.updateScene([self.sceneRect()])
            else:
                self.main_window.statusBar().showMessage('请选择你要旋转的图元')

    def anticlockwise_rotate(self):
        if self.painting == True:
            self.main_window.statusBar().showMessage('请完成当前绘制')
        else:
            if self.selected_id != '':
                if self.temp_item.item_type == 'ellipse' and self.rotate_angle % 90 != 0:
                    self.main_window.statusBar().showMessage('椭圆图元只能旋转90°及其倍数, 当前角度: '+str(self.rotate_angle))
                    return
                self.main_window.statusBar().showMessage('逆时针旋转'+ str(self.rotate_angle) +'度')
                xc = round((self.temp_item.boundingrect[0] + self.temp_item.boundingrect[2])/2)
                yc = round((self.temp_item.boundingrect[1] + self.temp_item.boundingrect[3])/2)
                self.temp_item.p_list = alg.rotate(self.temp_item.p_list,xc,yc,360 - self.rotate_angle)
                self.updateScene([self.sceneRect()])
            else:
                self.main_window.statusBar().showMessage('请选择你要旋转的图元')

    def set_rotate_angle(self):
        if self.painting == True:
            self.main_window.statusBar().showMessage('请完成当前绘制')
        else:
            self.clear_selection()
            text, ok = QInputDialog.getText(self, '请输入新的角度', '(0 <= angle <= 360)')
            if ok:
                if float(text) < 0 or float(text) > 360:
                    self.main_window.statusBar().showMessage('您的输入不符合要求')
                    return
                self.rotate_angle = float(text)
                self.main_window.statusBar().showMessage('设置的角度为: '+text)


    # 裁剪操作
    def start_clip(self, algorithm: str):
        self.status = 'clipitem'
        self.temp_algorithm = algorithm
        self.updateScene([self.sceneRect()])

    def do_clip(self):
        for eachitem in self.item_dict.values():
            if eachitem.item_type == 'line':
                x_min,y_min = self.clip_item.boundingrect[0], self.clip_item.boundingrect[1]
                x_max,y_max = self.clip_item.boundingrect[2], self.clip_item.boundingrect[3]
                tmplist = alg.clip(eachitem.p_list,x_min,y_min,x_max,y_max, self.temp_algorithm)
                if len(tmplist) != 0:
                    eachitem.p_list = tmplist

    def finish_clip(self):
        self.status = ''
        self.temp_algorithm = ''
        self.clip_item = None

    def delete_item(self):
        if self.selected_id != '':
            # 清空scene
            self.scene().removeItem(self.item_dict[self.selected_id])
            # 清空侧边栏listwidget
            items = self.list_widget.findItems(self.selected_id, Qt.MatchExactly)
            row = self.list_widget.row(items[0])
            self.list_widget.takeItem(row)
            # 清零选择
            oldselected_id = self.selected_id  # 先保存旧值
            self.list_widget.clearSelection()
            self.clear_selection()
            # 清楚canvas item_dict
            # 该语句必须在clear_selection之后，否则会访问被该语句删除的地方
            del self.item_dict[oldselected_id]

            self.main_window.statusBar().showMessage('删除图元： %s' % oldselected_id)
            self.updateScene([self.sceneRect()])
        else:
            self.main_window.statusBar().showMessage('请选择图元')

    def copy_item(self):
        if self.selected_id != '':
            item = self.item_dict[self.selected_id]
            self.cpx_item = MyItem('0', item.item_type, item.p_list, item.pen, item.algorithm, item.finish)
            self.main_window.statusBar().showMessage('复制图元： %s' % self.selected_id)
            self.updateScene([self.sceneRect()])
        else:
            self.main_window.statusBar().showMessage('请选择图元')

    def paste_item(self):
        if self.painting == False and self.cpx_item is not None:
            if self.cpx_item.id == '0':
                self.cpx_item.id = self.main_window.get_id()

            self.cpx_item.p_list = alg.translate(self.cpx_item.p_list, 10, 10)
            self.scene().addItem(self.cpx_item)
            self.item_dict[self.cpx_item.id] = self.cpx_item
            self.list_widget.addItem(self.cpx_item.id)

            self.main_window.statusBar().showMessage('粘贴图元： %s' % self.cpx_item.id)
            self.cpx_item = None
        else:
            self.main_window.statusBar().showMessage('没有复制或剪切的图元')
        self.updateScene([self.sceneRect()])



    def onlyonepoint(self):
        if len(self.temp_item.p_list) == 2:
            if self.temp_item.p_list[0][0] == self.temp_item.p_list[1][0] and self.temp_item.p_list[0][1] == self.temp_item.p_list[1][1]:
                return True
        return False

    # 鼠标事件
    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = round(pos.x())
        y = round(pos.y())
        if self.selected_id == '':
            if self.status == '':
                self.click_selection(self.scene().itemAt(pos.x(), pos.y(), QTransform()))
            elif self.status == 'clipitem':
                self.clip_item = MyItem('0', self.status, [[x, y], [x, y]], QPen(self.color, self.pensize))
                self.scene().addItem(self.clip_item)
            elif self.status == 'line':
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], QPen(self.color,self.pensize), self.temp_algorithm)
                self.scene().addItem(self.temp_item)
            elif self.status == 'triangle':
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], QPen(self.color,self.pensize), self.temp_algorithm,False)
                self.scene().addItem(self.temp_item)
            elif self.status == 'rectangle':
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y], [x, y], [x, y]], QPen(self.color,self.pensize), self.temp_algorithm)
                self.scene().addItem(self.temp_item)
            elif self.status == 'otherpolygon':
                if self.painting == False:
                    self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], QPen(self.color,self.pensize), self.temp_algorithm)
                    self.scene().addItem(self.temp_item)
                    self.edgenum = 1
                    self.painting = True
                else:
                    self.edgenum = self.edgenum + 1
                    self.temp_item.p_list.append([x, y])
            elif self.status == 'ellipse':
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], QPen(self.color,self.pensize))
                self.scene().addItem(self.temp_item)
            elif self.status == 'curve':
                if self.painting == False:
                    self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], QPen(self.color,self.pensize), self.temp_algorithm, False)
                    self.scene().addItem(self.temp_item)
                    self.edgenum = 1
                    self.painting = True
                else:
                    self.edgenum = self.edgenum + 1
                    self.temp_item.p_list.append([x, y])
        else:
            if self.onlyonepoint() == True:
                self.setCursor(Qt.SizeAllCursor)
                self.editstatus = 'Translate'
                self.editoriginpoint = [x, y]
            else:
                area = self.getPointArea(x, y)
                if area == 'Translate':
                    self.setCursor(Qt.SizeAllCursor)
                    self.editstatus = area
                    self.editoriginpoint = [x, y]
                elif area == 'Rotate':
                    self.setCursor(Qt.ClosedHandCursor)
                    self.editstatus = area
                    self.editoriginpoint = [x, y]
                elif area == 'Outer':
                    self.unsetCursor()
                    self.editstatus = ''
                    self.editoriginpoint.clear()
                    self.main_window.list_widget.clearSelection()
                    self.clear_selection()
                else:
                    self.setCursor(Qt.CrossCursor)
                    self.editstatus = area
                    self.editoriginpoint = [x, y]
        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = round(pos.x())
        y = round(pos.y())
        if self.selected_id == '':
            if self.status == 'clipitem':
                self.clip_item.p_list[1] = [x, y]
            elif self.status == 'line':
                self.temp_item.p_list[1] = [x, y]
            elif self.status == 'triangle':
                self.temp_item.p_list[1] = [x, y]
            elif self.status == 'rectangle':
                self.temp_item.p_list[1] = [self.temp_item.p_list[0][0], y]
                self.temp_item.p_list[2] = [x, y]
                self.temp_item.p_list[3] = [x, self.temp_item.p_list[0][1]]
            elif self.status == 'otherpolygon':
                self.temp_item.p_list[self.edgenum] = [x, y]
            elif self.status == 'ellipse':
                self.temp_item.p_list[1] = [x, y]
            elif self.status == 'curve':
                self.temp_item.p_list[self.edgenum] = [x, y]
        else:
            # 并未处在edit状态中
            if self.editstatus == '':
                if self.onlyonepoint() == True:
                    self.setCursor(Qt.SizeAllCursor)
                else:
                    area = self.getPointArea(x, y)
                    if area == 'Translate':
                        self.setCursor(Qt.SizeAllCursor)
                    elif area == 'Rotate':
                        self.setCursor(Qt.OpenHandCursor)
                    elif area == 'Scale1' or area == 'Scale8':
                        self.setCursor(Qt.SizeFDiagCursor)
                    elif area == 'Scale2' or area == 'Scale7':
                        self.setCursor(Qt.SizeVerCursor)
                    elif area == 'Scale3' or area == 'Scale6':
                        self.setCursor(Qt.SizeBDiagCursor)
                    elif area == 'Scale4' or area == 'Scale5':
                        self.setCursor(Qt.SizeHorCursor)
                    else:
                        self.unsetCursor()
            # 正在edit状态中
            else:
                if self.editstatus == 'Translate':
                    self.temp_item.p_list = alg.translate(self.temp_item.p_list, x - self.editoriginpoint[0],
                                                          y - self.editoriginpoint[1])
                    self.editoriginpoint[0] = x
                    self.editoriginpoint[1] = y
                elif self.editstatus == 'Rotate':
                    if self.temp_item.item_type == 'ellipse':
                        self.main_window.statusBar().showMessage('不能通过拖动来实现椭圆的旋转。')
                    else:
                        #以width的长度来标定旋转角度
                        xc = round((self.oldbdrect[0] + self.oldbdrect[2]) / 2)
                        yc = round((self.oldbdrect[1] + self.oldbdrect[3]) / 2)
                        angle_perlen = 180/(min(self.width() - 5 - xc,xc))
                        angle =  (x - xc) * angle_perlen
                        self.temp_item.p_list = alg.rotate(self.oldplist, xc, yc, round(angle))
                elif self.editstatus == 'Scale1':
                    xc,yc = self.oldbdrect[2], self.oldbdrect[3]
                    x = xc - 5 if xc - x < 5 else x
                    y = yc - 5 if yc - y < 5 else y
                    sx = (xc - x)/(xc - self.oldbdrect[0])
                    sy = (yc - y)/(yc - self.oldbdrect[1])
                    if ((self.temp_item.boundingrect[2] - self.temp_item.boundingrect[0] > 5 or sx >= 5/(xc - self.oldbdrect[0]))
                        and (self.temp_item.boundingrect[3] - self.temp_item.boundingrect[1] > 5 or sy >= 5/(yc - self.oldbdrect[1]))):
                        self.temp_item.p_list = alg.scaleforgui(self.oldplist, xc, yc,sx,sy)

                    # xc,yc = self.temp_item.boundingrect[2], self.temp_item.boundingrect[3]
                    # x = xc - 5 if xc - x < 5 else x
                    # y = yc - 5 if yc - y < 5 else y
                    # sx = (xc - x)/(xc - self.temp_item.boundingrect[0])
                    # sy = (yc - y)/(yc - self.temp_item.boundingrect[1])
                    # if ((self.temp_item.boundingrect[2] - self.temp_item.boundingrect[0] > 5 or sx >= 1)
                    #     and (self.temp_item.boundingrect[3] - self.temp_item.boundingrect[1] > 5 or sy >= 1)):
                    #     self.temp_item.p_list = alg.scaleforgui(self.temp_item.p_list, xc, yc,sx,sy)
                elif self.editstatus == 'Scale2':
                    xc = round((self.oldbdrect[0] + self.oldbdrect[2])/2)
                    yc = self.oldbdrect[3]
                    y = yc - 5 if yc - y < 5 else y
                    sy = (yc - y) / (yc - self.oldbdrect[1])
                    if self.temp_item.boundingrect[3] - self.temp_item.boundingrect[1] > 5 or sy >= 5/(yc - self.oldbdrect[1]):
                        self.temp_item.p_list = alg.scaleforgui(self.oldplist, xc, yc, 1, sy)
                elif self.editstatus == 'Scale3':
                    xc, yc = self.oldbdrect[0], self.oldbdrect[3]
                    x = xc + 5 if x - xc < 5 else x
                    y = yc - 5 if yc - y < 5 else y
                    sx = (xc - x) / (xc - self.oldbdrect[2])
                    sy = (yc - y) / (yc - self.oldbdrect[1])
                    if ((self.temp_item.boundingrect[2] - self.temp_item.boundingrect[0] > 5 or sx >= 5/(xc - self.oldbdrect[2]))
                            and (self.temp_item.boundingrect[3] - self.temp_item.boundingrect[1] > 5 or sy >= 5/(yc - self.oldbdrect[1]))):
                        self.temp_item.p_list = alg.scaleforgui(self.oldplist, xc, yc, sx, sy)
                elif self.editstatus == 'Scale4':
                    xc = self.oldbdrect[2]
                    yc = round((self.oldbdrect[1] + self.oldbdrect[3])/2)
                    x = xc - 5 if xc - x < 5 else x
                    sx = (xc - x) / (xc - self.oldbdrect[0])
                    if self.temp_item.boundingrect[2] - self.temp_item.boundingrect[0] > 5 or sx >= 5/(xc - self.oldbdrect[0]):
                        self.temp_item.p_list = alg.scaleforgui(self.oldplist, xc, yc, sx, 1)
                elif self.editstatus == 'Scale5':
                    xc = self.oldbdrect[0]
                    yc = round((self.oldbdrect[1] + self.oldbdrect[3]) / 2)
                    x = xc + 5 if x - xc < 5 else x
                    sx = (xc - x) / (xc - self.oldbdrect[2])
                    if self.temp_item.boundingrect[2] - self.temp_item.boundingrect[0] > 5 or sx >= 5/(xc - self.oldbdrect[2]):
                        self.temp_item.p_list = alg.scaleforgui(self.oldplist, xc, yc, sx, 1)
                elif self.editstatus == 'Scale6':
                    xc, yc = self.oldbdrect[2], self.oldbdrect[1]
                    x = xc - 5 if xc - x < 5 else x
                    y = yc + 5 if y - yc < 5 else y
                    sx = (xc - x) / (xc - self.oldbdrect[0])
                    sy = (yc - y) / (yc - self.oldbdrect[3])
                    if ((self.temp_item.boundingrect[2] - self.temp_item.boundingrect[0] > 5 or sx >= 5/(xc - self.oldbdrect[0]))
                            and (self.temp_item.boundingrect[3] - self.temp_item.boundingrect[1] > 5 or sy >= 5/(yc - self.oldbdrect[3]))):
                        self.temp_item.p_list = alg.scaleforgui(self.oldplist, xc, yc, sx, sy)
                elif self.editstatus == 'Scale7':
                    xc = round((self.oldbdrect[0]+ self.oldbdrect[2])/2)
                    yc = self.oldbdrect[1]
                    y = yc + 5 if y - yc < 5 else y
                    sy = (yc - y) / (yc - self.oldbdrect[3])
                    if self.temp_item.boundingrect[3] - self.temp_item.boundingrect[1] > 5 or sy >= 5/(yc - self.oldbdrect[3]):
                        self.temp_item.p_list = alg.scaleforgui(self.oldplist, xc, yc, 1, sy)
                elif self.editstatus == 'Scale8':
                    xc,yc = self.oldbdrect[0],self.oldbdrect[1]
                    x = xc + 5 if x - xc < 5 else x
                    y = yc + 5 if y - yc < 5 else y
                    sx = (xc - x) / (xc - self.oldbdrect[2])
                    sy = (yc - y) / (yc - self.oldbdrect[3])
                    if ((self.temp_item.boundingrect[2] - self.temp_item.boundingrect[0] > 5 or sx >= 5/(xc - self.oldbdrect[2]))
                            and (self.temp_item.boundingrect[3] - self.temp_item.boundingrect[1] > 5 or sy >= 5/(yc - self.oldbdrect[3]))):
                        self.temp_item.p_list = alg.scaleforgui(self.oldplist, xc, yc, sx, sy)
                else:
                    pass
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.selected_id == '':
            if self.status == 'clipitem':
                self.do_clip()
                self.scene().removeItem(self.clip_item)
                self.updateScene([self.sceneRect()])
                self.finish_clip()
            elif self.status == 'line':
                self.item_dict[self.temp_id] = self.temp_item
                self.list_widget.addItem(self.temp_id)
                self.finish_draw()
            elif self.status == 'triangle':
                self.temp_item.finish = True
                x0, y0 = self.temp_item.p_list[0]
                x1, y1 = self.temp_item.p_list[1]
                self.temp_item.p_list[0] = [x0, max(y0, y1)]
                self.temp_item.p_list[1] = [x1, max(y0, y1)]
                self.temp_item.p_list.append([round((x0 + x1) / 2), min(y0, y1)])
                self.item_dict[self.temp_id] = self.temp_item
                self.list_widget.addItem(self.temp_id)
                self.finish_draw()
            elif self.status == 'rectangle':
                self.item_dict[self.temp_id] = self.temp_item
                self.list_widget.addItem(self.temp_id)
                self.finish_draw()
            elif self.status == 'otherpolygon':
                if self.edgenum > 2:
                    xf, yf = self.temp_item.p_list[self.edgenum]
                    xb, yb = self.temp_item.p_list[0]
                    if (xf - xb) ** 2 + (yf - yb) ** 2 <= 25:
                        self.temp_item.p_list[self.edgenum] = [xb, yb]
                        self.updateScene([self.sceneRect()])
                        self.item_dict[self.temp_id] = self.temp_item
                        self.list_widget.addItem(self.temp_id)
                        self.finish_draw()
            elif self.status == 'ellipse':
                self.item_dict[self.temp_id] = self.temp_item
                self.list_widget.addItem(self.temp_id)
                self.finish_draw()
            elif self.status == 'curve':
                pass
        else:
            self.unsetCursor()
            self.editstatus = ''
            self.editoriginpoint.clear()
            #更新坐标点
            self.oldplist = copy.deepcopy(self.temp_item.p_list)
            self.oldbdrect = self.temp_item.boundingrect.copy()
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if self.selected_id == '':
            if self.status == 'curve':
                if self.painting == True:
                    self.temp_item.finish = True
                    self.item_dict[self.temp_id] = self.temp_item
                    self.list_widget.addItem(self.temp_id)
                    self.finish_draw()
                    self.updateScene([self.sceneRect()])


    def getPointArea(self, x: int, y: int) -> str:
        x_mid = round((self.temp_item.boundingrect[0] + self.temp_item.boundingrect[2])/2)
        y_mid = round((self.temp_item.boundingrect[1] + self.temp_item.boundingrect[3])/2)
        if self.temp_item.item_type == 'line' and abs(self.temp_item.p_list[0][0] - self.temp_item.p_list[1][0]) <= 3:
            # 垂直直线
            if abs(x - self.temp_item.boundingrect[0]) <= 3 and abs(y - self.temp_item.boundingrect[1]) <= 3:
                return 'Scale2'
            elif abs(x - self.temp_item.boundingrect[0]) <= 3 and abs(y - self.temp_item.boundingrect[3]) <= 3:
                return 'Scale7'
            elif abs(x - self.temp_item.boundingrect[0]) <= 3 and y > self.temp_item.boundingrect[1] and y <  self.temp_item.boundingrect[3]:
                return 'Translate'
            else:
                return 'Outer'
        elif self.temp_item.item_type == 'line' and abs(self.temp_item.p_list[0][1] - self.temp_item.p_list[1][1]) <= 3:
            #水平直线
            if abs(x - self.temp_item.boundingrect[0]) <= 3 and abs(y - self.temp_item.boundingrect[1]) <= 3:
                return 'Scale4'
            elif abs(x - self.temp_item.boundingrect[2]) <= 3 and abs(y - self.temp_item.boundingrect[3]) <= 3:
                return 'Scale5'
            elif abs(y - self.temp_item.boundingrect[1]) <= 3 and x > self.temp_item.boundingrect[0] and x <  self.temp_item.boundingrect[2]:
                return 'Translate'
            else:
                return 'Outer'
        else:
            if abs(x - self.temp_item.boundingrect[0]) <= 3 and abs(y - self.temp_item.boundingrect[1]) <= 3:
                return 'Scale1'
            elif abs(x - x_mid) <= 3 and abs(y - self.temp_item.boundingrect[1]) <= 3:
                return 'Scale2'
            elif abs(x - self.temp_item.boundingrect[2]) <= 3 and abs(y - self.temp_item.boundingrect[1]) <= 3:
                return 'Scale3'
            elif abs(x - self.temp_item.boundingrect[0]) <= 3 and abs(y - y_mid) <= 3:
                return 'Scale4'
            elif abs(x - self.temp_item.boundingrect[2]) <= 3 and abs(y - y_mid) <= 3:
                return 'Scale5'
            elif abs(x - self.temp_item.boundingrect[0]) <= 3 and abs(y - self.temp_item.boundingrect[3]) <= 3:
                return 'Scale6'
            elif abs(x - x_mid) <= 3 and abs(y - self.temp_item.boundingrect[3]) <= 3:
                return 'Scale7'
            elif abs(x - self.temp_item.boundingrect[2]) <= 3 and abs(y - self.temp_item.boundingrect[3]) <= 3:
                return 'Scale8'
            elif (self.temp_item.boundingrect[2] - self.temp_item.boundingrect[0] >= 25 and self.temp_item.boundingrect[3] - self.temp_item.boundingrect[1] >= 25
                    and sqrt((x - x_mid)**2 + (y - y_mid)**2) <= 10):
                return 'Rotate'
            elif (x > self.temp_item.boundingrect[0] and x < self.temp_item.boundingrect[2]
                    and y > self.temp_item.boundingrect[1]  and y < self.temp_item.boundingrect[3] ):
                return 'Translate'
            else:
                return 'Outer'



class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """

    def __init__(self, item_id: str, item_type: str, p_list: list, pen: QPen, algorithm: str = '', finish: bool = False,
                 parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'triangle','rectangle','ohtherpolygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param color: 画笔颜色
        :param finish: 标记曲线和三角形是否绘制完毕
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id  # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list  # 图元参数
        self.pen = pen  # 画笔颜色
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False
        self.finish = finish
        self.boundingrect = [] # 记录图元外接矩形的左上角和右下角坐标[x_min,y_min,x_max,y_max]


    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        if self.item_type == 'clipitem':
            painter.setPen(QPen(QColor(0,0,0), 2, Qt.DotLine))
            painter.drawRect(self.boundingRect())
        elif self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.setPen(self.pen)
                painter.drawPoint(*p)
            if self.selected:
                self.selectedDraw(painter)
        elif self.item_type == 'triangle':
            # 得到三角形外接矩形的两个顶点
            if self.finish == False:
                x0,y0 = self.p_list[0]
                x1,y1 = self.p_list[1]
                plist = []
                plist.append([x0, max(y0,y1)])
                plist.append([x1, max(y0,y1)])
                plist.append([round((x0+x1)/2), min(y0,y1)])
                item_pixels = alg.draw_polygon(plist,self.algorithm)
                for p in item_pixels:
                    painter.setPen(self.pen)
                    painter.drawPoint(*p)
                if self.selected:
                    self.selectedDraw(painter)
            else:
                item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
                for p in item_pixels:
                    painter.setPen(self.pen)
                    painter.drawPoint(*p)
                if self.selected:
                    self.selectedDraw(painter)
        elif self.item_type == 'rectangle':
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.setPen(self.pen)
                painter.drawPoint(*p)
            if self.selected:
                self.selectedDraw(painter)
        elif self.item_type == 'otherpolygon':
            item_pixels = alg.draw_multilines(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.setPen(self.pen)
                painter.drawPoint(*p)
            if self.selected:
                self.selectedDraw(painter)
        elif self.item_type == 'ellipse':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            plist = []
            plist.append([min(x0, x1), min(y0, y1)])
            plist.append([max(x0, x1), max(y0, y1)])
            item_pixels = alg.draw_ellipse(plist)
            for p in item_pixels:
                painter.setPen(self.pen)
                painter.drawPoint(*p)
            if self.selected:
                self.selectedDraw(painter)
        elif self.item_type == 'curve':
            if self.finish == False:
                item_pixels = alg.draw_multilines(self.p_list, 'DDA')
                for p in item_pixels:
                    painter.setPen(self.pen)
                    painter.drawPoint(*p)
            else:
                item_pixels = alg.draw_curve(self.p_list, self.algorithm)
                for p in item_pixels:
                    painter.setPen(self.pen)
                    painter.drawPoint(*p)
                if self.selected:
                    self.selectedDraw(painter)


    def selectedDraw(self, painter: QPainter):
        painter.setPen(QColor(255, 0, 0))
        #painter.drawRect(self.boundingRect())

        if self.item_type == 'line' and abs(self.p_list[0][0] - self.p_list[1][0]) <= 3:
            painter.drawRect(self.boundingRect())
        elif self.item_type == 'line' and abs(self.p_list[0][1] - self.p_list[1][1]) <= 3:
            painter.drawRect(self.boundingRect())
        else:
            self.boundingRect()
            x_mid = (self.boundingrect[0] + self.boundingrect[2]) / 2
            y_mid = (self.boundingrect[1] + self.boundingrect[3]) / 2
            #scale1
            painter.drawRect(QRectF(self.boundingrect[0] - 3, self.boundingrect[1] - 3, 6, 6))
            painter.drawLine(self.boundingrect[0] + 3,self.boundingrect[1], x_mid-  3, self.boundingrect[1])
            #scale2
            painter.drawRect(QRectF(x_mid - 3, self.boundingrect[1] - 3, 6, 6))
            painter.drawLine(x_mid + 3, self.boundingrect[1], self.boundingrect[2] - 3, self.boundingrect[1])
            #scale3
            painter.drawRect(QRectF(self.boundingrect[2] - 3, self.boundingrect[1] - 3, 6, 6))
            painter.drawLine(self.boundingrect[2], self.boundingrect[1] + 3, self.boundingrect[2], y_mid - 3)
            #scale4
            painter.drawRect(QRectF(self.boundingrect[0] - 3, y_mid - 3, 6, 6))
            painter.drawLine(self.boundingrect[2], y_mid + 3, self.boundingrect[2], self.boundingrect[3] - 3)
            #scale5
            painter.drawRect(QRectF(self.boundingrect[2] - 3, y_mid - 3, 6, 6))
            painter.drawLine(self.boundingrect[2] - 3, self.boundingrect[3], x_mid + 3, self.boundingrect[3])
            #scale6
            painter.drawRect(QRectF(self.boundingrect[0] - 3, self.boundingrect[3] - 3, 6, 6))
            painter.drawLine(x_mid - 3, self.boundingrect[3], self.boundingrect[0] + 3, self.boundingrect[3])
            #scale7
            painter.drawRect(QRectF(x_mid - 3, self.boundingrect[3] - 3, 6, 6))
            painter.drawLine(self.boundingrect[0], self.boundingrect[3] - 3, self.boundingrect[0], y_mid + 3)
            #scale8
            painter.drawRect(QRectF(self.boundingrect[2] - 3, self.boundingrect[3] - 3, 6, 6))
            painter.drawLine(self.boundingrect[0], y_mid - 3, self.boundingrect[0], self.boundingrect[1] + 3)


            #rotate center
            if self.boundingrect[2] - self.boundingrect[0] >= 25 and self.boundingrect[3] - self.boundingrect[1] >= 25 :
                painter.setPen(QPen(QColor(255, 0, 0), 2, Qt.DashLine))
                painter.drawEllipse(QPoint(x_mid,y_mid), 10,10)


        # x_mid = int((self.boundingrect[0] + self.boundingrect[2]) / 2)
        # if self.boundingrect[1] - 4 * self.rotationR < 0:
        #     painter.drawLine(QPoint(x_mid, self.boundingrect[3]),QPoint(x_mid, self.boundingrect[3] + 2 * self.rotationR))
        #     painter.setPen(QPen(QColor(255, 0, 0), 2, Qt.DashLine))
        #     painter.drawEllipse(QPoint(x_mid, self.boundingrect[3] + 3 * self.rotationR), self.rotationR, self.rotationR)
        #     self.rotationP = [x_mid, self.boundingrect[3] + 3 * self.rotationR]
        # else:
        #     painter.drawLine(QPoint(x_mid, self.boundingrect[1]), QPoint(x_mid, self.boundingrect[1] - 2 * self.rotationR))
        #     painter.setPen(QPen(QColor(255, 0, 0), 2, Qt.DashLine))
        #     painter.drawEllipse(QPoint(x_mid, self.boundingrect[1] - 3 * self.rotationR), self.rotationR, self.rotationR)
        #     self.rotationP = [x_mid, self.boundingrect[1] - 3 * self.rotationR]

    def boundingRect(self) -> QRectF:
        if self.item_type == 'clipitem':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            self.boundingrect = [x, y, max(x0, x1), max(y0, y1)]
            return QRectF(x, y, w, h)
        elif self.item_type == 'line':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            self.boundingrect = [x, y, max(x0, x1), max(y0, y1)]
            # if len(self.rotationcenter) == 0:
            #     x_mid = int((x + max(x0, x1))/2)
            #     y_mid = int((y + max(y0, y1))/2)
            #     self.rotationcenter.append([x_mid, y_mid])
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'triangle':
            x_min, y_min = self.p_list[0]
            x_max, y_max = self.p_list[0]
            for x, y in self.p_list:
                x_min = min(x_min, x)
                y_min = min(y_min, y)
                x_max = max(x_max, x)
                y_max = max(y_max, y)
            self.boundingrect = [x_min, y_min, x_max, y_max]
            # if len(self.rotationcenter) == 0:
            #     self.rotationcenter.append([int((x_min + x_max)/2),int((y_min+y_max)/2)])
            return QRectF(x_min - 1, y_min - 1, x_max - x_min + 2, y_max - y_min + 2)
        elif self.item_type == 'rectangle':
            x_min, y_min = self.p_list[0]
            x_max, y_max = self.p_list[0]
            for x, y in self.p_list:
                x_min = min(x_min, x)
                y_min = min(y_min, y)
                x_max = max(x_max, x)
                y_max = max(y_max, y)
            self.boundingrect = [x_min, y_min, x_max, y_max]
            # if len(self.rotationcenter) == 0:
            #     self.rotationcenter.append([int((x_min + x_max)/2),int((y_min+y_max)/2)])
            return QRectF(x_min - 1, y_min - 1, x_max - x_min + 2, y_max - y_min + 2)
        elif self.item_type == 'otherpolygon':
            x_min, y_min = self.p_list[0]
            x_max, y_max = self.p_list[0]
            for x,y in self.p_list:
                x_min = min(x_min, x)
                y_min = min(y_min, y)
                x_max = max(x_max, x)
                y_max = max(y_max, y)
            self.boundingrect = [x_min, y_min, x_max, y_max]
            # if len(self.rotationcenter) == 0:
            #     self.rotationcenter.append([int((x_min + x_max)/2),int((y_min+y_max)/2)])
            return QRectF(x_min - 1, y_min - 1, x_max - x_min + 2, y_max - y_min + 2)
        elif self.item_type == 'ellipse':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            self.boundingrect = [x, y, max(x0, x1), max(y0, y1)]
            # if len(self.rotationcenter) == 0:
            #     x_mid = int((x + max(x0, x1))/2)
            #     y_mid = int((y + max(y0, y1))/2)
            #     self.rotationcenter.append([x_mid, y_mid])
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'curve':
            x_min, y_min = self.p_list[0]
            x_max, y_max = self.p_list[0]
            for x, y in self.p_list:
                x_min = min(x_min, x)
                y_min = min(y_min, y)
                x_max = max(x_max, x)
                y_max = max(y_max, y)
            self.boundingrect = [x_min, y_min, x_max, y_max]
            # if len(self.rotationcenter) == 0:
            #     self.rotationcenter.append([int((x_min + x_max)/2),int((y_min+y_max)/2)])
            return QRectF(x_min - 1, y_min - 1, x_max - x_min + 2, y_max - y_min + 2)


class MainWindow(QMainWindow):
    """
    主窗口类
    """

    def __init__(self):
        super().__init__()
        self.item_cnt = 1

        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(150)

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 600, 600)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(605, 605)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget

        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        set_pen_act = file_menu.addAction('设置画笔颜色')
        set_pensize_act = file_menu.addAction('设置画笔粗细')
        reset_canvas_act = file_menu.addAction('重置画布')
        save_canvas_act = file_menu.addAction('保存画布')
        exit_act = file_menu.addAction('退出')

        draw_menu = menubar.addMenu('绘制')
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')

        polygon_menu = draw_menu.addMenu('多边形')
        triangle_menu = polygon_menu.addMenu('三角形')
        rectangle_menu = polygon_menu.addMenu('矩形')
        others_menu = polygon_menu.addMenu('自定义')
        triangle_dda_act = triangle_menu.addAction('DDA')
        triangle_bresenham_act = triangle_menu.addAction('Bresenham')
        rectangle_dda_act = rectangle_menu.addAction('DDA')
        rectangle_bresenham_act = rectangle_menu.addAction('Bresenham')
        otherpolygon_dda_act = others_menu.addAction('DDA')
        otherpolygon_bresenham_act = others_menu.addAction('Bresenham')

        ellipse_act = draw_menu.addAction('椭圆')
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')


        rotate_menu = menubar.addMenu('旋转')
        clockwise_act = rotate_menu.addAction('顺时针旋转')
        anticlockwise_act = rotate_menu.addAction('逆时针旋转')
        setangle_act = rotate_menu.addAction('设置旋转角度')

        clip_menu = menubar.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')

        edit_menu = menubar.addMenu('图元编辑')
        delete_item_act = edit_menu.addAction('删除图元')
        copy_item_act = edit_menu.addAction('复制图元')
        paste_item_act = edit_menu.addAction('粘贴图元')


        # 连接信号和槽函数
        # 文件目录
        set_pen_act.triggered.connect(self.set_pen_action)
        set_pensize_act.triggered.connect(self.set_pensize_action)
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        save_canvas_act.triggered.connect(self.save_canvas_action)
        exit_act.triggered.connect(qApp.quit)
        # 绘制目录 - 直线
        line_naive_act.triggered.connect(self.line_naive_action)
        line_dda_act.triggered.connect(self.line_dda_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)
        #绘制目录 - 多边形
        triangle_dda_act.triggered.connect(self.triangle_dda_action)
        triangle_bresenham_act.triggered.connect(self.triangle_bresenham_action)
        rectangle_dda_act.triggered.connect(self.rectangle_dda_action)
        rectangle_bresenham_act.triggered.connect(self.rectangle_bresenham_action)
        otherpolygon_dda_act.triggered.connect(self.otherpolygon_dda_action)
        otherpolygon_bresenham_act.triggered.connect(self.otherpolygon_bresenham_action)
        #绘制目录 - 椭圆
        ellipse_act.triggered.connect(self.ellipse_action)

        #绘制目录 - 曲线
        curve_bezier_act.triggered.connect(self.curve_bezier_actiton)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)

        #旋转目录
        clockwise_act.triggered.connect(self.clockwise_rotate)
        anticlockwise_act.triggered.connect(self.anticlockwise_rotate)
        setangle_act.triggered.connect(self.set_rotate_angle)

        #裁剪目录
        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)

        #选中操作
        self.list_widget.itemClicked.connect(self.canvas_widget.selection_changed)
        #self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)

        #图元编辑
        delete_item_act.triggered.connect(self.delete_item_action)
        copy_item_act.triggered.connect(self.copy_item_action)
        paste_item_act.triggered.connect(self.paste_item_action)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(600, 600)
        self.setWindowTitle('Enjoy Drawing')

    def get_id(self):
        _id = str(self.item_cnt)
        self.item_cnt += 1
        return _id

    # 文件目录操作
    def set_pen_action(self):
        if self.canvas_widget.painting == False:
            self.canvas_widget.clear_selection()#目的是为了取消keyboard的grab
            self.canvas_widget.color = QColorDialog.getColor()
            self.statusBar().showMessage('设置画笔颜色')
        else:
            self.statusBar().showMessage('请先完成当前绘制')

    def set_pensize_action(self):
        if self.canvas_widget.painting == False:
            self.canvas_widget.clear_selection()  # 目的是为了取消keyboard的grab
            size, ok = QInputDialog.getText(self,'请输入新的笔的粗细','1 <= size <= 10（默认为2)')
            if ok:
                if int(size) < 1 or int(size) > 10:
                    self.statusBar().showMessage('您输入的数值不符合要求')
                    return
                self.canvas_widget.pensize = int(size)
            self.statusBar().showMessage('设置画笔粗细')
        else:
            self.statusBar().showMessage('请先完成当前绘制')

    def reset_canvas_action(self):
        if self.canvas_widget.painting == False:
            self.canvas_widget.clear_selection()  # 目的是为了取消keyboard的grab
            text, ok = QInputDialog.getText(self, '请输入新的宽和高', '格式(100 <= width,height <=1000): width height')
            if ok:
                text = text.strip().split(' ')
                if len(text) != 2:
                    self.statusBar().showMessage('您的输入不符合要求')
                    return
                if int(text[0]) < 100 or int(text[0]) > 1000 or int(text[1]) < 100 or int(text[1]) > 1000 :
                    self.statusBar().showMessage('您的输入不符合要求')
                    return
                self.list_widget.itemClicked.disconnect(self.canvas_widget.selection_changed)
                self.list_widget.clear()  # clear之前必须解除槽函数和信号的connect
                self.item_cnt = 1

                self.scene = QGraphicsScene(self)
                self.scene.setSceneRect(0, 0, int(text[0]), int(text[1]))
                oldcavas = self.canvas_widget
                self.canvas_widget = MyCanvas(self.scene, self)
                self.canvas_widget.setFixedSize(int(text[0])+5, int(text[1])+5)
                self.canvas_widget.main_window = self
                self.canvas_widget.list_widget = self.list_widget

                self.hbox_layout.replaceWidget(oldcavas, self.canvas_widget)
                oldcavas.setParent(None)

                self.list_widget.itemClicked.connect(self.canvas_widget.selection_changed)
            self.statusBar().showMessage('重置画布')
        else:
            self.statusBar().showMessage('请先完成当前绘制')

    def save_canvas_action(self):
        if self.canvas_widget.painting == False:
            self.canvas_widget.clear_selection()  # 目的是为了取消keyboard的grab
            folderpath = os.getcwd()+"/GuiImg"
            folder = os.path.exists(folderpath)
            if not folder :
                os.makedirs(folderpath)
            filename,options = QFileDialog.getSaveFileName(self,"Save Image",folderpath+"/","PNG(*.png);;JPG(*.jpg);;BMP(*.bmp)")
            if filename != '':
                pixMap = self.canvas_widget.grab()
                pixMap.save(filename)
            self.statusBar().showMessage('保存图片: '+filename)
        else:
            self.statusBar().showMessage('请先完成当前绘制')

    # 绘制目录操作 - 直线
    def line_naive_action(self):
        if self.canvas_widget.painting == False :
            self.canvas_widget.start_draw_line('Naive', self.get_id())
            self.list_widget.clearSelection()
            self.canvas_widget.clear_selection()
            self.statusBar().showMessage('Naive算法绘制线段')
        else:
            self.statusBar().showMessage('请先完成当前绘制')

    def line_dda_action(self):
        if self.canvas_widget.painting == False:
            self.canvas_widget.start_draw_line('DDA', self.get_id())
            self.list_widget.clearSelection()
            self.canvas_widget.clear_selection()
            self.statusBar().showMessage('DDA算法绘制线段')
        else:
            self.statusBar().showMessage('请先完成当前绘制')

    def line_bresenham_action(self):
        if self.canvas_widget.painting == False :
            self.canvas_widget.start_draw_line('Bresenham', self.get_id())
            self.list_widget.clearSelection()
            self.canvas_widget.clear_selection()
            self.statusBar().showMessage('Bresenham算法绘制线段')
        else:
            self.statusBar().showMessage('请先完成当前绘制')

    # 绘制目录操作 - 多边形
    def triangle_dda_action(self):
        if self.canvas_widget.painting == False :
            self.canvas_widget.start_draw_polygon('triangle', 'DDA', self.get_id())
            self.list_widget.clearSelection()
            self.canvas_widget.clear_selection()
            self.statusBar().showMessage('DDA算法绘制三角形')
        else:
            self.statusBar().showMessage('请先完成当前绘制')

    def triangle_bresenham_action(self):
        if self.canvas_widget.painting == False :
            self.canvas_widget.start_draw_polygon('triangle', 'Bresenham', self.get_id())
            self.list_widget.clearSelection()
            self.canvas_widget.clear_selection()
            self.statusBar().showMessage('Bresenham算法绘制三角形')
        else:
            self.statusBar().showMessage('请先完成当前绘制')

    def rectangle_dda_action(self):
        if self.canvas_widget.painting == False :
            self.canvas_widget.start_draw_polygon('rectangle', 'DDA', self.get_id())
            self.list_widget.clearSelection()
            self.canvas_widget.clear_selection()
            self.statusBar().showMessage('DDA算法绘制矩形')
        else:
            self.statusBar().showMessage('请先完成当前绘制')

    def rectangle_bresenham_action(self):
        if self.canvas_widget.painting == False :
            self.canvas_widget.start_draw_polygon('rectangle', 'Bresenham', self.get_id())
            self.list_widget.clearSelection()
            self.canvas_widget.clear_selection()
            self.statusBar().showMessage('Bresenham算法绘制矩形')
        else:
            self.statusBar().showMessage('请先完成当前绘制')

    def otherpolygon_dda_action(self):
        if self.canvas_widget.painting == False :
            self.canvas_widget.start_draw_polygon('otherpolygon', 'DDA', self.get_id())
            self.list_widget.clearSelection()
            self.canvas_widget.clear_selection()
            self.statusBar().showMessage('DDA算法绘制自定义多边形')
        else:
            self.statusBar().showMessage('请先完成当前绘制')

    def otherpolygon_bresenham_action(self):
        if self.canvas_widget.painting == False:
            self.canvas_widget.start_draw_polygon('otherpolygon', 'Bresenham', self.get_id())
            self.list_widget.clearSelection()
            self.canvas_widget.clear_selection()
            self.statusBar().showMessage('Bresenham算法绘制自定义多边形')
        else:
            self.statusBar().showMessage('请先完成当前绘制')

    # 绘制目录操作 - 椭圆
    def ellipse_action(self):
        if self.canvas_widget.painting == False:
            self.canvas_widget.start_draw_ellipse(self.get_id())
            self.list_widget.clearSelection()
            self.canvas_widget.clear_selection()
            self.statusBar().showMessage('绘制椭圆')
        else:
            self.statusBar().showMessage('请先完成当前绘制')

    # 绘制目录操作 - 曲线
    def curve_bezier_actiton(self):
        if self.canvas_widget.painting == False :
            self.canvas_widget.start_draw_curve('Bezier',self.get_id())
            self.list_widget.clearSelection()
            self.canvas_widget.clear_selection()
            self.statusBar().showMessage('Bezier算法绘制曲线')
        else:
            self.statusBar().showMessage('请先完成当前绘制')

    def curve_b_spline_action(self):
        if self.canvas_widget.painting == False :
            self.canvas_widget.start_draw_curve('B-spline',self.get_id())
            self.list_widget.clearSelection()
            self.canvas_widget.clear_selection()
            self.statusBar().showMessage('B-spline算法绘制曲线')
        else:
            self.statusBar().showMessage('请先完成当前绘制')

    # 旋转操作
    def clockwise_rotate(self):
        self.canvas_widget.clockwise_rotate()

    def anticlockwise_rotate(self):
        self.canvas_widget.anticlockwise_rotate()

    def set_rotate_angle(self):
        self.canvas_widget.set_rotate_angle()

    #裁剪操作
    def clip_cohen_sutherland_action(self):
        if self.canvas_widget.painting == False :
            self.canvas_widget.start_clip('Cohen-Sutherland')
            self.list_widget.clearSelection()
            self.canvas_widget.clear_selection()
            self.statusBar().showMessage('cohen_sutherland算法裁剪线段')
        else:
            self.statusBar().showMessage('请先完成当前绘制')

    def clip_liang_barsky_action(self):
        if self.canvas_widget.painting == False :
            self.canvas_widget.start_clip('Liang-Barsky')
            self.list_widget.clearSelection()
            self.canvas_widget.clear_selection()
            self.statusBar().showMessage('liang_barsky算法裁剪线段')
        else:
            self.statusBar().showMessage('请先完成当前绘制')

    #编辑目录
    def delete_item_action(self):
        self.canvas_widget.delete_item()

    def copy_item_action(self):
        self.canvas_widget.copy_item()


    def paste_item_action(self):
        self.canvas_widget.paste_item()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('../Icon.png'))
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
