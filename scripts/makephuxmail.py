"""module docstring"""

# imports
import sys
import os
import sqlalchemy
import datetime

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
    SessionMaker = connect.connect('members',
        'members', 'localhost', 'members')
    session= SessionMaker()

    phuxes = common.get_members_with_current_membership_id(session, "Phux")

    departmentdict = {}
    for phux in phuxes:
        try:
            departmentdict.setdefault(phux.department[0].department.name_fld,
                    []).append(phux.contactinfo.email_fld)
        except IndexError: # No phuxes
            continue

    for department, emails in departmentdict.items():
        print(department)
        for email in emails:
            print(email)
        print()


if __name__ == '__main__':
    status = main()
    sys.exit(status)
