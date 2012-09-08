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
        MembershipDelegate)
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
        """Strip whitespace and special characters."""
        return ''.join(c for c in input if c.isalnum())

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


class NewMemberDialog(QWidget):
    """A dialog to create a new member to the registry."""
    def __init__(self, session, parent=None):
        self.parent = parent
        super().__init__()
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

        self.session.commit()
        self.parent.populateMemberList(choosemember=member)
        self.close()

    def reject(self):
        self.close()


class MemberEdit(QWidget):
    def __init__(self, session, member, parent=None):
        self.parent = parent
        super().__init__()
        self.ui = Ui_MemberEdit()
        self.ui.setupUi(self)
        self.ui.createLDAPAccount.connect(
                self.ui.createLDAPAccount,
                SIGNAL("clicked()"),
                self.createAccount
                )

        self.session = session
        self.member = self.session.query(Member).filter_by(
                objectId=member.objectId).one()

        self.fillFields()
        self.setWindowTitle(self.member.getWholeName())
        self.usernamevalidator = UsernameValidator(self.session,
                self)
        self.ui.username_fld.setValidator(self.usernamevalidator)

    def fillFields(self):
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

    def removeSelectedMembership(self, listview):
        selections = listview.selectedIndexes()
        for index in selections:
            listview.model().removeRow(index.row())

    def createAccount(self):
        if not self.member.username_fld:
            print("No username field")
            return

    def accept(self):
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
        self.parent.setStatusMessage("Medlem %s skapad!" %
                self.member.getWholeName())
        self.close()

    def reject(self):
        self.close()


class SvakSvat(QMainWindow):
    def __init__(self, SessionMaker):
        super().__init__()
        self.session = SessionMaker  # Assuming scoped_session

        self.initUI()
        self.setStatusMessage("Redo!", 3000)

    def initUI(self):
        vbox = QVBoxLayout()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Connect signals to slots.
        self.ui.searchfield.textChanged.connect(self.searchlist)
        self.ui.memberlistwidget.currentRowChanged.connect(lambda:
                self.showMemberInfo())
        self.ui.memberlistwidget.itemActivated.connect(self.editMember)
        self.ui.searchfield.returnPressed.connect(
                self.ui.memberlistwidget.setFocus)
        self.ui.actionNewMember.triggered.connect(lambda:
                NewMemberDialog(self.session, self))
        self.ui.actionRemoveMember.triggered.connect(self.removeMember)
        self.ui.actionEditMember.triggered.connect(self.editMember)

        self.ui.memberlistwidget.addAction(self.ui.actionEditMember)
        self.ui.memberlistwidget.addAction(self.ui.actionRemoveMember)
        self.ui.memberlistwidget.setContextMenuPolicy(Qt.ActionsContextMenu)

        self.populateMemberList()

        self.setWindowTitle('SvakSvat')

    def removeMember(self):
        member = self.currentMember()
        wholename = member.getWholeName()
        self.session.delete(member)
        self.session.commit()
        self.populateMemberList()
        self.setStatusMessage("Användare %s borttagen!" % wholename)

    def populateMemberList(self, choosemember=None):
        self.memberlist = self.session.query(Member).order_by(
                Member.surName_fld).all()
        self.ui.searchfield.clear()
        self.searchlist()
        if choosemember:
            memberindex = self.memberlist.index(choosemember)
            self.ui.memberlistwidget.setCurrentRow(memberindex)

    def currentMember(self):
        member = self.filteredmemberlist[self.ui.memberlistwidget.currentRow()]
        return member

    def editMember(self):
        member = self.currentMember()
        self.membereditwidget = MemberEdit(self.session, member, self)
        self.membereditwidget.show()

    def searchlist(self, pattern=''):
        self.filteredmemberlist = [member for member in self.memberlist
                if member.getWholeName().upper().find(pattern.upper()) != -1]
        self.ui.memberlistwidget.clear()
        for member in self.filteredmemberlist:
            self.ui.memberlistwidget.addItem(member.getWholeName())

    def showMemberInfo(self, member=None):
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
        currentposts = [postmembership.post.name_fld for postmembership in
                member.postmemberships if postmembership.isCurrent()]
        currentgroups = [groupmembership.group.name_fld for groupmembership in
                member.groupmemberships if groupmembership.isCurrent()]

        return ("\n".join(["\nPoster:"] + currentposts) +
                "\n".join(["\n\nGrupper:"] + currentgroups))

    def setStatusMessage(self, message, milliseconds=3000):
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
