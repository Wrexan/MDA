# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'window_main.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(120)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setMinimumSize(QtCore.QSize(0, 120))
        self.widget.setMaximumSize(QtCore.QSize(16777215, 120))
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.widget_3 = QtWidgets.QWidget(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_3.sizePolicy().hasHeightForWidth())
        self.widget_3.setSizePolicy(sizePolicy)
        self.widget_3.setObjectName("widget_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget_3)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.chb_search_strict = QtWidgets.QCheckBox(self.widget_3)
        self.chb_search_strict.setChecked(True)
        self.chb_search_strict.setObjectName("chb_search_strict")
        self.horizontalLayout_4.addWidget(self.chb_search_strict)
        self.chb_search_eng = QtWidgets.QCheckBox(self.widget_3)
        self.chb_search_eng.setChecked(True)
        self.chb_search_eng.setObjectName("chb_search_eng")
        self.horizontalLayout_4.addWidget(self.chb_search_eng)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.input_search = QtWidgets.QLineEdit(self.widget_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.input_search.sizePolicy().hasHeightForWidth())
        self.input_search.setSizePolicy(sizePolicy)
        self.input_search.setMinimumSize(QtCore.QSize(0, 30))
        self.input_search.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.input_search.setFont(font)
        self.input_search.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.input_search.setAutoFillBackground(False)
        self.input_search.setMaxLength(255)
        self.input_search.setAlignment(QtCore.Qt.AlignCenter)
        self.input_search.setObjectName("input_search")
        self.verticalLayout_3.addWidget(self.input_search)
        self.input_search.raise_()
        self.horizontalLayout.addWidget(self.widget_3)
        self.scroll_models = QtWidgets.QScrollArea(self.widget)
        self.scroll_models.setWidgetResizable(True)
        self.scroll_models.setObjectName("scroll_models")
        self.scroll_models_layout = QtWidgets.QWidget()
        self.scroll_models_layout.setGeometry(QtCore.QRect(0, 0, 500, 118))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.scroll_models_layout.setFont(font)
        self.scroll_models_layout.setObjectName("scroll_models_layout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.scroll_models_layout)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.scroll_models.setWidget(self.scroll_models_layout)
        self.horizontalLayout.addWidget(self.scroll_models)
        self.verticalLayout.addWidget(self.widget)
        self.widget_2 = QtWidgets.QWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(20)
        sizePolicy.setHeightForWidth(self.widget_2.sizePolicy().hasHeightForWidth())
        self.widget_2.setSizePolicy(sizePolicy)
        self.widget_2.setMinimumSize(QtCore.QSize(0, 20))
        self.widget_2.setMaximumSize(QtCore.QSize(16777215, 20))
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.widget_2)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(self.widget_2)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.verticalLayout.addWidget(self.widget_2)
        self.widget_4 = QtWidgets.QWidget(self.centralwidget)
        self.widget_4.setObjectName("widget_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_4)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(2)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.table_left = QtWidgets.QTableWidget(self.widget_4)
        self.table_left.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table_left.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.table_left.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_left.setAlternatingRowColors(False)
        self.table_left.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table_left.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_left.setGridStyle(QtCore.Qt.SolidLine)
        self.table_left.setColumnCount(3)
        self.table_left.setObjectName("table_left")
        self.table_left.setRowCount(0)
        self.table_left.horizontalHeader().setCascadingSectionResizes(False)
        self.table_left.horizontalHeader().setDefaultSectionSize(160)
        self.table_left.horizontalHeader().setMinimumSectionSize(20)
        self.table_left.horizontalHeader().setStretchLastSection(True)
        self.horizontalLayout_3.addWidget(self.table_left)
        self.table_right = QtWidgets.QTableWidget(self.widget_4)
        self.table_right.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.table_right.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.table_right.setAutoScrollMargin(16)
        self.table_right.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_right.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table_right.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_right.setColumnCount(8)
        self.table_right.setObjectName("table_right")
        self.table_right.setRowCount(0)
        self.table_right.horizontalHeader().setCascadingSectionResizes(False)
        self.table_right.horizontalHeader().setDefaultSectionSize(60)
        self.table_right.horizontalHeader().setMinimumSectionSize(20)
        self.table_right.horizontalHeader().setStretchLastSection(True)
        self.horizontalLayout_3.addWidget(self.table_right)
        self.verticalLayout.addWidget(self.widget_4)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.chb_search_strict.setText(_translate("MainWindow", "Строго"))
        self.chb_search_eng.setText(_translate("MainWindow", "Латиница"))
        self.label.setText(_translate("MainWindow", "Прайс"))
        self.label_2.setText(_translate("MainWindow", "Наличие"))
