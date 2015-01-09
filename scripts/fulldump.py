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


def get_contactinfo_tuple(member):
    """Returns tuple with the member's contact information for posting."""
    contactinfo = member.contactinfo
    department = '?'
    try:
        department = member.department[0].department.name_fld
    except:
        pass

    return (member.preferredName_fld, member. member.surName_fld,
            contactinfo.email_fld,
            contactinfo.streetAddress_fld, contactinfo.postalCode_fld,
            contactinfo.city_fld, contactinfo.country_fld, department)


def dump_member(member, writer):
    groups = ""
    posts = ""
    memberships = ""
    currentmembership = ""
    for groupmembership in member.groupmemberships:
        if groupmembership.startTime_fld and groupmembership.endTime_fld:
            group = groupmembership.group
            for year in range(groupmembership.startTime_fld.date().year,
                    groupmembership.endTime_fld.date().year + 1):
                groups += "%s %d," % (group.name_fld, year)

    for postmembership in member.postmemberships:
        if postmembership.startTime_fld and postmembership.endTime_fld:
            post = postmembership.post
            for year in range(postmembership.startTime_fld.date().year,
                    postmembership.endTime_fld.date().year + 1):
                posts += "%s %d," % (post.name_fld, year)

    probablyphuxyear = 9999
    probablyphuxmembership = ''
    stalmstart = ''
    for membership in member.membershipmemberships:
        mship = membership.membership
        if mship.name_fld == 'StÄlM' and membership.startTime_fld:
            stalmstart = membership.startTime_fld.year

        if membership.isCurrent():
            currentmembership += mship.name_fld + " "

        begin = end = ""
        try:
            begin = membership.startTime_fld.year
            if begin < probablyphuxyear:
                probablyphuxyear = begin
                probablyphuxmembership = mship.name_fld
            end = membership.endTime_fld.year

        except:
            continue

        finally:
            memberships += "%s %s - %s," % (mship.name_fld, begin or "", end or "")

    writer.writerow([str(probablyphuxyear) + " " + probablyphuxmembership, stalmstart] + [currentmembership] + [getattr(member, x.__str__().split('.')[1]) for x in Member.__table__.columns] + [getattr(member.contactinfo, x.__str__().split('.')[1]) for x in ContactInformation.__table__.columns] + [groups] + [posts] + [memberships])

def main():
    ps = passwordsafe.PasswordSafe()
    SessionMaker = ps.connect_with_config("mimer")
    session = SessionMaker()
    writer = csv.writer(open("alltut.csv", "w"))
    

    #members = [m for m in session.query(Member).all() if not m.membershipmemberships]
    #print ("all members without memberships: ", len(members))

    members = common.get_members_with_membership(session,
                                                 "Ordinarie medlem",
                                                 False, True).all()
    print("member length without ordinarie medlem: ", len(members))

    members += common.get_members_with_membership(session,
                                                  "Ordinarie medlem",
                                                  True, True).all()
    print("member length after noncurrent ordinarie medlem: ", len(members))

    members = common.get_members_with_membership(session,
                                                  "Ordinarie medlem",
                                                  True, False).all()
    print("Ordinarie medlemmar: ", len(members))

    members = session.query(Member).all()
    print("All members: ", len(members))

    header = ["första år samt medlemskapstyp", "StälMstart", "Nuvarande medlemskapstyp"] + [x.__str__().split('.')[1] for x in Member.__table__.columns]
    header += [x.__str__().split('.')[1] for x in
               ContactInformation.__table__.columns]
    header += ["grupper", "poster", "medlemskap"]
    writer.writerow(header)
    
    counter = 0
    for member in members:
        dump_member(member, writer)
        counter += 1
        if counter % 50 == 0:
            print(int((counter/len(members))*100), "%")

    print("All done. Kill me if I wont quit...")
    return

    """
    for member in members:
        if member.notes_fld:
            writer.writerow([member.getWholeName(), "Hedersbetygelser:",
                member.notes_fld])
        for groupmembership in member.groupmemberships:
            if groupmembership.startTime_fld and groupmembership.endTime_fld:
                group = groupmembership.group
                for year in range(groupmembership.startTime_fld.date().year,
                        groupmembership.endTime_fld.date().year + 1):
                    writer.writerow([member.getWholeName(), group.name_fld, year])
        for postmembership in member.postmemberships:
            if postmembership.startTime_fld and postmembership.endTime_fld:
                post = postmembership.post
                for year in range(postmembership.startTime_fld.date().year,
                        postmembership.endTime_fld.date().year + 1):
                    writer.writerow([member.getWholeName(), post.name_fld, year])

    """

if __name__ == '__main__':
    status = main()
    sys.exit(status)

