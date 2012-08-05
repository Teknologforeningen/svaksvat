"""Update non cc.hut.fi emails in LDAP from membersregistry.

Usage:
python3 ldpmailupdate.py > modify
ldapmodify -h 82.130.59.133 -D "cn=*ldapmanager*,dc=teknologforeningen,dc=fi" -w
*managerpasswd* -f modify
"""

# imports
import sys
import os
import sqlalchemy
import datetime

sys.path.append(os.path.dirname(os.getcwd()))  # Add .. to path
from backend import connect
from backend.orm import *

# constants
# exception classes
# interface functions
# classes
# internal functions & classes

def main():
    SessionMaker = connect.connect_localhost_readwrite()
    session = SessionMaker()
    users = session.query(Member).filter(Member.username_fld != None).all()
    for user in users:
        uid = user.username_fld
        mail = user.contactinfo.email_fld
        if "cc.hut.fi" not in mail:
            sys.stdout.write("""
dn: uid=%s,ou=People,dc=teknologforeningen,dc=fi
changetype: modify
replace: mail
mail: %s
-
""" % (uid, mail))



if __name__ == '__main__':
    status = main()
    sys.exit(status)

