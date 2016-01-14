"""Output CSV with with meritlist for all members"""

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

def main():
    ps = passwordsafe.PasswordSafe()
    SessionMaker = ps.connect_with_config("members")
    session = SessionMaker()
    writer = csv.writer(open("meritlist.csv", "w"))
    members = session.query(Member).order_by(Member.surName_fld).all()
    for member in members:
        for membership in member.membershipmemberships:
            mship = membership.membership
            currentmembership = ""
            if membership.isCurrent():
                currentmembership += mship.name_fld + " "

        if member.notes_fld:
            writer.writerow([currentmembership, member.getWholeName(), "Hedersbetygelser:",
                member.notes_fld])
        for groupmembership in member.groupmemberships:
            if groupmembership.startTime_fld and groupmembership.endTime_fld:
                group = groupmembership.group
                for year in range(groupmembership.startTime_fld.date().year,
                        groupmembership.endTime_fld.date().year + 1):
                    writer.writerow([currentmembership, member.getWholeName(), group.name_fld, year])
        for postmembership in member.postmemberships:
            if postmembership.startTime_fld and postmembership.endTime_fld:
                post = postmembership.post
                for year in range(postmembership.startTime_fld.date().year,
                        postmembership.endTime_fld.date().year + 1):
                    writer.writerow([currentmembership, member.getWholeName(), post.name_fld, year])
    print("I am all done, kill me please.")
    sys.exit(0)

if __name__ == '__main__':
    status = main()
    sys.exit(status)
