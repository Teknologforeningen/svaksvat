#!/usr/bin/env python3
"""LDAP utilities integrated with the member register."""

# imports
import io
import shlex
from subprocess import (Popen, call, PIPE, STDOUT, check_output,
        CalledProcessError)
import base64
import string
import sys
import os
import datetime
import argparse

import sqlalchemy

from random import randint

sys.path.append(os.path.dirname(os.getcwd()))  # Add .. to path
from backend.ldaplogin import (get_member_with_real_name,
        DuplicateNamesException, PersonNotFoundException)
from backend import connect
from backend.orm import *
from backend.commonutils import which

import passwordsafe

# constants
# exception classes
# interface functions
# classes
# internal functions & classes

"""
addldapuser(Member):
    if username in ldap:
        fail

    get next free uid
    generate password

    add ldap user with data from medlemsregister
    base64 encode if necessary

    add username to group medlem in ldap

    check for error in ldapmodify

    sleep 3

    make home directory

    insert bill account

delldapuser(Member):
    if username not in ldap:
        fail

    del ldap user from ldap
    del username from group medlem

    del home directory

    # do not del bill account because money is involved


"""


def encode_base64_ondemand(s):
    """
    Decode string to base64 if it isn't ascii. Also put leading ': ' so that LDAP
    knows the string is b64 encoded.

    >>> encode_base64_ondemand("Hej")
    ' Hej'
    >>> encode_base64_ondemand("Höj")
    ": SMO2ag=="
    """
    if not all(c in string.ascii_letters for c in s): # String not ASCII
        s = ": " + base64.b64encode(s.encode()).decode()
    else:
        s = " " + s
    return s


