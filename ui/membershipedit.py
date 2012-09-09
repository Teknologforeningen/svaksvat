# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'membershipedit.ui'
#
# Created: Mon Sep 10 00:30:32 2012
#      by: PyQt4 UI code generator 4.9.3
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
        MembershipEdit.resize(244, 330)
        MembershipEdit.setWindowTitle(_fromUtf8(""))
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
        self.onwards_radioButton = QtGui.QRadioButton(self.mandate_GroupBox)
        self.onwards_radioButton.setObjectName(_fromUtf8("onwards_radioButton"))
        self.verticalLayout_2.addWidget(self.onwards_radioButton)
        self.otherMandate_radioButton = QtGui.QRadioButton(self.mandate_GroupBox)
        self.otherMandate_radioButton.setObjectName(_fromUtf8("otherMandate_radioButton"))
        self.verticalLayout_2.addWidget(self.otherMandate_radioButton)
        self.verticalLayout.addWidget(self.mandate_GroupBox)
        self.startAndEndTimeWidget = QtGui.QWidget(MembershipEdit)
        self.startAndEndTimeWidget.setObjectName(_fromUtf8("startAndEndTimeWidget"))
        self.startEndLayout = QtGui.QFormLayout(self.startAndEndTimeWidget)
        self.startEndLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.startEndLayout.setMargin(0)
        self.startEndLayout.setObjectName(_fromUtf8("startEndLayout"))
        self.startdatumLabel_2 = QtGui.QLabel(self.startAndEndTimeWidget)
        self.startdatumLabel_2.setObjectName(_fromUtf8("startdatumLabel_2"))
        self.startEndLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.startdatumLabel_2)
        self.startTime_fld = QtGui.QDateEdit(self.startAndEndTimeWidget)
        self.startTime_fld.setObjectName(_fromUtf8("startTime_fld"))
        self.startEndLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.startTime_fld)
        self.endTimeLabel = QtGui.QLabel(self.startAndEndTimeWidget)
        self.endTimeLabel.setObjectName(_fromUtf8("endTimeLabel"))
        self.startEndLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.endTimeLabel)
        self.endTime_fld = QtGui.QDateEdit(self.startAndEndTimeWidget)
        self.endTime_fld.setObjectName(_fromUtf8("endTime_fld"))
        self.startEndLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.endTime_fld)
        self.verticalLayout.addWidget(self.startAndEndTimeWidget)
        self.startYearWidget = QtGui.QWidget(MembershipEdit)
        self.startYearWidget.setObjectName(_fromUtf8("startYearWidget"))
        self.startYearLayout = QtGui.QFormLayout(self.startYearWidget)
        self.startYearLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.startYearLayout.setMargin(0)
        self.startYearLayout.setObjectName(_fromUtf8("startYearLayout"))
        self.frNRLabel = QtGui.QLabel(self.startYearWidget)
        self.frNRLabel.setObjectName(_fromUtf8("frNRLabel"))
        self.startYearLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.frNRLabel)
        self.startYear_spinBox = QtGui.QSpinBox(self.startYearWidget)
        self.startYear_spinBox.setObjectName(_fromUtf8("startYear_spinBox"))
        self.startYearLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.startYear_spinBox)
        self.verticalLayout.addWidget(self.startYearWidget)
        self.buttonBox = QtGui.QDialogButtonBox(MembershipEdit)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout_3.addLayout(self.verticalLayout)

        self.retranslateUi(MembershipEdit)
        QtCore.QObject.connect(self.wholeyear_radioButton, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.startYearWidget.setVisible)
        QtCore.QObject.connect(self.laborday_radioButton, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.startYearWidget.setVisible)
        QtCore.QObject.connect(self.laborday_radioButton, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.startAndEndTimeWidget.setHidden)
        QtCore.QObject.connect(self.onwards_radioButton, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.endTime_fld.setHidden)
        QtCore.QObject.connect(self.wholeyear_radioButton, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.startAndEndTimeWidget.setHidden)
        QtCore.QObject.connect(self.onwards_radioButton, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.endTimeLabel.setHidden)
        QtCore.QMetaObject.connectSlotsByName(MembershipEdit)

    def retranslateUi(self, MembershipEdit):
        self.mandate_GroupBox.setTitle(QtGui.QApplication.translate("MembershipEdit", "Mandattid", None, QtGui.QApplication.UnicodeUTF8))
        self.wholeyear_radioButton.setText(QtGui.QApplication.translate("MembershipEdit", "Hela året", None, QtGui.QApplication.UnicodeUTF8))
        self.laborday_radioButton.setText(QtGui.QApplication.translate("MembershipEdit", "Vapp till vapp", None, QtGui.QApplication.UnicodeUTF8))
        self.onwards_radioButton.setText(QtGui.QApplication.translate("MembershipEdit", "Obestämd tid", None, QtGui.QApplication.UnicodeUTF8))
        self.otherMandate_radioButton.setText(QtGui.QApplication.translate("MembershipEdit", "Annan tid", None, QtGui.QApplication.UnicodeUTF8))
        self.startdatumLabel_2.setText(QtGui.QApplication.translate("MembershipEdit", "Startdatum", None, QtGui.QApplication.UnicodeUTF8))
        self.endTimeLabel.setText(QtGui.QApplication.translate("MembershipEdit", "Slutdatum", None, QtGui.QApplication.UnicodeUTF8))
        self.frNRLabel.setText(QtGui.QApplication.translate("MembershipEdit", "Från år", None, QtGui.QApplication.UnicodeUTF8))

