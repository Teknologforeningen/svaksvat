#!/usr/bin/env python3
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
    combobox.addItem("Okänd")
    combobox.addItem("Man")
    combobox.addItem("Kvinna")

    if member and member.gender_fld:
        combobox.setCurrentIndex(member.gender_fld)

def fill_qlineedit_from_db(container, fieldname, table):
    """Fill QLineEdit with corresponding value from database and set the
    maximum length. Skip if fieldname not present in container or table"""
    try:
        getattr(container, fieldname).setText(getattr(table, fieldname))
        getattr(container, fieldname).setMaxLength(get_field_max_length(table,
            fieldname))
    except AttributeError:
        return

def update_qtextfield_to_db(container, fieldname, table):
    "Write the value of the textfield to database."
    try:
        setattr(table, fieldname, str(getattr(container, fieldname).text()))
    except AttributeError:
        return


class UsernameValidator(QValidator):
    def __init__(self, session, parent=None):
        super().__init__()
        self.parent = parent
        self.session = session

    def fixup(self, input):
        # Strip whitespace and special characters.
        return ''.join(c for c in input if c.isalnum())

    def validate(self, input, pos):
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
    def __init__(self, session, parent=None):
        self.parent = parent
        super().__init__()
        self.ui = Ui_NewMember()
        self.ui.setupUi(self)
        self.session = session
        self.setWindowTitle("Ny medlem")
        self.usernamevalidator = UsernameValidator(self.session, self)
        self.member = Member() # Needed in UsernameValidator
        self.ui.username_fld.setValidator(self.usernamevalidator)
        init_gender_combobox(self.ui.gender_fld)

        # Set correct lengths for QTextEdits
        for field in self.member.editable_text_fields:
            fill_qlineedit_from_db(self.ui, field, self.member)

        contactinfo = ContactInformation()
        for field in contactinfo.publicfields:
            fill_qlineedit_from_db(self.ui, field, contactinfo)

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
        self.member = self.session.query(Member).filter_by(objectId =
                member.objectId).one()

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
        groups = ["%s %d" % (groupmembership.group.name_fld,
            groupmembership.startTime_fld.year) for groupmembership in
                self.member.groupmemberships]
        self.ui.groupView.setModel(GroupListModel(self.session, self.member,
            self))
        self.ui.groupView.setItemDelegate(mshipdelegate)

        # Posts
        posts = ["%s %d" % (postmembership.post.name_fld,
                postmembership.startTime_fld.year)
                for postmembership in self.member.postmemberships]
        self.ui.postView.setModel(PostListModel(self.session, self.member,
            self))
        self.ui.postView.setItemDelegate(mshipdelegate)

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
        self.session = SessionMaker # Assuming scoped_session

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
        self.ui.searchfield.returnPressed.connect(self.ui.memberlistwidget.setFocus)
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

    def searchlist(self, pattern = ''):
        self.filteredmemberlist = [member for member in self.memberlist
                if member.getWholeName().upper().find(pattern.upper()) != -1]
        self.ui.memberlistwidget.clear()
        for member in self.filteredmemberlist:
            self.ui.memberlistwidget.addItem(member.getWholeName())

    def showMemberInfo(self, member=None):
        if not member:
            member = self.currentMember()
        contactinfo = member.contactinfo
        memberinfo = ( """Namn: %s %s
Address: %s %s %s %s
Telefon: %s
Mobiltelefon: %s
Email: %s
Användarnamn: %s
"""
        %   (
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
