"""Commonly used queries on the database"""

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

# constants
# exception classes
# interface functions

def get_members_with_groupmembership(session, groupname, is_current=False):
    return get_members_with_membership_generic(Group, GroupMembership, session,
            groupname, is_current)

def get_members_with_membership(session, membershipname, is_current=False):
    return get_members_with_membership_generic(Membership, MembershipMembership, session,
            membershipname, is_current)

def get_members_with_membership_generic(membershiptypeclass, membershipclass,
        session, membershipname, is_current=False):
    typerow = session.query(membershiptypeclass).filter(
            membershiptypeclass.name_fld ==
            membershipname).one()
    typeid = typerow.objectId
    if is_current:
        return get_members_with_current_membership_id_generic(membershipclass, session, typeid)
    else:
        return get_members_with_membership_id_generic(membershipclass, session, typeid)

def get_members_with_membership_id_generic(membershipclass, session, membershipid):
    return session.query(Member).join(membershipclass).filter(
            membershipclass.membershipType_fld == membershipid)

def get_members_with_current_membership_id_generic(membershipclass, session, membershipid):
    membersquery = get_members_with_membership_id_generic(membershipclass, session, membershipid)
    now = datetime.now()
    return membersquery.filter(sqlalchemy.or_(membershipclass.endTime_fld > now,
                membershipclass.endTime_fld == None))

# classes
# internal functions & classes
