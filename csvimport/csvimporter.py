"""Script to import fields from a CSV-file to the database.
"""

# imports
import csv
import sys
import os
import sqlalchemy

sys.path.append(os.path.dirname(os.getcwd()))  # Add .. to path
from backend.ldaplogin import (get_member_with_real_name,
        DuplicateNamesException, PersonNotFoundException)
from backend import connect
from backend.orm import *


# interface functions
def add_posts(filename, session):
    member_dict_pairs, notfound, conflictingset = import_csv(filename, session)
    postnames = [post.name_fld for post in session.query(Post).all()]
    groupnames = [group.name_fld for group in session.query(Group).all()]
    for member, memberdict in member_dict_pairs:
        taskname = memberdict["Post"]
        mship = None
        if taskname in postnames:
            mship = create_row(PostMembership, session)
            mship.post = session.query(Post).filter(Post.name_fld ==
                    taskname).one()

        elif  taskname in groupnames:
            mship = create_row(GroupMembership, session)
            mship.group = session.query(Group).filter(Group.name_fld ==
                    taskname).one()

        else:
            print(taskname + " not found.")
            continue

        mship.member = member
        year = int(memberdict["Year"])
        mship.startTime_fld = datetime.datetime(year, 1, 1)
        mship.endTime_fld = datetime.datetime(year, 12, 31)

    notfound = notfound
    print_notfound_as_cvs(notfound)
    print("CONFLICTS:")
    for conflicts in conflictingset:
        for conflictingmember in conflicts:
            print(conflictingmember.getWholeName())
    #print_notfound_and_conflicts(notfound, conflictingset)
    session.commit()


def import_csv(filename, session):
    '''Import CSV-file to database

    Returns (member_dict_pairs, notfoundlist, conflictingset) where:
    member_dict_pairs - Tuples of found members with corresponding memberdict.
    notfoundlist - Members not found in the database.
    conflictingset - Members with too similar names.

    '''
    # List of dicts with field and value pairs
    memberdictlist = parse_csv(filename)

    member_dict_pairs = []
    notfoundlist = []
    conflictingset = set()

    dbsession = session
    for memberdict in memberdictlist:
        firstname = memberdict['givenNames_fld'].split(' ')[0]
        lastname = memberdict['surName_fld']
        try:
            member = get_member_with_real_name(firstname, lastname, dbsession)
            member_dict_pairs.append((member, memberdict))

        except PersonNotFoundException:
            notfoundlist.append(memberdict)

        except DuplicateNamesException as e:
            conflictingset.add(tuple(e.query.all()))

    return (member_dict_pairs, notfoundlist, conflictingset)


def parse_csv(filename,  delimiter=';', quotechar='"'):
    '''Parse CSV-file for contact information

    The first row is for the field names, each row thereafter is for the
    database records.  surName_fld and givenNames_fld is probably required to
    query for the Member.

    Returns list of fieldname=value dictionaries.
    '''

    memberdictlist = []
    with open(filename, newline='') as f:
        reader = csv.reader(f, delimiter=delimiter, quotechar=quotechar)
        try:
            fieldnames = reader.__next__()
            memberdictlist = [{field:value for field, value
                in zip(fieldnames, values)} for values in reader]

        except csv.Error as e:
            sys.exit('file {}, line {}: {}'
                    .format(filename, reader.line_num, e))
    return memberdictlist


def update_contact_info(member, memberdict, dry_run=False):
    print(member.getWholeName())
    #if not 'StÄlM' in (membership.type.name_fld for
            #membership in member.memberships):
        #print("Not StÄlM!")

    update_fields(member, memberdict, dry_run, verbose=True)
    update_fields(member.contactinfo, memberdict, dry_run, verbose=True)
    print('-' * 80)

def print_notfound_as_cvs(notfoundlist):
    writer = csv.writer(sys.stdout, delimiter=';', quotechar='"')
    try:
        keys = list(notfoundlist[0].keys())
        writer.writerow(keys)
        for notfound in notfoundlist:
            personrow = [notfound[key] for key in keys]
            writer.writerow(personrow)
    except IndexError:
        return



def print_notfound_and_conflicts(notfoundlist, conflictingset):
    print("Not found:" + "#" * 70)
    for notfound in notfoundlist:
        print(notfound)

    print("Conflicts:" + "#" * 70)
    for conflicts in conflictingset:
        for conflictingmember in conflicts:
            if 'StÄlM' in (membership.type.name_fld for
                    membership in conflictingmember.memberships):
                print(conflictingmember.getWholeName())
        print("-" * 80)


def main():
    filename = "test.csv"
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    SessionMaker = connect.connect('members', 'members', 'localhost', 'members')
    session = SessionMaker()
    member_dict_pairs, notfoundlist, conflictingset = import_csv(
            filename, session)
    toolongvalues = []
    try:
        [update_contact_info(member, memberdict, dry_run=False)
                for member, memberdict in member_dict_pairs]
    except TooLongValueException as e:
        toolongvalues.append(str(e))

    print_notfound_and_conflicts(notfoundlist, conflictingset)

    print("Too long values:" + "#" * 60)
    print(toolongvalues)
    for toolong in toolongvalues:
        print(toolong)

    #session.commit()
    return 0

def add_spexposts(session):
    newposts = ["Spexet: Assisterande regissör", "Spexet: Directeur",
    "Spexet: direction", "Spexet: Dirigent", "Spexet: Ekonomichef",
    "Spexet: Gyckleur", "Spexet: Infochef", "Spexet: Koreograf",
    "Spexet: Kostymchef", "Spexet: Kostymgrupp", "Spexet: Kulisschef",
    "Spexet: Kulissgrupp", "Spexet: Låtskrivarchef", "Spexet: Låtskrivare",
    "Spexet: Layoutgrupp", "Spexet: Manuschef", "Spexet: Manusgrupp", "Spexet: Musikalisk arrangör", "Spexet: Musikchef", "Spexet: Orkester", "Spexet: PR-chef", "Spexet: PR-grupp", "Spexet: PR- och infochef", "Spexet: PR och sponsgrupp", "Spexet: Producent", "Spexet: Produktionsassistent", "Spexet: Regissör", "Spexet: Scenmästare", "Spexet: Skådespelare", "Spexet: Spexklanen", "Spexet: Spexrådet", "Spexet: Sponsgrupp", "Spexet: Sufflös", "Spexet: Tecknare", "Spexet: Teknikchef", "Spexet: Teknikgrupp", "Spexet: Turnéchef"]

    spexposttype = create_row(PostType, session)
    spexposttype.name_fld = "Spexet"
    session.add(spexposttype)

    for postname in newposts:
        post = create_row(Post, session)
        post.name_fld = postname
        post.type = spexposttype

    session.commit()


def main2():
    filename = "test.csv"
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    SessionMaker = connect.connect('members', 'members', 'localhost', 'members')
    session = SessionMaker()

    #add_spexposts(session)

    add_posts(filename, session)

if __name__ == '__main__':
    status = main2()
    sys.exit(status)
