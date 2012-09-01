# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created: Sat Sep  1 12:08:13 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(337, 400)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.sKLabel = QtGui.QLabel(self.centralwidget)
        self.sKLabel.setObjectName(_fromUtf8("sKLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.sKLabel)
        self.searchfield = QtGui.QLineEdit(self.centralwidget)
        self.searchfield.setObjectName(_fromUtf8("searchfield"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.searchfield)
        self.verticalLayout.addLayout(self.formLayout)
        self.memberlistwidget = QtGui.QListWidget(self.centralwidget)
        self.memberlistwidget.setObjectName(_fromUtf8("memberlistwidget"))
        self.verticalLayout.addWidget(self.memberlistwidget)
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.memberinfo = QtGui.QTextEdit(self.centralwidget)
        self.memberinfo.setUndoRedoEnabled(True)
        self.memberinfo.setReadOnly(True)
        self.memberinfo.setObjectName(_fromUtf8("memberinfo"))
        self.verticalLayout.addWidget(self.memberinfo)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 337, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuNy = QtGui.QMenu(self.menubar)
        self.menuNy.setObjectName(_fromUtf8("menuNy"))
        self.menuEditera = QtGui.QMenu(self.menubar)
        self.menuEditera.setObjectName(_fromUtf8("menuEditera"))
        self.menuFil = QtGui.QMenu(self.menubar)
        self.menuFil.setObjectName(_fromUtf8("menuFil"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionAnv_ndare = QtGui.QAction(MainWindow)
        self.actionAnv_ndare.setObjectName(_fromUtf8("actionAnv_ndare"))
        self.actionGrupp = QtGui.QAction(MainWindow)
        self.actionGrupp.setObjectName(_fromUtf8("actionGrupp"))
        self.actionPost = QtGui.QAction(MainWindow)
        self.actionPost.setObjectName(_fromUtf8("actionPost"))
        self.actionAnv_ndare_2 = QtGui.QAction(MainWindow)
        self.actionAnv_ndare_2.setObjectName(_fromUtf8("actionAnv_ndare_2"))
        self.actionGrupper = QtGui.QAction(MainWindow)
        self.actionGrupper.setObjectName(_fromUtf8("actionGrupper"))
        self.actionPoster = QtGui.QAction(MainWindow)
        self.actionPoster.setObjectName(_fromUtf8("actionPoster"))
        self.actionG_r_s_kerhetskopia = QtGui.QAction(MainWindow)
        self.actionG_r_s_kerhetskopia.setObjectName(_fromUtf8("actionG_r_s_kerhetskopia"))
        self.actionAsdf = QtGui.QAction(MainWindow)
        self.actionAsdf.setObjectName(_fromUtf8("actionAsdf"))
        self.actionAvdelningar = QtGui.QAction(MainWindow)
        self.actionAvdelningar.setObjectName(_fromUtf8("actionAvdelningar"))
        self.menuNy.addAction(self.actionAnv_ndare)
        self.menuNy.addAction(self.actionGrupp)
        self.menuNy.addAction(self.actionPost)
        self.menuEditera.addAction(self.actionGrupper)
        self.menuEditera.addAction(self.actionPoster)
        self.menuEditera.addAction(self.actionAvdelningar)
        self.menuFil.addAction(self.actionG_r_s_kerhetskopia)
        self.menuFil.addAction(self.actionAsdf)
        self.menubar.addAction(self.menuFil.menuAction())
        self.menubar.addAction(self.menuNy.menuAction())
        self.menubar.addAction(self.menuEditera.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.sKLabel.setText(QtGui.QApplication.translate("MainWindow", "Sök", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Info", None, QtGui.QApplication.UnicodeUTF8))
        self.menuNy.setTitle(QtGui.QApplication.translate("MainWindow", "Ny", None, QtGui.QApplication.UnicodeUTF8))
        self.menuEditera.setTitle(QtGui.QApplication.translate("MainWindow", "Editera", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFil.setTitle(QtGui.QApplication.translate("MainWindow", "Fil", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAnv_ndare.setText(QtGui.QApplication.translate("MainWindow", "Medlem", None, QtGui.QApplication.UnicodeUTF8))
        self.actionGrupp.setText(QtGui.QApplication.translate("MainWindow", "Grupp", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPost.setText(QtGui.QApplication.translate("MainWindow", "Post", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAnv_ndare_2.setText(QtGui.QApplication.translate("MainWindow", "Användare", None, QtGui.QApplication.UnicodeUTF8))
        self.actionGrupper.setText(QtGui.QApplication.translate("MainWindow", "Grupper", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPoster.setText(QtGui.QApplication.translate("MainWindow", "Poster", None, QtGui.QApplication.UnicodeUTF8))
        self.actionG_r_s_kerhetskopia.setText(QtGui.QApplication.translate("MainWindow", "Gör säkerhetskopia", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAsdf.setText(QtGui.QApplication.translate("MainWindow", "Återställ databas", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAvdelningar.setText(QtGui.QApplication.translate("MainWindow", "Avdelningar", None, QtGui.QApplication.UnicodeUTF8))

