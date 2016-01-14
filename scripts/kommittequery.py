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

import passwordsafe

# constants
# exception classes
# interface functions
# classes
# internal functions & classes

def main():
    ps = passwordsafe.PasswordSafe()
    SessionMaker = ps.connect_with_config("members")
    session = SessionMaker()

    groups = session.query(Group).filter(
            Group.name_fld=="Styrelsen")

    with open("test.csv", "w") as f:
        for group in groups:
            for membership in group.memberships:
                f.write(str(membership.startTime_fld.date().year) + "\t"
                        + membership.member.getName() + "\t" +
                        membership.member.contactinfo.email_fld + "\n")


if __name__ == '__main__':
    status = main()
    sys.exit(status)

