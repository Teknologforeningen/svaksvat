"""Sets subscribedtomodulen_fld = 0 for all except StÄlMs"""

# imports
import sys
import os
import sqlalchemy
import csv

sys.path.append(os.getcwd())  # Add . to path
sys.path.append(os.path.dirname(os.getcwd()))  # Add .. to path
from backend.ldaplogin import (get_member_with_real_name,
                DuplicateNamesException, PersonNotFoundException)
from backend import connect
from backend.orm import *
import passwordsafe

import common

# constants
# exception classes
# interface functions
# classes
# internal functions & classes

def main(session):
    ordinarie = common.get_members_with_membership(session,
                                                   "Phux", True)
    for member in ordinarie:
        member.subscribedtomodulen_fld = 0
        print(member.givenNames_fld + " " + member.surName_fld +"\n")

    print("dirty count:", len(session.dirty))

    if input("Are you sure [y/n]? ") == "y":
        print("Committing...")
        session.commit()
        return
    print("Rolling back changes")



if __name__ == '__main__':
    ps = passwordsafe.PasswordSafe()
    SessionMaker = ps.connect_with_config("members")
    session = SessionMaker()
    status = main(session)
    sys.exit(status)
