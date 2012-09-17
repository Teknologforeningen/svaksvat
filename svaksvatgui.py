#!/usr/bin/env python3
"""SvakSvat Member register GUI."""
import sys
import os
import subprocess
import datetime

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from sqlalchemy.orm import scoped_session

from backend import connect
from backend.orm import (Member, ContactInformation, get_field_max_length,
        create_member, create_phux)
from backend.listmodels import (GroupListModel, PostListModel,
        DepartmentListModel, MembershipListModel, MembershipDelegate,
        configure_membership_qcombobox, assign_membership_to_member)

from ui.mainwindow import Ui_MainWindow
from ui.memberedit import Ui_MemberEdit
from ui.newmember import Ui_NewMember

import passwordsafe


def init_gender_combobox(combobox, member=None):
    """Initializes a QComboBox to gender_fld.

    Inserts the possible gender names in the database and assigns the
    combobox's current value to the given member's gender_fld value.

    combobox -- The QComboBox to be initialized.
    member -- A backend.orm.Member whose gender_fld gets assigned to the
    combobox

    """
    combobox.addItem("Okänd")
    combobox.addItem("Man")
    combobox.addItem("Kvinna")

    if member and member.gender_fld:
        combobox.setCurrentIndex(member.gender_fld)


def fill_qlineedit_from_db(lineedit, fieldname, table):
    """Initialize QLineEdit from a ORM-mapped table.

    lineedit -- QLineEdit or similar. setText and setMaxLength methods used.
    fieldname -- Table's column name. Ie. givenNames_fld.
    table -- ORM-mapping for database table Ie. Member or ContactInformation.

    Fills the container with corresponding value from the database table field
    of string type and sets the maximum length. Skip if fieldname not present
    in container or table.

    Use update_qtextfield_to_db to bring the changes back to database.

    """
    try:
        getattr(lineedit, fieldname).setText(getattr(table, fieldname))
        getattr(lineedit, fieldname).setMaxLength(get_field_max_length(table,
            fieldname))

    except AttributeError:
        return


def update_qtextfield_to_db(container, fieldname, table):
    """Write the text from a container to database table.

    container -- needs to have text()-method
    fieldname -- Table's column name. Ie. givenNames_fld.
    table -- ORM-mapping for database table Ie. Member or ContactInformation.

    """
    try:
        setattr(table, fieldname, str(getattr(container, fieldname).text()))
    except AttributeError:
        return


class UsernameValidator(QValidator):
    """Validates LDAP-usernames in QTextFields.

    Makes sure that no other Member has the same username_fld in the database.

    """
    def __init__(self, session, parent):
        """Construct the validator with given session and parent.

        session -- Sqlalchemy session.
        parent -- Parent including "member" and ui.username_fld members.

        The MemberEdit and NewMemberDialog classes are designed to be parent
        parameters.
        """

        super().__init__()
        self.parent = parent
        self.session = session

    def fixup(self, input):
        """Strip whitespace + special characters and make lower case"""
        return ''.join(c.lower() for c in input if c.isalnum())

    def validate(self, input, pos):
        """Checks for username uniqueness."""
        stripped = self.fixup(input)
        not_unique = self.session.query(Member).filter(Member.username_fld ==
                stripped).filter(Member.objectId !=
                        self.parent.member.objectId).count()
        if not_unique:
            self.parent.ui.username_fld.setStyleSheet("QLineEdit {\
                background-color: rgb(255, 100, 100); }")
            return (QValidator.Intermediate, stripped, pos)

        else:
            self.parent.ui.username_fld.setStyleSheet("QLineEdit {\
                background-color: rgb(255, 255, 255); }")
            return (QValidator.Acceptable, stripped, pos)

