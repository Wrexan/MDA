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
        MainWindow.resize(1280, 700)
        MainWindow.setWindowTitle("MDA")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("MDA.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setIconSize(QtCore.QSize(64, 64))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.HEAD = QtWidgets.QWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.HEAD.sizePolicy().hasHeightForWidth())
        self.HEAD.setSizePolicy(sizePolicy)
        self.HEAD.setMinimumSize(QtCore.QSize(0, 164))
        self.HEAD.setMaximumSize(QtCore.QSize(16777215, 164))
        self.HEAD.setObjectName("HEAD")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.HEAD)
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_8.setSpacing(2)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.widget_3 = QtWidgets.QWidget(self.HEAD)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_3.sizePolicy().hasHeightForWidth())
        self.widget_3.setSizePolicy(sizePolicy)
        self.widget_3.setObjectName("widget_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget_3)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.frame = QtWidgets.QFrame(self.widget_3)
        self.frame.setMinimumSize(QtCore.QSize(0, 86))
        self.frame.setObjectName("frame")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_5.setContentsMargins(4, 0, 4, 0)
        self.horizontalLayout_5.setSpacing(2)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.frame_7 = QtWidgets.QFrame(self.frame)
        self.frame_7.setMinimumSize(QtCore.QSize(100, 0))
        self.frame_7.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_7.setObjectName("frame_7")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_7)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frame_8 = QtWidgets.QFrame(self.frame_7)
        self.frame_8.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_8.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_8.setObjectName("frame_8")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.frame_8)
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.help = QtWidgets.QPushButton(self.frame_8)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.help.sizePolicy().hasHeightForWidth())
        self.help.setSizePolicy(sizePolicy)
        self.help.setMinimumSize(QtCore.QSize(116, 0))
        self.help.setMaximumSize(QtCore.QSize(116, 16777215))
        self.help.setObjectName("help")
        self.horizontalLayout_7.addWidget(self.help)
        self.settings_button = QtWidgets.QPushButton(self.frame_8)
        self.settings_button.setMinimumSize(QtCore.QSize(116, 0))
        self.settings_button.setMaximumSize(QtCore.QSize(116, 16777215))
        self.settings_button.setObjectName("settings_button")
        self.horizontalLayout_7.addWidget(self.settings_button)
        self.verticalLayout_2.addWidget(self.frame_8)
        self.web_status = QtWidgets.QLabel(self.frame_7)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.web_status.sizePolicy().hasHeightForWidth())
        self.web_status.setSizePolicy(sizePolicy)
        self.web_status.setMinimumSize(QtCore.QSize(240, 0))
        self.web_status.setMaximumSize(QtCore.QSize(240, 16777215))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.web_status.setFont(font)
        self.web_status.setFrameShape(QtWidgets.QFrame.Panel)
        self.web_status.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.web_status.setAlignment(QtCore.Qt.AlignCenter)
        self.web_status.setObjectName("web_status")
        self.verticalLayout_2.addWidget(self.web_status)
        self.price_status = QtWidgets.QLabel(self.frame_7)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.price_status.sizePolicy().hasHeightForWidth())
        self.price_status.setSizePolicy(sizePolicy)
        self.price_status.setMinimumSize(QtCore.QSize(240, 0))
        self.price_status.setMaximumSize(QtCore.QSize(240, 16777215))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.price_status.setFont(font)
        self.price_status.setFrameShape(QtWidgets.QFrame.Panel)
        self.price_status.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.price_status.setAlignment(QtCore.Qt.AlignCenter)
        self.price_status.setObjectName("price_status")
        self.verticalLayout_2.addWidget(self.price_status)
        self.horizontalLayout_5.addWidget(self.frame_7)
        self.frame_9 = QtWidgets.QFrame(self.frame)
        self.frame_9.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_9.setObjectName("frame_9")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.frame_9)
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_9.setSpacing(1)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.pt_cash_name = QtWidgets.QPlainTextEdit(self.frame_9)
        self.pt_cash_name.setMinimumSize(QtCore.QSize(0, 26))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.pt_cash_name.setFont(font)
        self.pt_cash_name.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.pt_cash_name.setReadOnly(True)
        self.pt_cash_name.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.pt_cash_name.setObjectName("pt_cash_name")
        self.verticalLayout_9.addWidget(self.pt_cash_name)
        self.pt_cash_descr = QtWidgets.QPlainTextEdit(self.frame_9)
        self.pt_cash_descr.setMinimumSize(QtCore.QSize(0, 26))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.pt_cash_descr.setFont(font)
        self.pt_cash_descr.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.pt_cash_descr.setReadOnly(True)
        self.pt_cash_descr.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.pt_cash_descr.setObjectName("pt_cash_descr")
        self.verticalLayout_9.addWidget(self.pt_cash_descr)
        self.pt_cash_price = QtWidgets.QPlainTextEdit(self.frame_9)
        self.pt_cash_price.setMinimumSize(QtCore.QSize(0, 26))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.pt_cash_price.setFont(font)
        self.pt_cash_price.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.pt_cash_price.setReadOnly(True)
        self.pt_cash_price.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.pt_cash_price.setObjectName("pt_cash_price")
        self.verticalLayout_9.addWidget(self.pt_cash_price)
        self.horizontalLayout_5.addWidget(self.frame_9)
        self.verticalLayout_3.addWidget(self.frame)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.frame_6 = QtWidgets.QFrame(self.widget_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_6.sizePolicy().hasHeightForWidth())
        self.frame_6.setSizePolicy(sizePolicy)
        self.frame_6.setMinimumSize(QtCore.QSize(0, 36))
        self.frame_6.setMaximumSize(QtCore.QSize(16777215, 36))
        self.frame_6.setBaseSize(QtCore.QSize(0, 36))
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_6)
        self.horizontalLayout_4.setContentsMargins(-1, 2, -1, 2)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem1 = QtWidgets.QSpacerItem(287, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.manufacturer_1 = QtWidgets.QLabel(self.frame_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.manufacturer_1.sizePolicy().hasHeightForWidth())
        self.manufacturer_1.setSizePolicy(sizePolicy)
        self.manufacturer_1.setMinimumSize(QtCore.QSize(128, 30))
        self.manufacturer_1.setMaximumSize(QtCore.QSize(128, 16777215))
        self.manufacturer_1.setBaseSize(QtCore.QSize(128, 0))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.manufacturer_1.setFont(font)
        self.manufacturer_1.setAlignment(QtCore.Qt.AlignCenter)
        self.manufacturer_1.setObjectName("manufacturer_1")
        self.horizontalLayout_4.addWidget(self.manufacturer_1)
        self.manufacturer_2 = QtWidgets.QLabel(self.frame_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.manufacturer_2.sizePolicy().hasHeightForWidth())
        self.manufacturer_2.setSizePolicy(sizePolicy)
        self.manufacturer_2.setMinimumSize(QtCore.QSize(128, 30))
        self.manufacturer_2.setMaximumSize(QtCore.QSize(128, 16777215))
        self.manufacturer_2.setBaseSize(QtCore.QSize(128, 0))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.manufacturer_2.setFont(font)
        self.manufacturer_2.setAlignment(QtCore.Qt.AlignCenter)
        self.manufacturer_2.setObjectName("manufacturer_2")
        self.horizontalLayout_4.addWidget(self.manufacturer_2)
        self.manufacturer_3 = QtWidgets.QLabel(self.frame_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.manufacturer_3.sizePolicy().hasHeightForWidth())
        self.manufacturer_3.setSizePolicy(sizePolicy)
        self.manufacturer_3.setMinimumSize(QtCore.QSize(128, 30))
        self.manufacturer_3.setMaximumSize(QtCore.QSize(128, 16777215))
        self.manufacturer_3.setBaseSize(QtCore.QSize(128, 0))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.manufacturer_3.setFont(font)
        self.manufacturer_3.setAlignment(QtCore.Qt.AlignCenter)
        self.manufacturer_3.setObjectName("manufacturer_3")
        self.horizontalLayout_4.addWidget(self.manufacturer_3)
        self.manufacturer_4 = QtWidgets.QLabel(self.frame_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.manufacturer_4.sizePolicy().hasHeightForWidth())
        self.manufacturer_4.setSizePolicy(sizePolicy)
        self.manufacturer_4.setMinimumSize(QtCore.QSize(128, 30))
        self.manufacturer_4.setMaximumSize(QtCore.QSize(128, 16777215))
        self.manufacturer_4.setBaseSize(QtCore.QSize(128, 0))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.manufacturer_4.setFont(font)
        self.manufacturer_4.setAlignment(QtCore.Qt.AlignCenter)
        self.manufacturer_4.setObjectName("manufacturer_4")
        self.horizontalLayout_4.addWidget(self.manufacturer_4)
        self.manufacturer_5 = QtWidgets.QLabel(self.frame_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.manufacturer_5.sizePolicy().hasHeightForWidth())
        self.manufacturer_5.setSizePolicy(sizePolicy)
        self.manufacturer_5.setMinimumSize(QtCore.QSize(128, 30))
        self.manufacturer_5.setMaximumSize(QtCore.QSize(128, 16777215))
        self.manufacturer_5.setBaseSize(QtCore.QSize(128, 0))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.manufacturer_5.setFont(font)
        self.manufacturer_5.setAlignment(QtCore.Qt.AlignCenter)
        self.manufacturer_5.setObjectName("manufacturer_5")
        self.horizontalLayout_4.addWidget(self.manufacturer_5)
        spacerItem2 = QtWidgets.QSpacerItem(287, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem2)
        self.verticalLayout_3.addWidget(self.frame_6)
        self.frame_2 = QtWidgets.QFrame(self.widget_3)
        self.frame_2.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout_7.setContentsMargins(9, 2, 9, 2)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.frame_3 = QtWidgets.QFrame(self.frame_2)
        self.frame_3.setMinimumSize(QtCore.QSize(0, 32))
        self.frame_3.setMaximumSize(QtCore.QSize(16777215, 32))
        self.frame_3.setBaseSize(QtCore.QSize(0, 32))
        self.frame_3.setLineWidth(0)
        self.frame_3.setObjectName("frame_3")
        self.hboxlayout = QtWidgets.QHBoxLayout(self.frame_3)
        self.hboxlayout.setContentsMargins(0, 0, 0, 0)
        self.hboxlayout.setSpacing(0)
        self.hboxlayout.setObjectName("hboxlayout")
        self.frame_4 = QtWidgets.QFrame(self.frame_3)
        self.frame_4.setObjectName("frame_4")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_4)
        self.horizontalLayout.setContentsMargins(12, 0, 12, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.chb_show_exact = QtWidgets.QCheckBox(self.frame_4)
        self.chb_show_exact.setEnabled(True)
        self.chb_show_exact.setMaximumSize(QtCore.QSize(120, 16777215))
        self.chb_show_exact.setObjectName("chb_show_exact")
        self.horizontalLayout.addWidget(self.chb_show_exact)
        self.chb_show_date = QtWidgets.QCheckBox(self.frame_4)
        self.chb_show_date.setEnabled(True)
        self.chb_show_date.setMaximumSize(QtCore.QSize(120, 16777215))
        self.chb_show_date.setObjectName("chb_show_date")
        self.horizontalLayout.addWidget(self.chb_show_date)
        self.pb_adv_search = QtWidgets.QPushButton(self.frame_4)
        self.pb_adv_search.setEnabled(True)
        self.pb_adv_search.setMaximumSize(QtCore.QSize(120, 16777215))
        self.pb_adv_search.setAutoDefault(False)
        self.pb_adv_search.setDefault(False)
        self.pb_adv_search.setFlat(False)
        self.pb_adv_search.setObjectName("pb_adv_search")
        self.horizontalLayout.addWidget(self.pb_adv_search)
        self.hboxlayout.addWidget(self.frame_4)
        self.search_widget = QtWidgets.QWidget(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_widget.sizePolicy().hasHeightForWidth())
        self.search_widget.setSizePolicy(sizePolicy)
        self.search_widget.setMinimumSize(QtCore.QSize(540, 30))
        self.search_widget.setMaximumSize(QtCore.QSize(540, 30))
        self.search_widget.setBaseSize(QtCore.QSize(540, 30))
        self.search_widget.setObjectName("search_widget")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.search_widget)
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.search_layout = QtWidgets.QHBoxLayout()
        self.search_layout.setSpacing(0)
        self.search_layout.setObjectName("search_layout")
        self.horizontalLayout_9.addLayout(self.search_layout)
        self.hboxlayout.addWidget(self.search_widget)
        self.frame_5 = QtWidgets.QFrame(self.frame_3)
        self.frame_5.setObjectName("frame_5")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.frame_5)
        self.horizontalLayout_6.setContentsMargins(12, 0, 12, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.chb_price_name_only = QtWidgets.QCheckBox(self.frame_5)
        self.chb_price_name_only.setEnabled(True)
        self.chb_price_name_only.setChecked(True)
        self.chb_price_name_only.setObjectName("chb_price_name_only")
        self.horizontalLayout_6.addWidget(self.chb_price_name_only)
        self.chb_search_eng = QtWidgets.QCheckBox(self.frame_5)
        self.chb_search_eng.setEnabled(True)
        self.chb_search_eng.setChecked(True)
        self.chb_search_eng.setObjectName("chb_search_eng")
        self.horizontalLayout_6.addWidget(self.chb_search_eng)
        self.chb_search_narrow = QtWidgets.QCheckBox(self.frame_5)
        self.chb_search_narrow.setChecked(True)
        self.chb_search_narrow.setObjectName("chb_search_narrow")
        self.horizontalLayout_6.addWidget(self.chb_search_narrow)
        self.hboxlayout.addWidget(self.frame_5)
        self.verticalLayout_7.addWidget(self.frame_3)
        self.web_load_progress_bar = QtWidgets.QProgressBar(self.frame_2)
        self.web_load_progress_bar.setMinimumSize(QtCore.QSize(0, 3))
        self.web_load_progress_bar.setMaximumSize(QtCore.QSize(16777215, 3))
        self.web_load_progress_bar.setProperty("value", 0)
        self.web_load_progress_bar.setTextVisible(False)
        self.web_load_progress_bar.setObjectName("web_load_progress_bar")
        self.verticalLayout_7.addWidget(self.web_load_progress_bar)
        self.verticalLayout_3.addWidget(self.frame_2)
        self.frame.raise_()
        self.frame_2.raise_()
        self.frame_6.raise_()
        self.verticalLayout_8.addWidget(self.widget_3)
        self.verticalLayout.addWidget(self.HEAD)
        self.BODY = QtWidgets.QWidget(self.centralwidget)
        self.BODY.setObjectName("BODY")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.BODY)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(2)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.tab_widget = QtWidgets.QTabWidget(self.BODY)
        self.tab_widget.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.tab_widget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tab_widget.setObjectName("tab_widget")
        self.tab_0 = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab_0.sizePolicy().hasHeightForWidth())
        self.tab_0.setSizePolicy(sizePolicy)
        self.tab_0.setMinimumSize(QtCore.QSize(0, 0))
        self.tab_0.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.tab_0.setObjectName("tab_0")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.tab_0)
        self.verticalLayout_5.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.table_parts = QtWidgets.QTableWidget(self.tab_0)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        self.table_parts.setFont(font)
        self.table_parts.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_parts.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table_parts.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_parts.setShowGrid(False)
        self.table_parts.setColumnCount(8)
        self.table_parts.setObjectName("table_parts")
        self.table_parts.setRowCount(0)
        self.table_parts.horizontalHeader().setDefaultSectionSize(4)
        self.table_parts.horizontalHeader().setHighlightSections(False)
        self.table_parts.horizontalHeader().setMinimumSectionSize(4)
        self.table_parts.verticalHeader().setVisible(False)
        self.table_parts.verticalHeader().setDefaultSectionSize(14)
        self.table_parts.verticalHeader().setMinimumSectionSize(14)
        self.verticalLayout_5.addWidget(self.table_parts)
        self.tab_widget.addTab(self.tab_0, "")
        self.tab_1 = QtWidgets.QWidget()
        self.tab_1.setObjectName("tab_1")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.tab_1)
        self.verticalLayout_6.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.table_accesory = QtWidgets.QTableWidget(self.tab_1)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        self.table_accesory.setFont(font)
        self.table_accesory.setFrameShape(QtWidgets.QFrame.Panel)
        self.table_accesory.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.table_accesory.setAutoScrollMargin(16)
        self.table_accesory.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_accesory.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table_accesory.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_accesory.setShowGrid(False)
        self.table_accesory.setColumnCount(8)
        self.table_accesory.setObjectName("table_accesory")
        self.table_accesory.setRowCount(0)
        self.table_accesory.horizontalHeader().setDefaultSectionSize(4)
        self.table_accesory.horizontalHeader().setHighlightSections(False)
        self.table_accesory.horizontalHeader().setMinimumSectionSize(4)
        self.table_accesory.verticalHeader().setVisible(False)
        self.table_accesory.verticalHeader().setDefaultSectionSize(14)
        self.table_accesory.verticalHeader().setMinimumSectionSize(14)
        self.verticalLayout_6.addWidget(self.table_accesory)
        self.tab_widget.addTab(self.tab_1, "")
        self.horizontalLayout_3.addWidget(self.tab_widget)
        self.price_widget = QtWidgets.QWidget(self.BODY)
        self.price_widget.setObjectName("price_widget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.price_widget)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setSpacing(2)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.model_widget = QtWidgets.QWidget(self.price_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(20)
        sizePolicy.setHeightForWidth(self.model_widget.sizePolicy().hasHeightForWidth())
        self.model_widget.setSizePolicy(sizePolicy)
        self.model_widget.setMinimumSize(QtCore.QSize(0, 20))
        self.model_widget.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.model_widget.setFont(font)
        self.model_widget.setObjectName("model_widget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.model_widget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lay_model_buttons = QtWidgets.QHBoxLayout()
        self.lay_model_buttons.setObjectName("lay_model_buttons")
        self.horizontalLayout_2.addLayout(self.lay_model_buttons)
        self.verticalLayout_4.addWidget(self.model_widget)
        self.table_price = QtWidgets.QTableWidget(self.price_widget)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        self.table_price.setFont(font)
        self.table_price.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_price.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table_price.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_price.setShowGrid(False)
        self.table_price.setColumnCount(3)
        self.table_price.setObjectName("table_price")
        self.table_price.setRowCount(0)
        self.table_price.horizontalHeader().setDefaultSectionSize(4)
        self.table_price.horizontalHeader().setHighlightSections(False)
        self.table_price.horizontalHeader().setMinimumSectionSize(4)
        self.table_price.verticalHeader().setVisible(False)
        self.table_price.verticalHeader().setDefaultSectionSize(14)
        self.table_price.verticalHeader().setMinimumSectionSize(14)
        self.verticalLayout_4.addWidget(self.table_price)
        self.horizontalLayout_3.addWidget(self.price_widget)
        self.verticalLayout.addWidget(self.BODY)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.tab_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.help.setText(_translate("MainWindow", "Помощь"))
        self.settings_button.setText(_translate("MainWindow", "Настройки"))
        self.chb_show_exact.setText(_translate("MainWindow", "Искомая модель"))
        self.chb_show_date.setText(_translate("MainWindow", "Показать дату"))
        self.pb_adv_search.setText(_translate("MainWindow", "Расш. поиск"))
        self.chb_price_name_only.setText(_translate("MainWindow", "Модель прайса"))
        self.chb_search_eng.setText(_translate("MainWindow", "Латиница"))
        self.chb_search_narrow.setText(_translate("MainWindow", "Минимум 2"))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_0), _translate("MainWindow", "   ЗАПЧАСТИ   "))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_1), _translate("MainWindow", "  АКСЕССУАРЫ  "))
