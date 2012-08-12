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

sys.path.append(os.path.dirname(os.getcwd()))  # Add .. to path
from backend.ldaplogin import (get_member_with_real_name,
        DuplicateNamesException, PersonNotFoundException)
from backend import connect
from backend.orm import *
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

        self.ps = passwordsafe.PasswordSafe()
        self.ps.askcredentials(self.check_ldap_login, "ldap",
                "servicelogin")


    def ldapsearch(self, ldaphost, username, password, query):
        """"Execute ldapsearch command."""
        ldapquery = shlex.split("""ldapsearch -h %s\
                -b dc=fi -D cn=%s,dc=teknologforeningen,dc=fi -w\
                %s %s""" % (ldaphost, username, password, query))
        return check_output(ldapquery, universal_newlines=True)

    def check_ldap_login(self, username, password):
        """Determine if LDAP credentials have sufficient privileges

        Done by searching for ServiceUser, if userPassword is shown the
        credentials have privileges."""
        ldaphost = self.ps.get_config_value("ldap", "host")
        try:
            output = self.ldapsearch(ldaphost, username, password, "cn=ServiceUser")
        except:
            return False
        return "\nuserPassword:: " in output

    def generate_ldifs(member, uidnumber, passwd):
        """Generates the strings needed to create the ldap user."""
        username = member.username_fld
        preferredname = member.preferredName_fld
        surname = member.surName_fld
        email = member.contactinfo.email_fld

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
        """ % (username, username, preferredname + " " + surname, username,
                uidnumber, surname, preferredname, username, email, passwd)

        # LDIF used to add the user to the medlem group.
        usergroupldif = """
dn: cn=medlem,ou=Group,dc=teknologforeningen,dc=fi
changetype: modify
add: memberUid
memberUid: %s
    """ % username

        return userldif, usergroupldif

    def get_next_uidnumber():
        """Returns the next free uidnumber greater than 1000"""
        uidquery = shlex.split("""ldapsearch -h ldap-master.teknologforeningen.fi \
                -b dc=fi -D cn=*serviceuser*,dc=teknologforeningen,dc=fi -w\
                *servicepassword* uidNumber""")
        output = check_output(uidquery, universal_newlines=True)
        uidnumbers = [int(line.split(": ")[1]) for line in output.split("\n") if
                "uidNumber: " in line]
        uidnumbers.sort()

        # Find first free uid over 1000.
        last = 1000
        for uid in uidnumbers:
            if uid > last + 1:
                break
            last = uid
        return last + 1

    def checkldapuser(member):
        #self.ldapsearch(
        ...

    def delldapuser(member):
        # Delete LDAP user account
        delusercmd = shlex.split("ldapdelete -h \
                ldap-master.teknologforeningen.fi -xD \
                cn=*serviceuser*,dc=teknologforeningen,dc=fi -w \
                *servicepassword* uid=""" + member.username_fld +
                ",ou=People,dc=teknologforeningen,dc=fi")

        if self.dry_run:
            cmd.append("-n")

        print(check_output(delusercmd))

        # Delete user from Members group
        deluserfromgroupldif = """
dn: cn=medlem,ou=Group,dc=teknologforeningen,dc=fi
changetype: modify
delete: memberUid
memberUid: """ + member.username_fld
        cmd = LDAPMODIFY_CMD
        groupmodproc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        out = groupmodproc.communicate(input=deluserfromgroupldif.encode())
        print(out[0].decode())

        return True

    def addldapuser(member):
        uidnumber = get_next_uidnumber()
        passwd = "passwd"
        userldif, usergroupldif = generate_ldifs(member, uidnumber, passwd)
        # Add the user to LDAP
        cmd = LDAPMODIFY_CMD
        if self.dry_run:
            cmd.append("-n")

        adduserproc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        out1 = adduserproc.communicate(input=userldif.encode())
        print(out1[0].decode())
        if adduserproc.returncode: # Failed command
            return False

        # Add the user to Members-group
        groupmodproc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        out2 = groupmodproc.communicate(input=usergroupldif.encode())
        print(out2[0].decode())

        return True


def main():
    lm = LDAPAccountManager()
    return 0

    member = Member()
    member.username_fld = "test123"
    member.preferredName_fld = "John"
    member.surName_fld = "Döe"
    member.contactinfo = ContactInformation()
    member.contactinfo.email_fld = "john.doe@test.net"
    passwd= "hunter2"
    if addldappuser(member):
        delldapuser(member)
        return 0
    return 1

if __name__ == '__main__':
    status = main()
    sys.exit(status)