class NewMemberDialog(QDialog):
    def __init__(self, session, parent=None):
        """Create the dialog and initialize the fields.

        session -- Sqlalchemy session.
        parent -- Parent for the QDialog.
        """
        self.parent = parent
        super().__init__(parent=self.parent)
        self.ui = Ui_NewMember()
        self.ui.setupUi(self)
        self.session = session
        self.setWindowTitle("Ny medlem")
        self.usernamevalidator = UsernameValidator(self.session, self)
        self.member = Member()  # Needed in UsernameValidator
        self.ui.username_fld.setValidator(self.usernamevalidator)
        init_gender_combobox(self.ui.gender_fld)

        # Set correct lengths for QTextEdits
        for field in self.member.editable_text_fields:
            fill_qlineedit_from_db(self.ui, field, self.member)

        contactinfo = ContactInformation()
        for field in contactinfo.publicfields:
            fill_qlineedit_from_db(self.ui, field, contactinfo)

        if self.member.birthDate_fld:
            self.ui.birthDate_fld.setDateTime(self.member.birthDate_fld)

        self.show()

    def accept(self):
        """Commit the new member to the database."""
        member = None
        if self.ui.makePhux_CheckBox.isChecked():
            member = create_phux(self.session)

        else:
            member = create_member(self.session)

        for field in Member.editable_text_fields:
            if (field == "username_fld" and not
                    self.ui.username_fld.hasAcceptableInput()):
                continue

            update_qtextfield_to_db(self.ui, field, member)

        self.member.gender_fld = self.ui.gender_fld.currentIndex()
        self.member.birthDate_fld = self.ui.birthDate_fld.dateTime(
                ).toPyDateTime()

        contactinfo = member.contactinfo
        for field in contactinfo.publicfields:
            update_qtextfield_to_db(self.ui, field, contactinfo)

        if not assign_membership_to_member(self.session, "Department",
                self.ui.department_comboBox.currentText(), member, parent=self,
                combobox=self.ui.department_comboBox, indefinite_time=True):
            return # Don't yet commit if Department not chosen.

        self.session.commit()
        self.parent.populateMemberList(choosemember=member)
        self.parent.setStatusMessage("Medlem %s skapad!" %
                member.getWholeName())
        super().accept()

    def reject(self):
        """Close the dialog without saving any changes."""
        super().reject()


