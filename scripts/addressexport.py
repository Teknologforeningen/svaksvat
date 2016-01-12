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

def get_contactinfo_tuple(member, considerNoPublish=False):
    """Returns tuple with the member's contact information

    If considerNoPublish is True a member with noPublishContactInfo_fld == 1
    will get empty contact information fields.
    """
    contactinfo = member.contactinfo
    department = '?'
    try:
        department = member.department[0].department.name_fld
    except:
        pass

    if considerNoPublish and member.dead_fld == 0 and member.noPublishContactInfo_fld == 1:
            return (member.preferredName_fld, member.surName_fld,
                    "", "", "", "", "", "")

    return (member.preferredName_fld, member.surName_fld,
            contactinfo.email_fld,
            contactinfo.streetAddress_fld, contactinfo.postalCode_fld,
            contactinfo.city_fld, contactinfo.country_fld, department)

def get_allinfo_tuple(member):
    """Returns tuple with the member's complete information for posting."""
    contactinfo = member.contactinfo
    department = '?'
    try:
        department = member.department[0].department.name_fld
    except:
        pass


    return (member.preferredName_fld,
            member.surName_fld,
            member.givenNames_fld,
            member.maidenName_fld,
            member.nickName_fld,
            member.birthDate_fld,
            member.studentId_fld,
            member.gender_fld,
            member.graduated_fld,
            member.occupation_fld,
            member.photo_fld,
            member.title_fld,
            member.nationality_fld,
            member.dead_fld,
            member.subscribedtomodulen_fld,
            member.username_fld,
            member.lastsync_fld,
            contactinfo.email_fld,
            contactinfo.streetAddress_fld,
            contactinfo.postalCode_fld,
            contactinfo.city_fld,
            contactinfo.country_fld,
            contactinfo.fax_fld,
            contactinfo.url_fld,
            contactinfo.location_fld,
            contactinfo.phone_fld,
            contactinfo.cellPhone_fld,
            department)


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

def get_stalmar(session):

    print("Hamtar StAlM")
    alumni = common.get_members_with_membership(
            session, "StÄlM", True).all()

    return alumni

def get_ordinarie(session):
    print("Hamtar ordinarie")
    ordinarie = common.get_members_with_membership(session,
            "Ordinarie medlem", True).all()

    return ordinarie

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

    xmascardmembers = get_funkisar(session)

    kanslist = common.get_members_with_membership(session,
            "Kanslist", True).one()

    kanslistemerita = common.get_members_with_membership(session,
            "Kanslist emerita", True).filter(
            Member.dead_fld == 0).all()

    for kanslistemeritus in kanslistemerita:
        xmascardmembers.add(kanslistemeritus)

    xmascardmembers.add(kanslist)

    xmascardmembers.update(get_radmembers(session))

    return xmascardmembers

def get_katalogenlist_stalm(session):
    print("Hamtar StAlM")
    alumni = common.get_members_with_membership(
            session, "StÄlM", True).all()

    return alumni

def get_katalogenlist_ordinarie(session):
    print("Hamtar ordinarie")
    ordinarie = common.get_members_with_membership(session,
            "Ordinarie medlem", True).all()
    return ordinarie

def main():
    ps = passwordsafe.PasswordSafe()
    SessionMaker = ps.connect_with_config("members")
    session = SessionMaker()

    ignoreKatalogen = False

    print("Detta script get ut adresser/info i csv format.")
    print("Alternativ:")
    print("1. Modulen")
    print(" -Lista för alla som Modulen skall skickas till")
    print("2. StÄlMar")
    print(" -Lista på alla stämar")
    print("3. Ordinarie")
    print(" -Lista på alla Ordinarie")
    print("4. Julkort")
    print(" -Vem skall få julkort?")
    print("5. Katalogen-lista-Stalm")
    print(" -Lista på alla stälmar, utom dom som inte vill ge ut info")
    print("6. Katalogen-lista-ordinarie")
    print(" -Lista på alla ordinarie, utom dom som inte vill ge ut info")
    print("\nDu får välja om du vill ha address, eller all info sedan.")


    choice = input("Ange siffra:\n")

    if choice[0] == "1":
        print("Modulen vald")
        filename = "modulenadresser.csv"
        members = get_modulenaddresses(session)
    elif choice[0] == "2":
        print("StÄlMar valda")
        filename = "stalmar.csv"
        members = get_stalmar(session)
    elif choice[0] == "3":
        print("Ordinarie valda")
        filename = "ordinarie.csv"
        members = get_ordinarie(session)

    elif choice[0] == "4":
        print("Julkort vald")
        filename = "julkortadresser.csv"
        members = get_christmascardaddressess(session)

    elif choice[0] == "5":
        print("Katalogen-lista-stalm vald")
        filename = "katalogen-lista-stalm.csv"
        members = get_katalogenlist_stalm(session)
        ignoreKatalogen = True

    elif choice[0] == "6":
        print("katalogen-lista-ordinarie vald")
        filename = "katalogen-lista-ordinarie.csv"
        members = get_katalogenlist_ordinarie(session)
        ignoreKatalogen = True  

    print("Oppnar fil.")
    writer = csv.writer(open(filename, "w"))

    choice = "2"
    choice = input("Vill du ha all info(1) eller kontaktuppgifter(2)?[2]")
    if choice[0] == "1":
        print("All info vald")
        print("Skriver fil: %s/%s" % (os.getcwd(), filename))
        for member in members:
            writer.writerow(get_allinfo_tuple(member))
    else:
        print("Endast adresser valda")
        print("Skriver fil: %s/%s" % (os.getcwd(), filename))
        for member in members:
            writer.writerow(get_contactinfo_tuple(member, ignoreKatalogen))

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
