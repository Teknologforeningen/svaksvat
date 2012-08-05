"""
Sync LDAP usernames to database.

1. Directly from email if cc.hut.fi domain.
2. Through 'common name,username' csv-file.
3. Dump list of members not found to csv-file.
4. Dump list of conflicting members to csv-file.
"""

# imports

import csv
import sys
import os

import sqlalchemy

sys.path.append(os.path.dirname(os.getcwd()))  # Add .. to path
from backend.ldaplogin import (get_member_with_real_name,
        split_ldap_common_name, DuplicateNamesException,
        PersonNotFoundException)

from backend import connect
from backend.orm import Member, ContactInformation


def set_username(member, username):
        print(member.getWholeName(), username)
        member.username_fld = username


def main():
    SessionMaker = connect.connect('members', 'members', 'localhost', 'members')
    session = SessionMaker()

    alreadyimported = []

    # uid from email with cc.hut.fi
    # fetch users without username and cc.hut.fi email
    no_username = session.query(Member).filter(Member.username_fld == None)
    from_email = no_username.join(ContactInformation).filter(
            ContactInformation.email_fld.like('%cc.hut.fi')).all()
    for member in from_email:
        username = member.contactinfo.email_fld.split('@')[0]
        alreadyimported.append(username)
        set_username(member, username)

    # uid from ldapsearch query stored in csv_file.

    print("Already imported: alreadyimported")

    not_found = []
    conflictingset = set()
    if len(sys.argv) > 1:
        reader = csv.reader(open(sys.argv[1], 'r'))

        for cn, uid in reader:
            if uid not in alreadyimported:
                firstname, surname = split_ldap_common_name(cn)

                try:
                    member = get_member_with_real_name(firstname, surname, session)
                    set_username(member, uid)

                except PersonNotFoundException:
                    not_found.append((cn, uid))

                except DuplicateNamesException as e:
                    conflictingset.add(tuple(e.query.all()))

    print("NOT FOUND" + '#' * 70)
    writer = csv.writer(open('not_found.csv', 'w'))
    for cn, uid in not_found:
        writer.writerow((cn, uid))
        print(cn, uid)

    print("CONFLICTS" + '#' * 70)
    for conflicts in conflictingset:
        for conflictingmember in conflicts:
            print(conflictingmember.getWholeName())
        print("-" * 80)

    if input("commit? [y/N]").lower() in ('y', 'yes'):
        print("Committing...")
        session.commit()

    return 0


if __name__ == '__main__':
    status = main()
    sys.exit(status)
