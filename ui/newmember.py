# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newmember.ui'
#
# Created: Sat Sep  1 12:12:10 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_NewMember(object):
    def setupUi(self, NewMember):
        NewMember.setObjectName(_fromUtf8("NewMember"))
        NewMember.resize(370, 330)
        self.verticalLayout_2 = QtGui.QVBoxLayout(NewMember)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.efternamnLabel = QtGui.QLabel(NewMember)
        self.efternamnLabel.setObjectName(_fromUtf8("efternamnLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.efternamnLabel)
        self.surname_fld = QtGui.QLineEdit(NewMember)
        self.surname_fld.setObjectName(_fromUtf8("surname_fld"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.surname_fld)
        self.allaFRnamnLabel = QtGui.QLabel(NewMember)
        self.allaFRnamnLabel.setObjectName(_fromUtf8("allaFRnamnLabel"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.allaFRnamnLabel)
        self.givenNames_fld = QtGui.QLineEdit(NewMember)
        self.givenNames_fld.setObjectName(_fromUtf8("givenNames_fld"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.givenNames_fld)
        self.adressLabel = QtGui.QLabel(NewMember)
        self.adressLabel.setObjectName(_fromUtf8("adressLabel"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.adressLabel)
        self.streetAddress_fld = QtGui.QLineEdit(NewMember)
        self.streetAddress_fld.setObjectName(_fromUtf8("streetAddress_fld"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.streetAddress_fld)
        self.telefonLabel = QtGui.QLabel(NewMember)
        self.telefonLabel.setObjectName(_fromUtf8("telefonLabel"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.telefonLabel)
        self.phone_fld = QtGui.QLineEdit(NewMember)
        self.phone_fld.setObjectName(_fromUtf8("phone_fld"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.phone_fld)
        self.emailLabel = QtGui.QLabel(NewMember)
        self.emailLabel.setObjectName(_fromUtf8("emailLabel"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.LabelRole, self.emailLabel)
        self.email_fld = QtGui.QLineEdit(NewMember)
        self.email_fld.setObjectName(_fromUtf8("email_fld"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.email_fld)
        self.avdelningLabel = QtGui.QLabel(NewMember)
        self.avdelningLabel.setObjectName(_fromUtf8("avdelningLabel"))
        self.formLayout.setWidget(6, QtGui.QFormLayout.LabelRole, self.avdelningLabel)
        self.department_comboBox = QtGui.QComboBox(NewMember)
        self.department_comboBox.setEditable(True)
        self.department_comboBox.setObjectName(_fromUtf8("department_comboBox"))
        self.formLayout.setWidget(6, QtGui.QFormLayout.FieldRole, self.department_comboBox)
        self.tilltalsnamnLabel = QtGui.QLabel(NewMember)
        self.tilltalsnamnLabel.setObjectName(_fromUtf8("tilltalsnamnLabel"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.tilltalsnamnLabel)
        self.preferredName_fld = QtGui.QLineEdit(NewMember)
        self.preferredName_fld.setObjectName(_fromUtf8("preferredName_fld"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.preferredName_fld)
        self.gRTillPhuxLabel = QtGui.QLabel(NewMember)
        self.gRTillPhuxLabel.setObjectName(_fromUtf8("gRTillPhuxLabel"))
        self.formLayout.setWidget(7, QtGui.QFormLayout.LabelRole, self.gRTillPhuxLabel)
        self.makePhux_CheckBox = QtGui.QCheckBox(NewMember)
        self.makePhux_CheckBox.setObjectName(_fromUtf8("makePhux_CheckBox"))
        self.formLayout.setWidget(7, QtGui.QFormLayout.FieldRole, self.makePhux_CheckBox)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtGui.QDialogButtonBox(NewMember)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(NewMember)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), NewMember.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), NewMember.reject)
        QtCore.QMetaObject.connectSlotsByName(NewMember)

    def retranslateUi(self, NewMember):
        NewMember.setWindowTitle(QtGui.QApplication.translate("NewMember", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.efternamnLabel.setText(QtGui.QApplication.translate("NewMember", "Efternamn", None, QtGui.QApplication.UnicodeUTF8))
        self.allaFRnamnLabel.setText(QtGui.QApplication.translate("NewMember", "Alla förnamn", None, QtGui.QApplication.UnicodeUTF8))
        self.adressLabel.setText(QtGui.QApplication.translate("NewMember", "Adress", None, QtGui.QApplication.UnicodeUTF8))
        self.telefonLabel.setText(QtGui.QApplication.translate("NewMember", "Telefon", None, QtGui.QApplication.UnicodeUTF8))
        self.emailLabel.setText(QtGui.QApplication.translate("NewMember", "Email", None, QtGui.QApplication.UnicodeUTF8))
        self.avdelningLabel.setText(QtGui.QApplication.translate("NewMember", "Avdelning", None, QtGui.QApplication.UnicodeUTF8))
        self.tilltalsnamnLabel.setText(QtGui.QApplication.translate("NewMember", "Tilltalsnamn", None, QtGui.QApplication.UnicodeUTF8))
        self.gRTillPhuxLabel.setText(QtGui.QApplication.translate("NewMember", "Gör till Phux", None, QtGui.QApplication.UnicodeUTF8))

