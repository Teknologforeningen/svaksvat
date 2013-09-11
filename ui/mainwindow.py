# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created: Sun Sep 30 20:10:11 2012
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
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/res/mainicon.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.searchlabelLabel = QtGui.QLabel(self.centralwidget)
        self.searchlabelLabel.setObjectName(_fromUtf8("searchlabelLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.searchlabelLabel)
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
        self.menuNew = QtGui.QMenu(self.menubar)
        self.menuNew.setObjectName(_fromUtf8("menuNew"))
        self.menuEdit = QtGui.QMenu(self.menubar)
        self.menuEdit.setObjectName(_fromUtf8("menuEdit"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionNewMember = QtGui.QAction(MainWindow)
        self.actionNewMember.setObjectName(_fromUtf8("actionNewMember"))
        self.actionNewGroup = QtGui.QAction(MainWindow)
        self.actionNewGroup.setObjectName(_fromUtf8("actionNewGroup"))
        self.actionNewPost = QtGui.QAction(MainWindow)
        self.actionNewPost.setObjectName(_fromUtf8("actionNewPost"))
        self.actionGrupper = QtGui.QAction(MainWindow)
        self.actionGrupper.setObjectName(_fromUtf8("actionGrupper"))
        self.actionPoster = QtGui.QAction(MainWindow)
        self.actionPoster.setObjectName(_fromUtf8("actionPoster"))
        self.actionMakeBackup = QtGui.QAction(MainWindow)
        self.actionMakeBackup.setObjectName(_fromUtf8("actionMakeBackup"))
        self.actionRestoreFromBackup = QtGui.QAction(MainWindow)
        self.actionRestoreFromBackup.setObjectName(_fromUtf8("actionRestoreFromBackup"))
        self.actionAvdelningar = QtGui.QAction(MainWindow)
        self.actionAvdelningar.setObjectName(_fromUtf8("actionAvdelningar"))
        self.actionNewDepartment = QtGui.QAction(MainWindow)
        self.actionNewDepartment.setObjectName(_fromUtf8("actionNewDepartment"))
        self.actionRemoveMember = QtGui.QAction(MainWindow)
        self.actionRemoveMember.setObjectName(_fromUtf8("actionRemoveMember"))
        self.actionEditMember = QtGui.QAction(MainWindow)
        self.actionEditMember.setObjectName(_fromUtf8("actionEditMember"))
        self.menuNew.addAction(self.actionNewMember)
        self.menuNew.addAction(self.actionNewGroup)
        self.menuNew.addAction(self.actionNewPost)
        self.menuNew.addAction(self.actionNewDepartment)
        self.menuEdit.addAction(self.actionGrupper)
        self.menuEdit.addAction(self.actionPoster)
        self.menuEdit.addAction(self.actionAvdelningar)
        self.menuFile.addAction(self.actionMakeBackup)
        self.menuFile.addAction(self.actionRestoreFromBackup)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuNew.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.searchlabelLabel.setBuddy(self.searchfield)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.searchlabelLabel.setText(QtGui.QApplication.translate("MainWindow", "Sök", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Info", None, QtGui.QApplication.UnicodeUTF8))
        self.menuNew.setTitle(QtGui.QApplication.translate("MainWindow", "Ny", None, QtGui.QApplication.UnicodeUTF8))
        self.menuEdit.setTitle(QtGui.QApplication.translate("MainWindow", "Editera", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "Fil", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNewMember.setText(QtGui.QApplication.translate("MainWindow", "Medlem", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNewMember.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+N", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNewGroup.setText(QtGui.QApplication.translate("MainWindow", "Grupp", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNewPost.setText(QtGui.QApplication.translate("MainWindow", "Post", None, QtGui.QApplication.UnicodeUTF8))
        self.actionGrupper.setText(QtGui.QApplication.translate("MainWindow", "Grupper", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPoster.setText(QtGui.QApplication.translate("MainWindow", "Poster", None, QtGui.QApplication.UnicodeUTF8))
        self.actionMakeBackup.setText(QtGui.QApplication.translate("MainWindow", "Gör säkerhetskopia", None, QtGui.QApplication.UnicodeUTF8))
        self.actionMakeBackup.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+S", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRestoreFromBackup.setText(QtGui.QApplication.translate("MainWindow", "Återställ databas", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRestoreFromBackup.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+L", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAvdelningar.setText(QtGui.QApplication.translate("MainWindow", "Avdelningar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNewDepartment.setText(QtGui.QApplication.translate("MainWindow", "Avdelning", None, QtGui.QApplication.UnicodeUTF8))
        self.actionRemoveMember.setText(QtGui.QApplication.translate("MainWindow", "Ta bort medlem", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEditMember.setText(QtGui.QApplication.translate("MainWindow", "Editera Medlem", None, QtGui.QApplication.UnicodeUTF8))

import svaksvat_rc