class MemberEdit(QWidget):
    """Dialog to edit almost every aspect of a member."""
    def __init__(self, session, member, parent=None):
        """Create the dialog and fill in the values from a member.

        session -- Sqlalchemy session.
        member -- backend.orm.Member to be edited.
        parent -- Parent for the QDialog

        """
        self.parent = parent
        super().__init__()
        self.ui = Ui_MemberEdit()
        self.ui.setupUi(self)
        self.session = session
        self.member = self.session.query(Member).filter_by(
                objectId=member.objectId).one()

        self.fillFields()
        self.setWindowTitle(self.member.getWholeName())

        self.usernamevalidator = UsernameValidator(self.session,
                self)
        self.ui.username_fld.setValidator(self.usernamevalidator)

    def fillFields(self):
        """Fill every widget with the corresponding values of a Member."""
        for field in Member.editable_text_fields:
            fill_qlineedit_from_db(self.ui, field, self.member)

        self.ui.notes_fld.setPlainText(self.member.notes_fld)
        self.ui.dead_fld.setChecked(bool(self.member.dead_fld))
        if self.member.birthDate_fld:
            self.ui.birthDate_fld.setDateTime(self.member.birthDate_fld)
        self.ui.subscribedToModulen_fld_checkbox.setChecked(
                bool(self.member.subscribedtomodulen_fld))

        init_gender_combobox(self.ui.gender_fld, self.member)

        # Contact information
        contactinfo = self.member.contactinfo
        for field in contactinfo.publicfields:
            fill_qlineedit_from_db(self.ui, field, contactinfo)

        mshipdelegate = MembershipDelegate()

        # Groups
        grouplistmodel = GroupListModel(self.session, self.member, self,
                self.ui.group_comboBox)
        self.ui.groupView.setModel(grouplistmodel)
        self.ui.groupView.setItemDelegate(mshipdelegate)
        self.ui.removeGroupButton.clicked.connect(lambda:
                self.removeSelectedMembership(self.ui.groupView))
        grouplistmodel.rowsInserted.connect(lambda index, row:
                    self.ui.groupView.edit(grouplistmodel.index(row)))

        # Posts
        postlistmodel = PostListModel(self.session, self.member, self,
                self.ui.post_comboBox)
        self.ui.postView.setModel(postlistmodel)
        self.ui.removePostButton.clicked.connect(lambda:
                self.removeSelectedMembership(self.ui.postView))
        self.ui.postView.setItemDelegate(mshipdelegate)
        postlistmodel.rowsInserted.connect(lambda index, row:
                self.ui.postView.edit(postlistmodel.index(row)))

        # Departments
        departmentlistmodel = DepartmentListModel(self.session, self.member, self,
                self.ui.department_comboBox)
        self.ui.departmentView.setModel(departmentlistmodel)
        self.ui.removeDepartmentButton.clicked.connect(lambda:
                self.removeSelectedMembership(self.ui.departmentView))
        self.ui.departmentView.setItemDelegate(mshipdelegate)

        # Memberships
        membershiplistmodel = MembershipListModel(self.session, self.member,
                self, None)
        self.ui.membershipView.setModel(membershiplistmodel)
        self.ui.removeMembershipButton.clicked.connect(lambda:
                self.removeSelectedMembership(self.ui.membershipView))
        self.ui.membershipView.setItemDelegate(mshipdelegate)

    def removeSelectedMembership(self, listview):
        """Remove selected items from a QListView."""
        selections = listview.selectedIndexes()
        for index in selections:
            listview.model().removeRow(index.row())

    def createAccount(self):
        if not self.member.username_fld:
            print("No username field")
            return

    def accept(self):
        """Commit Member.*_fld and contactinfo.*_fld changes to database.

        Most notably all the QListView changes are already committed.

        """

        for field in Member.editable_text_fields:
            if (field == "username_fld" and not
                    self.ui.username_fld.hasAcceptableInput()):
                continue

            update_qtextfield_to_db(self.ui, field, self.member)

        self.member.notes_fld = str(self.ui.notes_fld.toPlainText()[:255])

        self.member.gender_fld = self.ui.gender_fld.currentIndex()
        date = self.ui.birthDate_fld.dateTime().date()

        self.member.birthDate_fld = self.ui.birthDate_fld.dateTime(
                ).toPyDateTime()

        self.member.dead_fld = int(self.ui.dead_fld.isChecked())

        self.member.subscribedtomodulen_fld = int(
                self.ui.subscribedToModulen_fld_checkbox.isChecked())

        contactinfo = self.member.contactinfo

        for field in contactinfo.publicfields:
            update_qtextfield_to_db(self.ui, field, contactinfo)

        self.session.commit()
        self.parent.populateMemberList(choosemember=self.member)
        super().accept()

    def reject(self):
        """Close the dialog without saving the fields to the database."""
        #TODO: Also rollback the MembershipListView changes.
        self.session.rollback()
        super().reject()