class LDAPAccountManager:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run

        self.ldapmodifypath = which("ldapmodify")
        self.ldapsearchpath = which("ldapsearch")
        self.ldappasswdpath = which("ldappasswd")
        self.ldapdeletepath = which("ldapdelete")

        self.ps = passwordsafe.PasswordSafe(enablegui=True)
        self.ldaphost = self.ps.get_config_value("ldap", "host")
        auth, self.servicelogin, self.servicepassword = self.ps.askcredentials(
                self.check_ldap_login, "ldap", "servicelogin")

        SessionMaker = self.ps.connect_with_config("pykota")
        self.pykotasession = SessionMaker()

        self.LDAPMODIFY_CMD = shlex.split("""%s -h \
            %s -xD cn=%s,dc=teknologforeningen,dc=fi -w %s""" % (self.ldapmodifypath,
                self.ldaphost, self.servicelogin, self.servicepassword))

    def check_bill_account(self, member):
        if member.username_fld:
            return bool(self.pykotasession.execute(
            "select * from users where username='%s'" %
            member.username_fld).rowcount)

        return False

    def get_bill_balance(self, member):
        try:
            return self.pykotasession.execute(
                "select balance from users where username='%s';" %
                member.username_fld).fetchone()['balance']
        except:
            return None

    def get_bill_code(self, member):
        try:
            return "".joint(self.pykotasession.execute(
                "select id, pin from users where username='%s';" %
                member.username_fld).fetchone()[:])

        except:
            return None

    def ldapsearch(self, query):
        """"Execute ldapsearch command with saved credentials."""
        return self.ldapsearch_with_credentials(self.servicelogin, self.servicepassword, query)

    def ldapsearch_with_credentials(self, username, password, query):
        """"Execute ldapsearch command."""
        ldapquery = shlex.split("""%s -h %s\
                -b dc=fi -D cn=%s,dc=teknologforeningen,dc=fi -w\
                %s %s""" % (self.ldapsearchpath, self.ldaphost, username, password, query))

        return check_output(ldapquery, universal_newlines=True)

    def check_ldap_login(self, username, password):
        """Determine if LDAP credentials have sufficient privileges

        Done by searching for ServiceUser, if userPassword is shown the
        credentials have privileges."""
        try:
            output = self.ldapsearch_with_credentials(username, password, "cn=ServiceUser")
        except CalledProcessError:
            return False
        return "\nuserPassword:: " in output

    def generate_ldifs(self, member, uidnumber, passwd):
        """Generates the strings needed to create the ldap user."""
        username = member.username_fld
        preferredname = member.preferredName_fld
        name = member.getName()
        surname = member.surName_fld
        email = member.contactinfo.email_fld

        if not all([username, preferredname, name, surname, email]):
            return None, None

        # LDIF used to create the user account.
        userldif = """
dn: uid=%s,ou=People,dc=teknologforeningen,dc=fi
changetype: add
uid: %s
cn: %s
homeDirectory: /rhome/%s
uidNumber: %d
mailHost: smtp.ayy.fi
gidNumber: 1000
sn: %s
givenName: %s
loginShell: /bin/bash
objectClass: kerberosSecurityObject
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: shadowAccount
objectClass: inetLocalMailRecipient
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: billAccount
krbName: %s
mail: %s
userPassword: %s
        """ % (username, username, name, username,
                uidnumber, surname, preferredname, username, email, passwd)

        # LDIF used to add the user to the medlem group.
        usergroupldif = """
dn: cn=medlem,ou=Group,dc=teknologforeningen,dc=fi
changetype: modify
add: memberUid
memberUid: %s
    """ % username

        return userldif, usergroupldif

    def get_next_uidnumber(self):
        """Returns the next free uidnumber greater than 1000"""

        output = self.ldapsearch("uidNumber")
        uidnumbers = [int(line.split(": ")[1]) for line in output.splitlines() if
                      "uidNumber: " in line]
        uidnumbers.sort()

        # Find first free uid over 1000.
        last = 1000
        for uid in uidnumbers:
            if uid > last + 1:
                break
            last = uid
        return last + 1

    def checkldapuser(self, member):
        if not member.username_fld:
            return False

        output = self.ldapsearch("uid=" + member.username_fld)

        return "\n# numEntries: 1" in output

    def getPosixGroups(self, member):
        output = self.ldapsearch(
            "(&(objectClass=posixGroup)(memberUid=%s))" %
            member.username_fld)

        groups = [line.split(": ")[1] for line in output.splitlines() if "cn: " in line]
        return groups

    def delldapuser(self, member):
        if not member.username_fld:
            return

        # Delete LDAP user account
        delusercmd = shlex.split("""%s -h \
                %s -xD  cn=%s,dc=teknologforeningen,dc=fi -w \
                %s uid=%s,ou=People,dc=teknologforeningen,dc=fi""" % (

                    self.ldapdeletepath, self.ldaphost, self.servicelogin,
                    self.servicepassword, member.username_fld))

        if self.dry_run:
            delusercmd.append("-n")

        check_output(delusercmd)
        print("User %s deleted." % member.username_fld)

        # Delete user from Members group
        deluserfromgroupldif = """
dn: cn=medlem,ou=Group,dc=teknologforeningen,dc=fi
changetype: modify
delete: memberUid
memberUid: """ + member.username_fld
        cmd = self.LDAPMODIFY_CMD
        groupmodproc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        out = groupmodproc.communicate(input=deluserfromgroupldif.encode())
        print(out[0].decode())

        return True

    def change_ldap_password(self, username, newpassword):
        """Change password for user account."""
        changepwcommand = shlex.split("""%s -h %s -D \
                cn=%s,dc=teknologforeningen,dc=fi -w %s -s %s \
                uid=%s,ou=People,dc=teknologforeningen,dc=fi""" %
                (self.ldappasswdpath, self.ldaphost, self.servicelogin, self.servicepassword,
                    newpassword, username))

        check_output(changepwcommand, universal_newlines=True)
        print("New password set for user %s." % username)


    def create_bill_account(self, member):
        """Create BILL account and return BILL-code."""
        if not member.username_fld:
            return False
        username = member.username_fld

        self.pykotasession.execute(
            "INSERT INTO users(username, name, pin) VALUES('%s', '%s',\
                '%s');" % (username,
                           member.getName(), str(randint(1000, 9999))))

        self.pykotasession.execute(
            "INSERT INTO userpquota(userid,printerid,balancelimit) \
                SELECT (SELECT id FROM users WHERE username='%s'\
                ),id,deflimit_u FROM printers WHERE defactivate_u='t';" %
            username)

        self.pykotasession.commit()

        return self.get_bill_code(member)

    def addldapuser(self, member, passwd):
        uidnumber = self.get_next_uidnumber()
        userldif, usergroupldif = self.generate_ldifs(
            member, uidnumber, passwd)

        if not userldif:  # Something is missing in member.
            return False

        # Add the user to LDAP
        cmd = self.LDAPMODIFY_CMD
        if self.dry_run:
            cmd.append("-n")

        adduserproc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        out1 = adduserproc.communicate(input=userldif.encode())
        print(out1[0].decode())

        # Workaround because password setting with ldif doesn't work.
        if not self.dry_run:
            self.change_ldap_password(member.username_fld, passwd)

        if self.checkldapuser(member):  # if user add successful
            # Add the user to Members-group
            groupmodproc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
            out2 = groupmodproc.communicate(input=usergroupldif.encode())
            print(out2[0].decode())

            if not self.check_bill_account(member):
                # Create BILL-account if it does not exist.
                self.create_bill_account(member)

            return True

        return False


def main():
    member = Member()
    member.username_fld = "test123"
    member.preferredName_fld = "John"
    member.surName_fld = "Döe"
    member.contactinfo = ContactInformation()
    member.contactinfo.email_fld = "john.doe@test.net"
    lm = LDAPAccountManager()
    output = lm.ldapsearch("uid=test123")
    passwd= "hunter2"
    print(lm.getPosixGroups(member))
    if lm.addldapuser(member, passwd) and lm.checkldapuser(member):
        ...
        #lm.delldapuser(member)
    print(lm.checkldapuser(member))
    return 0

if __name__ == '__main__':
    status = main()
    sys.exit(status)
