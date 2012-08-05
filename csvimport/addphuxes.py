"""Script to add members from a CSV-file to the database.
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

import csvimporter

#constants

DEPARTMENTS = ["Arkitektur", "Automations- och systemteknik", "Materialteknik",
    "Bionformationsteknologi", "Byggnads- och miljöteknik", "Datateknik",
    "Elektronik och elektroteknik", "Teknisk fysik och matematik",
    "Informationsnätverk", "Kemiteknik", "Lantmäteri", "Maskinteknik",
    "Produktionsekonomi", "Telekommunikationsteknik", "Bioproduktteknologi",
    "ASE Business Technology", "ASE CEMS", "ASE finansiering",
    "ASE företagsamhet", "ASE företagsjuridik", "ASE handel",
    "ASE i.a.S. Management", "ASE international business communication",
    "ASE logistik", "ASE marknadsföring", "ASE nationalekonomi",
    "ASE affärskommunikation", "ASE organisation och ledarskap",
    "ASE redovisning", "ASAD filmkonst", "ASAD Fotografering",
    "ASAD grafisk design", "ASAD industriell design",
    "ASAD Inredningsarkitektur och möbeldesign",
    "ASAD Keramik och glaskonst", "ASAD Beklädnadsdesign och dräktkonst",
    "ASAD konstpedagogik", "ASAD tekstilkonst", "ASAD scenografi"]

def get_phux_membershiptype(session):
    phuxes = session.query(MembershipType).filter(MembershipType.name_fld ==
        "Phux").one()
    return phuxes

def get_department(session, departmentname):
    department = session.query(Department).filter(Department.name_fld ==
        departmentname).one()
    return department

def main():
    SessionMaker = connect.connect('members', 'members', 'localhost', 'members')
    session = SessionMaker()

    memberdictlist = csvimporter.parse_csv(sys.argv[1], ',', '"')
    for memberdict in memberdictlist:
        new_member = create_phux(session)

        csvimporter.update_contact_info(new_member, memberdict, dry_run = False)

        birthdate = memberdict["birthDate_fld_format"]
        if birthdate:
            datelist = [int(s) for s in
                    birthdate.split('.')]
            datelist.reverse()
            new_member.birthDate_fld = datetime.datetime(*datelist)

        if memberdict["subscribedtomodulen_fld_format"]:
            new_member.subscribedtomodulen_fld = 0;

        departmentstr = memberdict["department_format"]
        if departmentstr:
            department = get_department(session,
                        DEPARTMENTS[int(departmentstr) - 1])
            new_departmentmship = create_row(DepartmentMembership, session)
            new_departmentmship.member = new_member
            new_departmentmship.department = department
            new_departmentmship.startTime_fld = datetime.datetime(day=29, month=8,
                    year=int(memberdict["registeredYear"]))
            session.add(new_departmentmship)

        genderstr = memberdict["gender_fld_format"]
        if genderstr:
            new_member.gender_fld = int(genderstr)




    print("Dirty: ", session.dirty)
    print("New: ", session.new)
    session.commit()


if __name__ == '__main__':
    main()
