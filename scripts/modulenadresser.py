"""Output CSV with contact information for people eligible for Modulen."""

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

def get_contactinfo_tuple(member):
    """Returns tuple with the member's contact information for posting."""
    contactinfo = member.contactinfo
    department = '?'
    try:
        department = member.department[0].department.name_fld
    except:
        pass

    return (member.preferredName_fld, member.surName_fld, contactinfo.email_fld,
            contactinfo.streetAddress_fld, contactinfo.postalCode_fld,
            contactinfo.city_fld, contactinfo.country_fld, department)


def get_modulenaddresses(session):
    print("Hamtar ordinarie")
    ordinarie = common.get_members_with_membership(session,
            "Ordinarie medlem", True).filter(
            Member.subscribedtomodulen_fld == 1).all()

    print("Hamtar StAlM")
    alumni = common.get_members_with_membership(
            session, "StÄlM", True).filter(
            Member.subscribedtomodulen_fld == 1).all()

    return ordinarie + alumni

def get_funkisar(session):
    posts = session.query(Post).all()
    funkisar = set()

    for post in posts:
        for membership in post.memberships:
            if membership.isCurrent():
                funkisar.add(membership.member)

    return funkisar


def get_radmembers(session):
    radlist = ["dar", "ar", "fr", "far", "konrad"]
    rads = session.query(Group).filter(Group.abbreviation_fld.in_(radlist)).all()
    radmembers = set()

    for rad in rads:
        for membership in rad.memberships:
            if membership.isCurrent():
                radmembers.add(membership.member)

    return radmembers

def get_dekadenskontakter(session):
    memberships = session.query(Group).filter(Group.name_fld ==
            "Styrelsen").one().memberships
    dekadenskontakter = set()

    for mship in memberships:
        # if mship started 10 years ago.
        if (mship.startTime_fld > datetime.datetime.now() -
            datetime.timedelta(365 * 10)):
            dekadenskontakter.add(mship.member)

    return dekadenskontakter

def get_tfs(year=None):
    if not year:
        year = datetime.date.today().year

    memberships = session.query(Group).filter(Group.name_fld ==
            "Styrelsen").one().memberships

    tfs = set()

    for mship in memberships:
        if (mship.startTime_fld.date.year == year):
            tfs.add(mship.member)





def get_christmascardaddressess(session):
    posts = session.query(Post).all()
    xmascardmembers = set()

    xmascardmembers.add(get_funkisar(session))

    kanslist = common.get_members_with_membership(session,
            "Kanslist", True).one()

    kanslistemerita = common.get_members_with_membership(session,
            "Kanslist emerita", True).filter(
            Member.dead_fld == 0).all()

    for kanslistemeritus in kanslistemerita:
        xmascardmembers.add(kanslistemeritus)

    xmascardmembers.add(kanslist)


    xmascardmembers.add(get_radmembers(session))

    return xmascardmembers

def main():
    ps = passwordsafe.PasswordSafe()
    SessionMaker = ps.connect_with_config("mimer")
    session = SessionMaker()

    print("Detta script get ut adresser i csv format.")
    print("Alternativ:")
    print("1. Modulen")
    choice = input("Vilka adresser vill du ha?\n")
 
    if choice[0] == "1":
        print("Modulen vald")
        filename = "modulenadresser.csv"
        members = get_modulenaddresses(session)

    print("Oppnar fil.")
    writer = csv.writer(open(filename, "w"))

    print("Skriver fil: %s/%s" % (os.getcwd(), filename))
    for member in members:
            writer.writerow(get_contactinfo_tuple(member))

    print("Fardig")
    """
    radlist = ["dar", "ar", "fr", "far", "konrad"]
    members = []
    rads = session.query(Group).filter(Group.abbreviation_fld.in_(radlist)).all()

    for rad in rads:
        for membership in rad.memberships:
            if membership.isCurrent():
                m = membership.member
                writer.writerow([m.surName_fld + " " + m.preferredName_fld,
                    rad.name_fld])

    memberships = session.query(MembershipType).filter(MembershipType.name_fld
            == "Ordinarie medlem").one().membership
    mships = [mship for mship in memberships if mship.isCurrent()]
    for mship in mships:
        m = mship.member
        writer.writerow(get_contactinfo_tuple(m))
    #members = get_funkisar(session)
    thisyear = datetime.date.today().year
    #members = get_dekadenskontakter(session)
    #members = members | get_radmembers(session)
    for year in range(thisyear - 10, thisyear):
        members = get_tfs(year)
        writer.writerow(year)
        for member in members:
            writer.writerow(get_contactinfo_tuple(member))
    """

if __name__ == '__main__':
    status = main()
    sys.exit(status)

