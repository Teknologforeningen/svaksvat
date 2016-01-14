"""
Sync fields between Joomla Community Builder and Member registry.
"""

# imports
import sys
import os
import sqlalchemy
import datetime
from sqlalchemy import or_

sys.path.append(os.path.dirname(os.getcwd()))  # Add .. to path
from backend.ldaplogin import (get_member_with_real_name,
        DuplicateNamesException, PersonNotFoundException)
from backend import connect
from backend.orm import (Member, ContactInformation, Jos_CBFields,
        Jos_Users, Jos_Fields, Jos_Privacy)

# constants
NOT_VISIBLE = 99

# Jos_CBFields conversions
COMPROFDICT = dict(
        cb_streetaddress='streetAddress_fld',
        cb_postalcode='postalCode_fld',
        cb_city='city_fld',
        cb_country='country_fld',
        cb_phone='phone_fld',
        cb_subscribedtomodulen='subscribedtomodulen_fld')


# exception classes
# interface functions
# classes
# internal functions & classes

def get_members(joomlasession, registrysession, username):
    registrymember = registrysession.query(Member).filter(Member.username_fld ==
            username).one()
    joomlamember = joomlasession.query(
            Jos_CBFields).join(Jos_Users).filter(
                    Jos_Users.username == username).one()
    return registrymember, joomlamember


def set_field_invisible(joomlasession, joomlamember, joomlafield):
    """Set the field invisible on the profile page."""

    userid = joomlamember.user.id
    fieldid = joomlasession.query(Jos_Fields).filter(
            Jos_Fields.name == joomlafield).one().fieldid

    # If privacy rule already exists.
    if joomlasession.query(Jos_Privacy).filter(
            Jos_Privacy.userid == userid).filter(
                    Jos_Privacy.xid == fieldid).count() == 0:
        #####
        # Oursql gives an error when adding a privacyrule the normal way
        # https://bugs.launchpad.net/oursql/+bug/805983
        # privacyrule = Jos_Privacy(user = joomlamember.user, type="field",
        #        field = field, rule = NOT_VISIBLE)
        # joomlasession.add(privacyrule)
        # joomlasession.commit()
        #
        # Workaround is to execute a convetional SQL insert statement.
        #####
        ins = Jos_Privacy.__table__.insert().values(userid = joomlamember.user.id,
                type="field", xid = fieldid, rule = NOT_VISIBLE)
        joomlasession.connection().execute(ins)


def copy_fields_to_joomla(joomlasession, registrysession, username):
    """Copy fields to homepage from members registry for given user.

    Also sets the field invisible on the profile page.

    Returns True if succesful."""

    try:
        registrymember, joomlamember = get_members(
                joomlasession, registrysession, username)
    except sqlalchemy.orm.exc.NoResultFound as e:
        print("User %s not found" % username)
        return False

    # Copy email field.
    mail = 'email'
    setattr(joomlamember.user, mail,
            getattr(registrymember.contactinfo, 'email_fld'))
    set_field_invisible(joomlasession, joomlamember, mail)

    # Copy rest of fields.
    for joomlafield, registryfield in COMPROFDICT.items():
        registryvalue = None
        if hasattr(registrymember, registryfield):
            registryvalue = getattr(registrymember, registryfield)
        else:
            registryvalue = getattr(registrymember.contactinfo, registryfield)

        setattr(joomlamember, joomlafield, registryvalue)
        set_field_invisible(joomlasession, joomlamember, joomlafield)
    registrymember.lastsync_fld = datetime.datetime.now()

    return True


def copy_fields_to_registry(joomlasession, registrysession, username):
    """Copy fields to  members registry from homepage for given user.

    Returns True if succesful."""

    try:
        registrymember, joomlamember = get_members(
                joomlasession, registrysession, username)
    except sqlalchemy.orm.exc.NoResultFound as e:
        print("User %s not found" % username)
        return False

    # Copy email field.
    mail = 'email_fld'
    setattr(registrymember.contactinfo, mail,
            getattr(joomlamember.user, 'email'))

    # Copy rest of fields.
    for joomlafield, registryfield in COMPROFDICT.items():
        joomlavalue = getattr(joomlamember, joomlafield)
        setattr(registrymember.contactinfo, registryfield, joomlavalue)

    return True

def get_usernames(joomlasession):
    """Get list of usernames on the homepage."""
    users = joomlasession.query(Jos_Users).all()
    return [user.username for user in users]

def get_dirty_from_registry(registrysession):
    """Get query with the members to be synced to the homepage"""
    dirtymembersquery = registrysession.query(Member).join(
            ContactInformation).filter(or_(
        Member.lastsync_fld < Member.modified_fld,
        Member.lastsync_fld < ContactInformation.modified_fld))
    return dirtymembersquery

def sync_databases(joomlasession, registrysession):
    """Sync the member contactinfo fields between the homepage and
    member.registry"""
    synced_joomla, synced_registry = 0, 0
    usernames = get_usernames(joomlasession)

    registrydirtyquery = get_dirty_from_registry(registrysession)

    for username in usernames:
        # If member with username must be synced.
        if registrydirtyquery.filter(
                Member.username_fld == username).count() == 1:
            if copy_fields_to_joomla(joomlasession, registrysession, username):
                synced_joomla += 1
        else:
            if copy_fields_to_registry(joomlasession, registrysession,
                    username):
                synced_registry += 1

    print("Synced %d users to homepage" % synced_joomla)
    print("Synced %d users to members registry" % synced_registry)


def main():
    JoomlaSessionMaker = connect.connect('joomla',
        'joomla', 'postgre.teknolog.fi', 'joomla', 'mysql+oursql',
        create_metadata=False)
    joomlasession = JoomlaSessionMaker()

    RegistrySessionMaker = connect.connect('members',
        'members', 'postgre.teknolog.fi', 'members')
    registrysession = RegistrySessionMaker()

    sync_databases(joomlasession, registrysession)
    registrysession.commit()
    joomlasession.commit()

    return 0


if __name__ == '__main__':
    status = main()
    sys.exit(status)
