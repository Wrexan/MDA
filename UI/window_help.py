# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'window_help.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1240, 700)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.text = QtWidgets.QPlainTextEdit(Dialog)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(12)
        self.text.setFont(font)
        self.text.setReadOnly(True)
        self.text.setPlainText("")
        self.text.setObjectName("text")
        self.verticalLayout.addWidget(self.text)
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setMinimumSize(QtCore.QSize(0, 0))
        self.frame.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(-1, 2, -1, 2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(0, 23))
        self.label.setMaximumSize(QtCore.QSize(16777215, 23))
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.project_link = QtWidgets.QLabel(self.frame)
        self.project_link.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.project_link.setOpenExternalLinks(True)
        self.project_link.setObjectName("project_link")
        self.horizontalLayout.addWidget(self.project_link)
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Автор: Гостев В.   Помощь в тестировании: Дяченко А., Довгопятый Т., Кондратченко К."))
        self.project_link.setText(_translate("Dialog", "<a href=\"https://github.com/Wrexan/MDA\"> <font size=3 color=black>Страница проекта</font> </a>"))
        self.label_2.setText(_translate("Dialog", "[2022]"))
