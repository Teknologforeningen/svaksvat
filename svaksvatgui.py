#!/usr/bin/env python3
import sys
import os
import subprocess
import datetime

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from sqlalchemy.orm import scoped_session

from backend import connect
from backend.orm import Member, get_field_max_length
from backend.listmodels import MembershipListModel

from memberedit import Ui_Dialog

import passwordsafe

class UsernameValidator(QValidator):
    def __init__(self, session, parent=None):
        super(UsernameValidator, self).__init__()
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

class MemberEdit(QWidget):
    def __init__(self, session=None, member=None):
        super(MemberEdit, self).__init__()
        self.ui = Ui_Dialog()
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

    def fillLineEditFromDB(self, fieldname, row=None):
        """Fill LineEdit with corresponding value from database and set the
        maximum length."""
        if row is None:
            row = self.member
        getattr(self.ui, fieldname).setText(getattr(row, fieldname))
        getattr(self.ui, fieldname).setMaxLength(get_field_max_length(row,
            fieldname))

    def fillFields(self):
        self.fillLineEditFromDB("username_fld")
        self.fillLineEditFromDB("givenNames_fld")
        self.fillLineEditFromDB("surName_fld")
        self.fillLineEditFromDB("preferredName_fld")
        self.fillLineEditFromDB("maidenName_fld")
        self.fillLineEditFromDB("studentId_fld")
        self.fillLineEditFromDB("nationality_fld")

        self.ui.notes_fld.setPlainText(self.member.notes_fld)

        self.ui.dead_fld.setChecked(bool(self.member.dead_fld))
        if self.member.birthDate_fld:
            self.ui.birthDate_fld.setDateTime(self.member.birthDate_fld)
        self.ui.subscribedToModulen_fld_checkbox.setChecked(
                bool(self.member.subscribedtomodulen_fld))
        self.ui.gender_fld.addItem("Okänd")
        self.ui.gender_fld.addItem("Man")
        self.ui.gender_fld.addItem("Kvinna")
        if self.member.gender_fld:
            self.ui.gender_fld.setCurrentIndex(self.member.gender_fld)

        # Contact information
        contactinfo = self.member.contactinfo
        self.fillLineEditFromDB("streetAddress_fld", row=contactinfo)
        self.fillLineEditFromDB("postalCode_fld", row=contactinfo)
        self.fillLineEditFromDB("city_fld", row=contactinfo)
        self.fillLineEditFromDB("country_fld", row=contactinfo)
        self.fillLineEditFromDB("phone_fld", row=contactinfo)
        self.fillLineEditFromDB("email_fld", row=contactinfo)

        # Groups
        groups = ["%s %d" % (groupmembership.group.name_fld,
            groupmembership.startTime_fld.year) for groupmembership in
                self.member.groupmemberships]
        self.ui.groupView.setModel(MembershipListModel(self.session,
            self.member, self))

        # Posts
        posts = ["%s %d" % (postmembership.post.name_fld,
                postmembership.startTime_fld.year)
                for postmembership in self.member.postmemberships]
        #self.ui.postView.setModel(ListModelCommon(self.session, self))

    def createAccount(self):
        if not self.member.username_fld:
            print("No username field")
            return

    def updateTextFieldToDB(self, fieldname, row=None):
        "Write the value of the textfield to database."
        if row is None:
            row = self.member

        setattr(row, fieldname, str(getattr(self.ui, fieldname).text()))


    def accept(self):
        if self.ui.username_fld.hasAcceptableInput():
            self.updateTextFieldToDB("username_fld")
        self.updateTextFieldToDB("givenNames_fld")
        self.updateTextFieldToDB("surName_fld")
        self.updateTextFieldToDB("preferredName_fld")
        self.updateTextFieldToDB("maidenName_fld")
        self.updateTextFieldToDB("studentId_fld")
        self.updateTextFieldToDB("nationality_fld")

        self.member.notes_fld = str(self.ui.notes_fld.toPlainText()[:255])

        self.member.gender_fld = self.ui.gender_fld.currentIndex()
        date = self.ui.birthDate_fld.dateTime().date()
        self.member.birthDate_fld = datetime.datetime(date.year(), date.month(),
                date.day())

        self.member.dead_fld = int(self.ui.dead_fld.isChecked())

        self.member.subscribedtomodulen_fld = int(
                self.ui.subscribedToModulen_fld_checkbox.isChecked())

        contactinfo = self.member.contactinfo
        self.updateTextFieldToDB("streetAddress_fld", row=contactinfo)
        self.updateTextFieldToDB("postalCode_fld", row=contactinfo)
        self.updateTextFieldToDB("city_fld", row=contactinfo)
        self.updateTextFieldToDB("country_fld", row=contactinfo)
        self.updateTextFieldToDB("phone_fld", row=contactinfo)
        self.updateTextFieldToDB("email_fld", row=contactinfo)

        self.session.commit()
        self.close()

    def reject(self):
        self.close()


class SimpleRegister(QWidget):
    def __init__(self, SessionMaker):
        super(SimpleRegister, self).__init__()

        self.session = SessionMaker # Assuming scoped_session

        self.initUI()

    def initUI(self):
        vbox = QVBoxLayout()
        self.searchfield = QLineEdit(self)
        self.searchfield.textChanged.connect(self.searchlist)
        self.memberlistwidget = QListWidget(self)
        self.memberinfo = QTextEdit(self)
        self.memberinfo.setReadOnly(True)
        self.memberlistwidget.itemClicked.connect(self.showMemberInfo)
        self.memberlistwidget.itemActivated.connect(self.editMember)
        self.searchfield.returnPressed.connect(self.memberlistwidget.setFocus)

        # Populate list.
        self.memberlist = self.session.query(Member).order_by(
                Member.surName_fld).all()

        self.searchlist()
        vbox.addWidget(self.searchfield)
        vbox.addWidget(self.memberlistwidget)
        vbox.addWidget(self.memberinfo)
        self.setLayout(vbox)
        self.setWindowTitle('SimpleRegister')

    def editMember(self, membername):
        member = self.filteredmemberlist[self.memberlistwidget.currentRow()]
        self.membereditwidget = MemberEdit(self.session, member)
        self.membereditwidget.show()

    def searchlist(self, pattern = ''):
        self.filteredmemberlist = [member for member in self.memberlist
                if member.getWholeName().upper().find(pattern.upper()) != -1]
        self.memberlistwidget.clear()
        for member in self.filteredmemberlist:
            self.memberlistwidget.addItem(member.getWholeName())

    def showMemberInfo(self, membername):
        member = self.filteredmemberlist[self.memberlistwidget.currentRow()]
        memberID = member.objectId
        contactinfo = self.session.query(Member).filter_by(
                objectId = memberID).one().contactinfo
        memberinfo = (
        """
Namn: %s %s
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
        self.memberinfo.setText(memberinfo + membershipinfo)

    def getMembershipInfo(self, member):
        currentposts = [postmembership.post.name_fld for postmembership in
                member.postmemberships if postmembership.isCurrent()]
        currentgroups = [groupmembership.group.name_fld for groupmembership in
                member.groupmemberships if groupmembership.isCurrent()]

        return ("\n".join(["\nPoster:"] + currentposts) +
                "\n".join(["\n\nGrupper:"] + currentgroups))

def main():
    ps = passwordsafe.PasswordSafe()
    SessionMaker = scoped_session(ps.connect_with_config("mimer"))
    app = QApplication(sys.argv)
    sr = SimpleRegister(SessionMaker)
    sr.show()
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())
