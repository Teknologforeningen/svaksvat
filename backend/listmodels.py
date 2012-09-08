
# imports
import time
import datetime

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui.membershipedit import Ui_MembershipEdit

from . import orm

# constants
# exception classes
# interface functions

#TODO: Adding membership through combobox sometimes doesn't leave editor open.
# especially if last group in the list has the same name.
# Has something to do with MemberEdit being a QDialog. If it's QWidget the
# problem disappears.
def configure_membership_qcombobox(combobox, membershiptypetablename, session):
    membershiptargetclass = getattr(orm, membershiptypetablename)
    membershiptargets = session.query(membershiptargetclass).order_by(
            membershiptargetclass.name_fld).all()
    membershiptargetnames = [target.name_fld for target in
            membershiptargets]

    completer = QCompleter(membershiptargetnames)
    combobox.setCompleter(completer)
    combobox.addItems(membershiptargetnames)

    return combobox

def assign_membership_to_member(session, membershiptypename, membershipname,
        member, parent=None, combobox=None, indefinite_time=False):
    membership = orm.create_membership(session,
            membershiptypename, membershipname)

    if not membership:
        questiontext = "%s finns inte. Skall den skapas?" % (membershipname)

        if QMessageBox.question(parent, membershipname + " hittades inte!",
                questiontext, "Nej", "Ja",
                escapeButtonNumber=0):
            membership = orm.create_membership(session,
                    membershiptypename, membershipname,
                    create_nonexistent_target=True)
            if combobox:
                combobox.addItem(membershipname)

        else:
            session.rollback()
            return False

    membership.member = member

    membership.startTime_fld = datetime.datetime.now()
    if not indefinite_time:
        membership.setMandateToThisYear()

    return True


# classes

class MembershipListModel(QAbstractListModel):
    def __init__(self, session, member, parent=None,
        membershiptype="group", add_membership_combobox=None):
        super().__init__(parent)
        self.session = session
        self.member = session.merge(member) # Get local object for this Model
        self.membershiptype = membershiptype
        self.internalDataRefresh()
        self.combobox = add_membership_combobox
        self.configureAddMembershipQComboBox()
        self.parent = parent

    def internalDataRefresh(self):
        self.session.refresh(self.member)
        self._data = getattr(self.member, self.membershiptype + "memberships")

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < self.rowCount():
            return None

        row = index.row()

        membership = self._data[row]
        membershiptarget = getattr(membership, self.membershiptype)
        duration = self.membershipDuration(membership)
        if role == Qt.DisplayRole:
            return "%s %s" % (membershiptarget.name_fld,
                    duration)

        elif role == Qt.EditRole:
            return membership

        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            membership = self.data(index, role)
            membership.startTime_fld = value[0]
            membership.endTime_fld = value[1]
            self.session.commit()
            return True

        return False

    def flags(self, index):
        flag = super().flags(index)
        return flag|Qt.ItemIsEditable

    def removeRows(self, row, count, parent=QModelIndex()):
        self.beginRemoveRows(parent, row, row+count-1)
        if row + count > self.rowCount():
            self.endRemoveRows()
            return False

        memberships_to_delete = [
                membership for membership in self._data[row:row + count]]

        for membership in memberships_to_delete:
            self.session.delete(membership)

        self.endRemoveRows()
        return True

    def insertRows(self, row, count, parent=QModelIndex()):
        self.beginInsertRows(parent, row, row+count-1)

        membershipname = self.combobox.currentText()
        membershiptypename = self.membershiptype.title()

        for i in range(count):

            if not assign_membership_to_member(self.session, membershiptypename,
                    membershipname, self.member, parent=self.parent,
                    combobox=self.combobox):
                return False

        self.endInsertRows()

        return True

    def endRemoveRows(self):
        self.session.commit()
        self.internalDataRefresh()
        super().endRemoveRows()

    def endInsertRows(self):
        self.session.commit()
        self.internalDataRefresh()
        super().endInsertRows()

    def membershipDuration(self, membership):
        if not membership.startTime_fld:
            return "???"

        startyear = membership.startTime_fld.year
        if not membership.endTime_fld:
            return str(startyear) + " - nuvarande"

        endyear = membership.endTime_fld.year
        if startyear == endyear:
            return str(startyear)

        startmonth = membership.startTime_fld.month
        endmonth = membership.endTime_fld.month
        return "%d.%d - %d.%d" % (startmonth, startyear, endmonth, endyear)


    def configureAddMembershipQComboBox(self):
        # Membershiptype begins with upper-case character
        membershiptypetablename = self.membershiptype.title()
        configure_membership_qcombobox(self.combobox, membershiptypetablename,
                self.session)
        self.combobox.lineEdit().returnPressed.connect(lambda: self.insertRow(self.rowCount()))

