#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
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
from PyQt5.QtGui import QPainter, QMouseEvent, QColor, QIcon
from PyQt5.QtCore import QRectF, QRect


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
        self.polypainting = False
        self.polyedgenum = 0

    # 开始绘制操作
    def start_draw_line(self, algorithm, item_id):
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_polygon(self, status, algorithm, item_id):
        self.status = status # 分为 'triangle', 'rectangle', 'otherpolygon'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    # 绘制结束
    def finish_draw(self):
        self.temp_id = self.main_window.get_id()
        self.polypainting = False

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''

    def selection_changed(self, selected):
        self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        self.selected_id = selected
        self.item_dict[selected].selected = True
        self.item_dict[selected].update()  # 调用paint
        self.status = ''
        self.updateScene([self.sceneRect()])  # 调用paint

    # 鼠标事件
    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.color, self.temp_algorithm)
            self.scene().addItem(self.temp_item)
        elif self.status == 'triangle':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.color, self.temp_algorithm)
            self.scene().addItem(self.temp_item)
        elif self.status == 'rectangle':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.color, self.temp_algorithm)
            self.scene().addItem(self.temp_item)
        elif self.status == 'otherpolygon':
            if self.polypainting == False:
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.color, self.temp_algorithm)
                self.scene().addItem(self.temp_item)
                self.polyedgenum = 1
                self.polypainting = True
            else:
                self.polyedgenum = self.polyedgenum + 1
                self.temp_item.p_list.append([x, y])
        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'triangle':
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'rectangle':
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'otherpolygon':
            self.temp_item.p_list[self.polyedgenum] = [x, y]
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.status == 'line':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'triangle':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'rectangle':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'otherpolygon':
            xf, yf = self.temp_item.p_list[self.polyedgenum]
            xb, yb = self.temp_item.p_list[0]
            if (xf - xb) ** 2 + (yf - yb) ** 2 <= 25:
                self.temp_item.p_list[self.polyedgenum] = [xb, yb]
                self.updateScene([self.sceneRect()])
                self.item_dict[self.temp_id] = self.temp_item
                self.list_widget.addItem(self.temp_id)
                self.finish_draw()

        super().mouseReleaseEvent(event)


    def resetcanvas(self):
        self.item_dict.clear()
        self.selected_id = ''
        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        for item in self.scene().items():
            self.scene().removeItem(item)


class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """

    def __init__(self, item_id: str, item_type: str, p_list: list, color: QColor, algorithm: str = '',
                 parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'triangle','rectangle','ohtherpolygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param color: 画笔颜色
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id  # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list  # 图元参数
        self.color = color  # 画笔颜色
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.setPen(self.color)
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'triangle':
            # 得到三角形外接矩形的两个顶点
            x0,y0 = self.p_list[0]
            x1,y1 = self.p_list[1]
            plist = []
            plist.append([x0, max(y0,y1)])
            plist.append([x1, max(y0,y1)])
            plist.append([int((x0+x1)/2), min(y0,y1)])
            item_pixels = alg.draw_polygon(plist,self.algorithm)
            for p in item_pixels:
                painter.setPen(self.color)
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'rectangle':
            x0,y0 = self.p_list[0]
            x1,y1 = self.p_list[1]
            plist = []
            plist.append(self.p_list[0])
            plist.append([x0, y1])
            plist.append(self.p_list[1])
            plist.append([x1, y0])
            item_pixels = alg.draw_polygon(plist, self.algorithm)
            for p in item_pixels:
                painter.setPen(self.color)
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'otherpolygon':
            item_pixels = alg.draw_multilines(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.setPen(self.color)
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'ellipse':
            pass
        elif self.item_type == 'curve':
            pass

    def boundingRect(self) -> QRectF:
        if self.item_type == 'line':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'triangle':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'rectangle':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'otherpolygon':
            x_min, y_min = self.p_list[0]
            x_max, y_max = self.p_list[0]
            for x,y in self.p_list:
                x_min = min(x_min, x)
                y_min = min(y_min, y)
                x_max = max(x_max, x)
                y_max = max(y_max, y)
            return QRectF(x_min - 1, y_min - 1, x_max - x_min + 2, y_max - y_min + 2)
        elif self.item_type == 'ellipse':
            pass
        elif self.item_type == 'curve':
            pass


class MainWindow(QMainWindow):
    """
    主窗口类
    """

    def __init__(self):
        super().__init__()
        self.item_cnt = 1

        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

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
        set_pen_act = file_menu.addAction('设置画笔')
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

        edit_menu = menubar.addMenu('编辑')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        clip_menu = edit_menu.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')

        # 连接信号和槽函数
        # 文件目录
        set_pen_act.triggered.connect(self.set_pen_action)
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

        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(600, 600)
        self.setWindowTitle('Just Drawing')

    def get_id(self):
        _id = str(self.item_cnt)
        self.item_cnt += 1
        return _id

    # 文件目录操作
    def set_pen_action(self):
        self.canvas_widget.color = QColorDialog.getColor()
        self.statusBar().showMessage('设置画笔颜色')

    def reset_canvas_action(self):
        self.list_widget.clear()
        self.item_cnt = 0
        text, ok = QInputDialog.getText(self, '请输入新的宽和高', '格式(100 <= width,height <=1000): width height')
        if ok:
            text = text.strip().split(' ')
            self.canvas_widget.setFixedSize(int(text[0])+5, int(text[1])+5)
            self.scene.setSceneRect(0, 0, int(text[0]), int(text[1]))
        self.canvas_widget.resetcanvas()
        self.statusBar().showMessage('重置画布')

    def save_canvas_action(self):
        filename,options = QFileDialog.getSaveFileName(self,"Save Image",os.getcwd()+"/GuiImg/","Images (*.png *.jpg *.bmp)")
        if filename != '':
            pixMap = self.canvas_widget.grab()
            pixMap.save(filename)
        self.statusBar().showMessage('保存图片: '+filename)

    # 绘制目录操作 - 直线
    def line_naive_action(self):
        self.canvas_widget.start_draw_line('Naive', self.get_id())
        self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_dda_action(self):
        self.canvas_widget.start_draw_line('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_bresenham_action(self):
        self.canvas_widget.start_draw_line('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    # 绘制目录操作 - 多边形
    def triangle_dda_action(self):
        self.canvas_widget.start_draw_polygon('triangle', 'DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制三角形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def triangle_bresenham_action(self):
        self.canvas_widget.start_draw_polygon('triangle', 'Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制三角形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def rectangle_dda_action(self):
        self.canvas_widget.start_draw_polygon('rectangle', 'DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制矩形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def rectangle_bresenham_action(self):
        self.canvas_widget.start_draw_polygon('rectangle', 'Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制矩形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def otherpolygon_dda_action(self):
        self.canvas_widget.start_draw_polygon('otherpolygon', 'DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制自定义多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def otherpolygon_bresenham_action(self):
        self.canvas_widget.start_draw_polygon('otherpolygon', 'Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制自定义多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('./paint.png'))
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
