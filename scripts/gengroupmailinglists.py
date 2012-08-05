"""Generates the mailinglists for all groups."""

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
    SessionMaker = connect.connect_localhost_readwrite()
    session = SessionMaker()

    groups = session.query(Group).all()

    print("Generating mailing lists for:")

    thisyear = str(datetime.datetime.now().year)[-2:]

    listdir = "lists"
    if not os.path.exists(listdir):
        os.mkdir(listdir)
        print("Created lists directory")

    elif os.path.isfile(listdir):
        print("Error: lists is a file. Exiting...")
        return

    for group in groups:
        if group.abbreviation_fld != None:
            print(group.name_fld)
            mailinglist = open(os.path.join(listdir, group.abbreviation_fld +
                thisyear), "w")
            mailinglist.write("# " + group.name_fld + " generated " +
                    datetime.date.today().isoformat())
            for membership in group.memberships:
                if membership.isCurrent():
                    mailinglist.write("\n# %s\n%s" %
                            (membership.member.getWholeName(),
                                membership.member.contactinfo.email_fld))


if __name__ == '__main__':
    status = main()
    sys.exit(status)