class GroupListModel(MembershipListModel):
    def __init__(self, session, member, parent,
            add_membership_combobox=None):
        super().__init__(session, member, parent, "group",
                add_membership_combobox)

class PostListModel(MembershipListModel):
    def __init__(self, session, member, parent,
            add_membership_combobox):
        super().__init__(session, member, parent, "post",
                add_membership_combobox)

class DepartmentListModel(MembershipListModel):
    def __init__(self, session, member, parent,
            add_membership_combobox):
        super().__init__(session, member, parent, "department",
                add_membership_combobox)

class MembershipDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QDialog(parent=parent)
        editor.setModal(True)
        editor.ui = Ui_MembershipEdit()
        editor.ui.setupUi(editor)

        editor.ui.startYear_spinBox.setRange(datetime.MINYEAR, datetime.MAXYEAR)

        # Connect signals to slots.
        editor.ui.buttonBox.accepted.connect(lambda:
                (self.commitData.emit(editor),self.closeEditor.emit(editor,
                    QAbstractItemDelegate.NoHint)))
        editor.ui.buttonBox.rejected.connect(
                lambda: self.closeEditor.emit(editor,
                    QAbstractItemDelegate.NoHint))
        editor.ui.wholeyear_radioButton.toggled.connect(editor.ui.startYearWidget.setVisible)
        editor.ui.laborday_radioButton.toggled.connect(editor.ui.startYearWidget.setVisible)
        editor.ui.otherMandate_radioButton.toggled.connect(editor.ui.startAndEndTimeWidget.setVisible)

        return editor

    def setEditorData(self, editor, index):
        membership = index.data(Qt.EditRole)
        startdate = membership.startTime_fld.date()
        enddate = membership.endTime_fld.date()

        editor.ui.startYear_spinBox.setFocus()

        # Whole year mandate
        if (startdate.year == enddate.year and
                startdate == datetime.date(startdate.year, 1, 1) and
                enddate == datetime.date(startdate.year, 12, 31)):
            editor.ui.wholeyear_radioButton.toggle()
            editor.ui.startAndEndTimeWidget.hide()

        # Labor day to labor day mandate
        elif (startdate.year == (enddate.year - 1) and
                startdate == datetime.date(startdate.year, 5, 1) and
                enddate == datetime.date(startdate.year + 1, 4, 30)):
            editor.ui.laborday_radioButton.toggle()
            editor.ui.startAndEndTimeWidget.hide()

        # Other mandate
        else:
            editor.ui.otherMandate_radioButton.toggle()
            editor.ui.startYearWidget.hide()

        editor.ui.startYear_spinBox.setValue(membership.startTime_fld.year)
        editor.ui.startTime_fld.setDate(membership.startTime_fld)
        editor.ui.endTime_fld.setDate(membership.endTime_fld)

    def setModelData(self, editor, model, index):
        startyear = editor.ui.startYear_spinBox.value()

        starttime = None
        endtime = None

        if editor.ui.otherMandate_radioButton.isChecked():
            starttime = editor.ui.startTime_fld.dateTime().toPyDateTime()
            endtime = editor.ui.endTime_fld.dateTime().toPyDateTime()
            if endtime < starttime:
                endtime = starttime # Don't allow endtime before starttime

        elif editor.ui.laborday_radioButton.isChecked():
            starttime = datetime.datetime(startyear, 5, 1)
            endtime = datetime.datetime(startyear + 1, 4, 30)

        elif editor.ui.wholeyear_radioButton.isChecked():
            starttime = datetime.datetime(startyear, 1, 1)
            endtime = datetime.datetime(startyear, 12, 31)

        else: assert()

        model.setData(index, (starttime, endtime), Qt.EditRole)

    def eventFilter(self, editor, event):
        if event.type() == QEvent.KeyPress:
            # Undo Tab-key override in QStyledItemDelegate
            # pressing tab would otherwise close the editor.
            if event.key() == Qt.Key_Tab:
                return False
        if event.type() == QEvent.FocusOut:
            # Don't close editor when it looses focus.
            return False
        return super().eventFilter(editor, event)

# internal functions & classes