class SvakSvat(QMainWindow):
    """Member Registry Application."""
    def __init__(self, session):
        """Create the window.

        session -- Sqlalchemy scoped_session.

        """
        super().__init__()
        self.session = session  # Assuming scoped_session

        self.initUI()
        self.setStatusMessage("Redo!", 3000)

    def initUI(self):
        """Create the window and connect the Qt signals to slots"""
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Connect signals to slots.
        self.ui.searchfield.textChanged.connect(self.searchlist)
        self.ui.memberlistwidget.currentRowChanged.connect(lambda:
                self.showMemberInfo())
        self.ui.memberlistwidget.itemActivated.connect(self.editMember)
        self.ui.searchfield.returnPressed.connect(self.ui.memberlistwidget.setFocus)
        self.ui.actionNewMember.triggered.connect(self.createMember)
        self.ui.actionRemoveMember.triggered.connect(self.removeMember)
        self.ui.actionEditMember.triggered.connect(self.editMember)

        self.ui.memberlistwidget.addAction(self.ui.actionEditMember)
        self.ui.memberlistwidget.addAction(self.ui.actionRemoveMember)
        self.ui.memberlistwidget.setContextMenuPolicy(Qt.ActionsContextMenu)

        self.populateMemberList()

        self.setWindowTitle('SvakSvat')

    def createMember(self):
        newmemberdialog = NewMemberDialog(self.session, self)
        newmemberdialog.exec()

    def removeMember(self):
        """Remove selected member."""
        member = self.currentMember()
        wholename = member.getWholeName()
        self.session.delete(member)
        self.session.commit()
        self.populateMemberList()
        self.setStatusMessage("Användare %s borttagen!" % wholename)

    def populateMemberList(self, choosemember=None):
        """Fill the memberlist from the database."""
        self.memberlist = self.session.query(Member).order_by(
                Member.surName_fld).all()
        self.ui.searchfield.clear()
        self.searchlist()
        if choosemember:
            memberindex = self.memberlist.index(choosemember)
            self.ui.memberlistwidget.setCurrentRow(memberindex)

    def currentMember(self):
        """Returns the currently selected member."""
        member = self.filteredmemberlist[self.ui.memberlistwidget.currentRow()]
        return member

    def editMember(self):
        """Edit the currently selected member."""
        member = self.currentMember()
        self.membereditwidget = MemberEdit(self.session, member, self)
        self.membereditwidget.show()

    def searchlist(self, pattern=''):
        """Perform a filter operation on the memberlist.

        pattern -- The string to match.

        """
        self.filteredmemberlist = [member for member in self.memberlist
                if member.getWholeName().upper().find(pattern.upper()) != -1]
        self.ui.memberlistwidget.clear()
        for member in self.filteredmemberlist:
            self.ui.memberlistwidget.addItem(member.getWholeName())

    def showMemberInfo(self, member=None):
        """Show the member's info in the panel below.

        member -- backend.orm.Member to show.
        """
        if not member:
            member = self.currentMember()
        contactinfo = member.contactinfo
        memberinfo = """Namn: %s %s
Address: %s %s %s %s
Telefon: %s
Mobiltelefon: %s
Email: %s
Användarnamn: %s
""" % (
            member.givenNames_fld,
            member.surName_fld,
            contactinfo.streetAddress_fld,
            contactinfo.postalCode_fld,
            contactinfo.city_fld,
            contactinfo.country_fld,
            contactinfo.phone_fld,
            contactinfo.cellPhone_fld,
            contactinfo.email_fld,
            member.username_fld
            )

        membershipinfo = self.getMembershipInfo(member)
        self.ui.memberinfo.setText(memberinfo + membershipinfo)

    def getMembershipInfo(self, member):
        """Get the current membershipinfo for a member.

        member -- backend.orm.Member

        Used in showMemberInfo"""
        currentposts = [postmembership.post.name_fld for postmembership in
                member.postmemberships if postmembership.isCurrent()]
        currentgroups = [groupmembership.group.name_fld for groupmembership in
                member.groupmemberships if groupmembership.isCurrent()]

        return ("\n".join(["\nPoster:"] + currentposts) +
                "\n".join(["\n\nGrupper:"] + currentgroups))

    def setStatusMessage(self, message, milliseconds=3000):
        """Sets a status message in the MainWindow.

        message -- The status message to set.
        milliseconds -- The lifetime of the message.

        """
        self.ui.statusbar.showMessage(message, milliseconds)


def main():
    ps = passwordsafe.PasswordSafe()
    SessionMaker = scoped_session(ps.connect_with_config("memberslocalhost"))
    app = QApplication(sys.argv)
    sr = SvakSvat(SessionMaker)
    sr.show()
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())
