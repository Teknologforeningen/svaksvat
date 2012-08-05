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

import csvimporter

# constants
# exception classes
# interface functions
# classes
# internal functions & classes


def main():
    SessionMaker = connect.connect('members',
        'members', 'localhost', 'members')
    session = SessionMaker()

    memberdictlist = csvimporter.parse_csv(sys.argv[1], ',', None)
    for memberdict in memberdictlist:
        memberquery = session.query(Member).filter(Member.surName_fld ==
                memberdict["Efternamn"])
        birthdatestr = ""
        try:
            birthdatestr = memberdict["födelsedatum"]
        except KeyError:
            pass
        if birthdatestr:
            datelist = [int(s) for s in
                    birthdatestr.split('.')]
            datelist.reverse()
            birthdate = datetime.datetime(*datelist)

            memberquery = memberquery.filter(Member.birthDate_fld ==
                            birthdate)
        else:
            memberquery = memberquery.join(
                    ContactInformation).filter(
                    ContactInformation.phone_fld == memberdict["Telefon"])

        try:
            member = memberquery.one()

            member.contactinfo.email_fld = memberdict["e-post"]
        except sqlalchemy.orm.exc.NoResultFound:
            print("Not found: ", memberquery)


    session.commit()



if __name__ == '__main__':
    status = main()
    sys.exit(status)
