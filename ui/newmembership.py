# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newmembership.ui'
#
# Created: Sun Sep  2 17:33:02 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MembershipEdit(object):
    def setupUi(self, MembershipEdit):
        MembershipEdit.setObjectName(_fromUtf8("MembershipEdit"))
        MembershipEdit.resize(233, 268)
        self.verticalLayout_3 = QtGui.QVBoxLayout(MembershipEdit)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.mandate_GroupBox = QtGui.QGroupBox(MembershipEdit)
        self.mandate_GroupBox.setObjectName(_fromUtf8("mandate_GroupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.mandate_GroupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.wholeyear_radioButton = QtGui.QRadioButton(self.mandate_GroupBox)
        self.wholeyear_radioButton.setObjectName(_fromUtf8("wholeyear_radioButton"))
        self.verticalLayout_2.addWidget(self.wholeyear_radioButton)
        self.laborday_radioButton = QtGui.QRadioButton(self.mandate_GroupBox)
        self.laborday_radioButton.setObjectName(_fromUtf8("laborday_radioButton"))
        self.verticalLayout_2.addWidget(self.laborday_radioButton)
        self.otherMandate_radioButton = QtGui.QRadioButton(self.mandate_GroupBox)
        self.otherMandate_radioButton.setObjectName(_fromUtf8("otherMandate_radioButton"))
        self.verticalLayout_2.addWidget(self.otherMandate_radioButton)
        self.verticalLayout.addWidget(self.mandate_GroupBox)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.startdatumLabel = QtGui.QLabel(MembershipEdit)
        self.startdatumLabel.setObjectName(_fromUtf8("startdatumLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.startdatumLabel)
        self.startTime_fld = QtGui.QDateEdit(MembershipEdit)
        self.startTime_fld.setObjectName(_fromUtf8("startTime_fld"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.startTime_fld)
        self.slutdatumLabel = QtGui.QLabel(MembershipEdit)
        self.slutdatumLabel.setObjectName(_fromUtf8("slutdatumLabel"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.slutdatumLabel)
        self.endDate_fld = QtGui.QDateEdit(MembershipEdit)
        self.endDate_fld.setObjectName(_fromUtf8("endDate_fld"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.endDate_fld)
        self.frNRLabel = QtGui.QLabel(MembershipEdit)
        self.frNRLabel.setObjectName(_fromUtf8("frNRLabel"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.frNRLabel)
        self.startYear = QtGui.QSpinBox(MembershipEdit)
        self.startYear.setObjectName(_fromUtf8("startYear"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.startYear)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtGui.QDialogButtonBox(MembershipEdit)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout_3.addLayout(self.verticalLayout)

        self.retranslateUi(MembershipEdit)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), MembershipEdit.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), MembershipEdit.reject)
        QtCore.QMetaObject.connectSlotsByName(MembershipEdit)

    def retranslateUi(self, MembershipEdit):
        MembershipEdit.setWindowTitle(QtGui.QApplication.translate("MembershipEdit", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.mandate_GroupBox.setTitle(QtGui.QApplication.translate("MembershipEdit", "Mandattid", None, QtGui.QApplication.UnicodeUTF8))
        self.wholeyear_radioButton.setText(QtGui.QApplication.translate("MembershipEdit", "Hela året", None, QtGui.QApplication.UnicodeUTF8))
        self.laborday_radioButton.setText(QtGui.QApplication.translate("MembershipEdit", "Vapp till vapp", None, QtGui.QApplication.UnicodeUTF8))
        self.otherMandate_radioButton.setText(QtGui.QApplication.translate("MembershipEdit", "Annan tid", None, QtGui.QApplication.UnicodeUTF8))
        self.startdatumLabel.setText(QtGui.QApplication.translate("MembershipEdit", "Startdatum", None, QtGui.QApplication.UnicodeUTF8))
        self.slutdatumLabel.setText(QtGui.QApplication.translate("MembershipEdit", "Slutdatum", None, QtGui.QApplication.UnicodeUTF8))
        self.frNRLabel.setText(QtGui.QApplication.translate("MembershipEdit", "Från år", None, QtGui.QApplication.UnicodeUTF8))

