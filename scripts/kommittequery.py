"""Queries all persons in kommittees."""

# imports
import sys
import os
import sqlalchemy
import datetime

sys.path.append(os.getcwd())  # Add . to path
sys.path.append(os.path.dirname(os.getcwd()))  # Add .. to path
from backend.ldaplogin import (get_member_with_real_name,
        DuplicateNamesException, PersonNotFoundException)
from backend import connect
from backend.orm import *

import common

# constants
# exception classes
# interface functions
# classes
# internal functions & classes

def main():
    SessionMaker = connect.connect_localhost_readwrite()
    session = SessionMaker()

    groups = session.query(Group).filter(
            Group.name_fld=="Styrelsen")

    for group in groups:
        for membership in group.memberships:
            print(str(membership.startTime_fld.date().year) + "\t"
                    + membership.member.getName() + "\t" +
                    membership.member.contactinfo.email_fld)


if __name__ == '__main__':
    status = main()
    sys.exit(status)

