"""
The ORM mappings for both Joomla's MySQL and the member registry's Postgres
databases and related functions.
"""

# imports
from datetime import (date, datetime, timedelta)
import pickle
import sys

from sqlalchemy import (Column, ForeignKey, String, DateTime, Integer, Text,
                        Numeric)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.serializer import loads, dumps
import sqlalchemy

from PyQt5 import QtCore, QtGui

# constants
Base = declarative_base()

# exception classes
class TooLongValueException(Exception):
    def __init__(self, field, value, maxlength):
        self.field = field
        self.value = value
        self.maxlength = maxlength

    def __str__(self):
        return ("The value %s for the field %s is over %d in length." %
                (self.value, self.field, self.maxlength))


# interface functions
def backup_everything(session):
    meta = get_declarative_base().metadata
    backupdict = {}
    for table in reversed(meta.sorted_tables):
        query = session.query(table)
        queryresults = query.all()
        backupdict[table.name] = dumps(queryresults)

    return backupdict


def restore_everything(session, backupdict):
    meta = get_declarative_base().metadata
    # Truncate tables
    progress = QtGui.QProgressDialog()
    progress.show()
    progress.setAutoClose(True)
    progress.setLabelText("Tömmer databas")
    progress.setMaximum(len(meta.sorted_tables) + 1)
    for table in reversed(meta.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()

    progress.setLabelText("Återställer")

    # Add recovered objects
    for i, table in enumerate(meta.sorted_tables):
        progress.setValue(i + 1)
        if progress.wasCanceled():
            return False
        if table.name in backupdict:
            progress.setLabelText('Återställer tabellen %s' % table.name)
            QtCore.QCoreApplication.processEvents()
            serialized_table = backupdict[table.name]
            restored_objects = loads(serialized_table, meta, session)
            for restored_object in restored_objects:

                table_class = table.name.replace("Table", "")
                if (table_class == "MembershipType"):
                    table_class = "Membership"
                if (table_class == 'members_sequence'):
                    table_class = "Sequence"

                row = eval(table_class)()
                i = 0
                for key in restored_object.keys():
                    setattr(row, key, restored_object[i])
                    i += 1
                session.merge(row)

    session.commit()
    session.close()

    progress.close()
    return True


def create_row(table_orm, session):
    # We have to determine the correct objectId for from the sequence-table
    sequence_query = session.query(Sequence).filter(Sequence.objectname ==
                                                    table_orm.sequence_name)
    if sequence_query.count() == 0:
        session.add(Sequence(objectname=table_orm.sequence_name))
        session.commit()
    sequence = sequence_query.one()

    hexstring = number_to_string(sequence.next)
    # Integrity error avoidance due to corrupt sequence.
    while session.query(table_orm).filter_by(objectId=hexstring).count() != 0:
        sequence.next += 1
        hexstring = number_to_string(sequence.next)

    # Create the row
    row = table_orm()
    row.objectId = hexstring

    return row


def create_member(session):
    new_member = create_row(Member, session)
    new_contactinfo = create_row(ContactInformation, session)
    new_member.contactinfo = new_contactinfo
    new_member.contactinfos = [new_contactinfo]
    session.add(new_member)
    session.add(new_contactinfo)
    return new_member


def create_membership(session, membershiptargetname, name_fld,
        create_nonexistent_target=False):

    mshiptargetname = membershiptargetname
    membershipclassname = membershiptargetname + "Membership"

    globaldict = globals()
    membershiptargetclass = globaldict[membershiptargetname]
    membershipclass = globaldict[membershipclassname]

    membershiptarget = None
    try:
        membershiptarget = session.query(
                membershiptargetclass).filter_by(name_fld = name_fld).one()

    except sqlalchemy.orm.exc.NoResultFound:
        if create_nonexistent_target:
            membershiptarget = create_row(membershiptargetclass, session)
            membershiptarget.name_fld = name_fld
        else:
            return None

    new_membership = create_row(membershipclass, session)

    setattr(new_membership, mshiptargetname.lower(), membershiptarget)

    session.add(new_membership)

    return new_membership


def create_phux(session):
    new_phux = create_member(session)
    new_phuxmembership = create_membership(session, "Membership", "Phux", True)
    new_phuxmembership.member = new_phux

    today = datetime.today()
    year = today.year
    new_phuxmembership.startTime_fld = today
    # Phuxes die before labour day.
    if new_phuxmembership.startTime_fld.date() > date(today.year, 4, 30):
        year += 1

    new_phuxmembership.endTime_fld = datetime(year, 4, 30)

    session.add(new_phuxmembership)
    return new_phux

def get_declarative_base():
    """
    There must only be one declarative base for the ORM.
    """
    return Base


def number_to_string(number):
    """
    Converts given number to a String(32) representing
    an objectID primary key. Makes too long strings if
    the number is over 32 digits.

    >>> number_to_string(1)
    '00000000000000000000000000000001'

    >>> number_to_string(0xdeadbeef)
    '000000000000000000000000deadbeef'
    """

    # Convert to hexadecimal and remove leading '0x'
    objectID = hex(int(number))[2:]
    # Insert leading zeros.
    objectID = (32 - len(objectID)) * "0" + objectID
    return objectID


def update_fields(table, fielddict, dry_run=False, verbose=False):
    """
    Convenience function to update the fields in a table. The fielddict
    argument is a dict(fieldsname = fieldsvalue). The function checks that
    the fields are in the table and that they aren't too long.
    """
    for (field, value) in fielddict.items():
        if hasattr(table, field):
            update_field(table, field, value, dry_run, verbose)

def get_field_max_length(row, field):
    """Returns maximum length for fields with length,

    if field has no maximum length then return sys.maxsize."""
    field_type = getattr(row.__class__, field).property.columns[0].type
    if hasattr(field_type, "length"):
        return field_type.length
    return sys.maxsize

def update_field(row, field, value, dry_run=False, verbose=False):
    maxlength = get_field_max_length(row, field)
    if maxlength < len(value):
        raise TooLongValueException(field, value, maxlength)
    elif getattr(row, field) != value:
        if verbose:
            print(row.__tablename__, field,
                    getattr(row, field), '->', value)
        if not dry_run:
            setattr(row, field, value)


# classes
# The member registry tables.
class MemberRegistryCommon(object):
    """Common columns to all tables in the member registry."""
    created_fld = Column(DateTime, default=datetime.now())
    createdBy_fld = Column(String(36))
    modified_fld = Column(DateTime, onupdate=datetime.now())
    modifiedBy_fld = Column(String(36))
    notes_fld = Column(String(255))
    objectId = Column(String(36), primary_key=True)


class MembershipCommon(object):
    """Common columns to all membership tables in the member registry."""
    startTime_fld = Column(DateTime)
    endTime_fld = Column(DateTime)
    eventStatus_fld = Column(Integer)
    eventType_fld = Column(Integer)

    def isCurrent(self):
        now = datetime.now()
        return ((self.endTime_fld == None or
                self.endTime_fld > now) and
                (self.startTime_fld == None or self.startTime_fld < now)
                )

    def setMandateToThisYear(self):
        thisyear = date.today().year
        self.startTime_fld = datetime(thisyear, 1, 1)
        self.endTime_fld = datetime(thisyear, 12, 31)

class ContactInformation(get_declarative_base(), MemberRegistryCommon):
    """Member Contact Information"""
    __tablename__ = 'ContactInformationTable'
    sequence_name = "contactInformation"

    member_fld = Column(String(36), ForeignKey('MemberTable.objectId'))
    location_fld = Column(String(20))
    streetAddress_fld = Column(String(60))
    postalCode_fld = Column(String(20))
    city_fld = Column(String(30))
    country_fld = Column(String(30))
    phone_fld = Column(String(30))
    cellPhone_fld = Column(String(30))
    fax_fld = Column(String(30))
    url_fld = Column(String(60))
    email_fld = Column(String(50))

    publicfields = ['location_fld', 'streetAddress_fld',
            'postalCode_fld', 'city_fld', 'country_fld', 'phone_fld',
            'cellPhone_fld', 'fax_fld', 'url_fld', 'email_fld']


class DepartmentType(get_declarative_base(), MemberRegistryCommon,
        MembershipCommon):
    __tablename__ = "DepartmentTypeTable"
    sequence_name = "departmentType"

    name_fld = Column(String)
    description_fld = Column(String)

    department = relationship("Department", backref='type')


class Department(get_declarative_base(),
        MemberRegistryCommon, MembershipCommon):
    __tablename__ = 'DepartmentTable'
    sequence_name = "department"

    departmentType_fld = Column(String,
            ForeignKey("DepartmentTypeTable.objectId"))
    name_fld = Column(String)
    abbreviation_fld = Column(String)
    description_fld = Column(String)

    memberships = relationship("DepartmentMembership", backref='department')


class DepartmentMembership(get_declarative_base(), MemberRegistryCommon,
        MembershipCommon):
    __tablename__ = 'DepartmentMembershipTable'
    sequence_name = "departmentMembership"

    member_fld = Column(String, ForeignKey("MemberTable.objectId"))
    department_fld = Column(String, ForeignKey("DepartmentTable.objectId"))


class GroupMembership(get_declarative_base(), MemberRegistryCommon,
        MembershipCommon):
    __tablename__ = 'GroupMembershipTable'
    sequence_name = "groupMembership"

    member_fld = Column(String, ForeignKey("MemberTable.objectId"))
    post_fld = Column(String, ForeignKey("PostTable.objectId"))
    group_fld = Column(String, ForeignKey("GroupTable.objectId"))

class Group(get_declarative_base(), MemberRegistryCommon, MembershipCommon):
    __tablename__ = 'GroupTable'
    sequence_name = "group"

    groupType_fld = Column(String, ForeignKey("GroupTypeTable.objectId"))
    name_fld = Column(String)
    description_fld = Column(String)
    abbreviation_fld = Column(String)

    memberships = relationship("GroupMembership", backref='group',
            cascade="all, delete, delete-orphan")


class GroupType(get_declarative_base(), MemberRegistryCommon,
        MembershipCommon):
    __tablename__ = 'GroupTypeTable'
    sequence_name = "groupType"

    name_fld = Column(String)
    description_fld = Column(String)

    group = relationship("Group", backref='type')


class Member(get_declarative_base(), MemberRegistryCommon):
    """
    The member representation. A member has a name and many other personal
    fields. It also has relationships to all the membership classes and even
    to ContactInformation, which is strange. Therefore there's an
    getPrimaryContactInfo method to abstract this away.
    """
    __tablename__ = 'MemberTable'
    sequence_name = "member"

    givenNames_fld = Column(String(100))
    preferredName_fld = Column(String(30))
    surName_fld = Column(String(40))
    maidenName_fld = Column(String(20))
    nickName_fld = Column(String(20))
    birthDate_fld = Column(DateTime)
    studentId_fld = Column(String(10))
    gender_fld = Column(Integer)
    graduated_fld = Column(Integer)
    occupation_fld = Column(String(30))
    photo_fld = Column(Text)
    title_fld = Column(String(30))
    nationality_fld = Column(String(3))
    primaryContactId_fld = Column(String(33),
            ForeignKey('ContactInformationTable.objectId', use_alter=True,
                name="fk_primary_contactinfo"))
    dead_fld = Column(Integer)
    subscribedtomodulen_fld = Column(Integer, default=0)

    noPublishContactInfo_fld = Column(Integer, default=0)

    username_fld = Column(String(150))
    lastsync_fld = Column(DateTime, default=datetime.min)
    
    # Support for several contact infos exists in the database, but is not for now implemented in this frontend

    contactinfos = relationship(ContactInformation,
            backref='member', cascade="all, delete, delete-orphan",
            primaryjoin="Member.objectId==ContactInformation.member_fld")
    contactinfo = relationship(ContactInformation,
            primaryjoin=primaryContactId_fld==ContactInformation.objectId,
            post_update=True)


    departmentmemberships = relationship("DepartmentMembership",
            backref='member', cascade="all, delete, delete-orphan")
    groupmemberships = relationship("GroupMembership", backref='member',
            cascade="all, delete, delete-orphan")
    membershipmemberships = relationship("MembershipMembership",
            backref='member', cascade="all, delete, delete-orphan")
    postmemberships = relationship("PostMembership", backref='member',
            cascade="all, delete, delete-orphan")
    presence = relationship("Presence", backref='member',
            cascade="all, delete, delete-orphan")

    editable_text_fields = ['givenNames_fld', 'preferredName_fld',
            'surName_fld', 'maidenName_fld', 'nickName_fld', 'studentId_fld',
            'occupation_fld', 'title_fld', 'nationality_fld', 'username_fld']

    editable_checkboxes = ['subscribedtomodulen_fld', 'noPublishContactInfo_fld']

    publicfields = ['nickName_fld', 'occupation_fld',
            'nationality_fld']

    def getWholeName(self):
        """
        Convenience method that returns surname + given names.

        >>> foo = Member()
        >>> foo.surName_fld = "Foo"
        >>> foo.givenNames_fld = "Bar Bar"
        >>> foo.getWholeName()
        'Foo Bar Bar'

        """
        return (self.surName_fld or '') + " " + (self.givenNames_fld or '')

    def getName(self):
        """
        Convenience method that returns surname + preferred name.

        >>> foo = Member()
        >>> foo.surName_fld = "Foo"
        >>> foo.preferredName_fld = "Bar"
        >>> foo.getName()
        'Foo Bar'

        """
        return (self.surName_fld or '') + " " + (self.preferredName_fld or
                self.givenNames_fld or '')

    def ifOrdinarieMedlem(self):
        membershipnames = [mship.membership.name_fld for mship in
                self.membershipmemberships]

        return "Ordinarie medlem" in membershipnames



class MembershipMembership(get_declarative_base(),
        MemberRegistryCommon, MembershipCommon):
    __tablename__ = "MembershipTable"
    sequence_name = "membership"

    member_fld = Column(String, ForeignKey("MemberTable.objectId"))
    membershipType_fld = Column(String,
            ForeignKey("MembershipTypeTable.objectId"))


class Membership(get_declarative_base(), MemberRegistryCommon,
        MembershipCommon):
    __tablename__ = "MembershipTypeTable"
    sequence_name = "membershipType"

    name_fld = Column(String)
    abbreviation_fld = Column(String)
    description_fld = Column(String)

    memberships = relationship("MembershipMembership", backref='membership')


class PostMembership(get_declarative_base(), MemberRegistryCommon,
        MembershipCommon):
    __tablename__ = "PostMembershipTable"
    sequence_name = "postMembership"

    post_fld = Column(String, ForeignKey("PostTable.objectId"))
    member_fld = Column(String, ForeignKey("MemberTable.objectId"))


class Post(get_declarative_base(), MemberRegistryCommon, MembershipCommon):
    __tablename__ = "PostTable"
    sequence_name = "post"

    postType_fld = Column(String, ForeignKey("PostTypeTable.objectId"))
    name_fld = Column(String)
    description_fld = Column(String)
    abbreviation_fld = Column(String)

    memberships = relationship("PostMembership", backref='post',
            cascade="all, delete, delete-orphan")
    groupmembership = relationship("GroupMembership", backref='post',
            cascade="all, delete, delete-orphan")


class PostType(get_declarative_base(), MemberRegistryCommon, MembershipCommon):
    __tablename__ = "PostTypeTable"
    sequence_name = "postType"

    name_fld = Column(String)
    description_fld = Column(String)

    post = relationship("Post", backref='type')


class Presence(get_declarative_base(), MemberRegistryCommon, MembershipCommon):
    __tablename__ = "PresenceTable"
    sequence_name = "presence"

    member_fld = Column(String, ForeignKey("MemberTable.objectId"))
    atTF_fld = Column(Integer)
    atTKY_fld = Column(Integer)
    atHUT_fld = Column(Integer)


class Sequence(get_declarative_base()):
    __tablename__ = "members_sequence"
    next = Column(Numeric(19), default=1)
    objectname = Column(String, primary_key=True)


# The Joomla's MySQL tables.
class Jos_Users(get_declarative_base()):
    '''
    Table containing all the users on a Joomla CMS.
    '''

    __tablename__ = "jos_users"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    username = Column(String(150))
    email = Column(String(100))


class Jos_CBFields(get_declarative_base()):
    '''
    User fields used in the Community Builder Joomla module.
    '''
    __tablename__ = "jos_comprofiler"

    user_id = Column(Integer, ForeignKey("jos_users.id"),
            primary_key=True)
    lastupdatedate = Column(DateTime, onupdate=datetime.now)
    cb_streetaddress = Column(String(255))
    cb_postalcode = Column(String(255))
    cb_city = Column(String(255))
    cb_country = Column(String(255))
    cb_phone = Column(String(255))
    cb_subscribedtomodulen = Column(Integer)

    user = relationship("Jos_Users", uselist=False, backref='cbfields')


class Jos_Privacy(get_declarative_base()):
    '''
    Privacy fields used in the Community Builder Joomla module.
    '''
    __tablename__ = "jos_comprofiler_privacy"

    userid = Column(Integer, ForeignKey("jos_users.id"),
            primary_key=True)
    type = Column(String(8))
    xid = Column(Integer, ForeignKey("jos_comprofiler_fields.fieldid"),
            primary_key=True)
    rule = Column(Integer)
    params = Column(String(255))

    user = relationship("Jos_Users", uselist=False, backref='privacies')
    field = relationship("Jos_Fields", uselist=False, backref='privacies')


class Jos_Fields(get_declarative_base()):
    '''
    List of fields used in the Community Builder Joomla module. This class is
    used to get the field ID to be uset in Jos_Privacy.
    '''
    __tablename__ = "jos_comprofiler_fields"
    fieldid = Column(Integer, primary_key=True)
    name = Column(String(50))

MEMBERSDBTABLES = [DepartmentMembership, Department, DepartmentType,
        GroupMembership, Group, GroupType, PostMembership, Post, PostType,
        MembershipMembership, Membership, Presence, ContactInformation, Member,
        Sequence]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
