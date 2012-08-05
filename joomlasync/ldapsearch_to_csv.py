"""
Parse output of ldapsearch to a CSV-file with rows as 'common
name,username'.
"""

# imports
import os
import sys
import csv

sys.path.append(os.path.dirname(os.getcwd()))  # Add ..
from backend.ldaplogin import extract_name_from_ldapquery


def main():
    uidlist = []
    cnlist = []

    for line in sys.stdin:
        if line.startswith('uid:'):
            uid = line.split(':')[1].strip()
            uidlist.append(uid)

        if line.startswith('cn:'):
            # extract_name_from_ldapquery accepts only bytestrings.
            cn = extract_name_from_ldapquery(line.encode())
            cnlist.append(cn)

    db = {}
    writer = csv.writer(open('uid_cn.csv', 'w'))
    for uid, cn in zip(uidlist, cnlist):
        print(cn, uid)
        writer.writerow((cn, uid))

    return 0


if __name__ == '__main__':
    status = main()
    sys.exit(status)
