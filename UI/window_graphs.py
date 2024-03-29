# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'window_graphs.ui'
#
# Created by: PyQt5 UI code generator 5.15.8
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1240, 700)
        Dialog.setMinimumSize(QtCore.QSize(1240, 700))
        Dialog.setMaximumSize(QtCore.QSize(1240, 700))
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_2 = QtWidgets.QFrame(Dialog)
        self.frame_2.setMaximumSize(QtCore.QSize(16777215, 38))
        self.frame_2.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout_2.setSpacing(2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(12)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.cb_year = QtWidgets.QComboBox(self.frame_2)
        self.cb_year.setMinimumSize(QtCore.QSize(120, 0))
        self.cb_year.setMaximumSize(QtCore.QSize(120, 28))
        self.cb_year.setBaseSize(QtCore.QSize(120, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.cb_year.setFont(font)
        self.cb_year.setMaxVisibleItems(12)
        self.cb_year.setObjectName("cb_year")
        self.horizontalLayout_3.addWidget(self.cb_year)
        self.cb_month = QtWidgets.QComboBox(self.frame_2)
        self.cb_month.setMinimumSize(QtCore.QSize(120, 0))
        self.cb_month.setMaximumSize(QtCore.QSize(120, 28))
        self.cb_month.setBaseSize(QtCore.QSize(120, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.cb_month.setFont(font)
        self.cb_month.setMaxVisibleItems(12)
        self.cb_month.setObjectName("cb_month")
        self.horizontalLayout_3.addWidget(self.cb_month)
        self.rb_year = QtWidgets.QRadioButton(self.frame_2)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rb_year.setFont(font)
        self.rb_year.setObjectName("rb_year")
        self.horizontalLayout_3.addWidget(self.rb_year)
        self.rb_month = QtWidgets.QRadioButton(self.frame_2)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rb_month.setFont(font)
        self.rb_month.setObjectName("rb_month")
        self.horizontalLayout_3.addWidget(self.rb_month)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.label = QtWidgets.QLabel(self.frame_2)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.cb_graph = QtWidgets.QComboBox(self.frame_2)
        self.cb_graph.setMinimumSize(QtCore.QSize(220, 0))
        self.cb_graph.setMaximumSize(QtCore.QSize(220, 28))
        self.cb_graph.setBaseSize(QtCore.QSize(220, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.cb_graph.setFont(font)
        self.cb_graph.setMaxVisibleItems(12)
        self.cb_graph.setObjectName("cb_graph")
        self.horizontalLayout_3.addWidget(self.cb_graph)
        self.frame = QtWidgets.QFrame(self.frame_2)
        self.frame.setMinimumSize(QtCore.QSize(160, 0))
        self.frame.setMaximumSize(QtCore.QSize(160, 16777215))
        self.frame.setObjectName("frame")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.cb_smooth = QtWidgets.QCheckBox(self.frame)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.cb_smooth.setFont(font)
        self.cb_smooth.setChecked(True)
        self.cb_smooth.setObjectName("cb_smooth")
        self.horizontalLayout_4.addWidget(self.cb_smooth)
        self.sb_min = QtWidgets.QSpinBox(self.frame)
        self.sb_min.setMinimumSize(QtCore.QSize(40, 0))
        self.sb_min.setMaximumSize(QtCore.QSize(40, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.sb_min.setFont(font)
        self.sb_min.setAlignment(QtCore.Qt.AlignCenter)
        self.sb_min.setMinimum(1)
        self.sb_min.setMaximum(5)
        self.sb_min.setProperty("value", 3)
        self.sb_min.setObjectName("sb_min")
        self.horizontalLayout_4.addWidget(self.sb_min)
        self.lbl_min = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lbl_min.setFont(font)
        self.lbl_min.setObjectName("lbl_min")
        self.horizontalLayout_4.addWidget(self.lbl_min)
        self.horizontalLayout_3.addWidget(self.frame)
        self.horizontalLayout_2.addLayout(self.horizontalLayout_3)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.verticalLayout.addWidget(self.frame_2)
        self.graph_frame = QtWidgets.QFrame(Dialog)
        self.graph_frame.setMinimumSize(QtCore.QSize(0, 0))
        self.graph_frame.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.graph_frame.setFrameShape(QtWidgets.QFrame.Panel)
        self.graph_frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.graph_frame.setObjectName("graph_frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.graph_frame)
        self.horizontalLayout.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.graph_layout = QtWidgets.QVBoxLayout()
        self.graph_layout.setObjectName("graph_layout")
        self.horizontalLayout.addLayout(self.graph_layout)
        self.verticalLayout.addWidget(self.graph_frame)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Статистика"))
        self.rb_year.setText(_translate("Dialog", "Год"))
        self.rb_month.setText(_translate("Dialog", "Месяц"))
        self.label.setText(_translate("Dialog", "Граф:"))
        self.cb_smooth.setText(_translate("Dialog", "Сгладить"))
        self.lbl_min.setText(_translate("Dialog", "Нижний порог"))
