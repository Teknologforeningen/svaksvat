"""LDAP support functions"""

# imports
import subprocess
import base64

from .orm import Member


# constants
ldapmaster = "ldap.teknolog.fi"


# exception classes
class DuplicateNamesException(Exception):
    """
    Raised when the search query returns more than one user because they
    share the same name.
    """
    def __init__(self, query):
        self.query = query

    def __str__(self):
        print(self.query)


class PersonNotFoundException(Exception):
    """
    Raised when there isn't a database entry for the searched person.
    """
    def __init__(self, person_name):
        self.person_name = person_name

    def __str__(self):
        print(self.person_name)


# interface functions
def query_ldap_user_info(username, password):
    """
    Performs query with ldapsearch to the TF LDAP-master
    Returns output of the command.
    Raises subprocess.CalledProcessError on invalid login credentials
    """

    # Perform ldap query for the user's common name
    ldapquery = ['ldapsearch', '-b', 'dc=fi', '-w', password,
            '-D', 'uid=%s,ou=People,dc=teknologforeningen,dc=fi' % username,
            '-h', ldapmaster, 'uid=%s' % username, 'cn']
    queryoutput = subprocess.check_output(ldapquery)

    return queryoutput


def extract_name_from_ldapquery(ldapquery):
    """
    Parses the output of the query_ldap_user_info function and returns the
    person's name in the "Firstname Surname" format.
    """
    common_name = ''
    if b'cn:: ' in ldapquery:  # base64 encoding
        # Extract base64 encoded common name from output
        common_name_b64 = ldapquery.split(b'cn:: ')[1].splitlines()[0]
        # Decode common name
        common_name = base64.b64decode(common_name_b64).decode('utf-8')
    else:
        common_name = ldapquery.split(
                b'cn: ')[1].splitlines()[0].decode('utf-8')

    return common_name


def split_ldap_common_name(common_name):
    """Returns firstname, surname tuple
    filters non alphabetical characters to avoid encoding problems"""
    namesplit = common_name.split()
    firstname = namesplit[0]
    surname = ''
    if len(namesplit) > 1:
        surname = namesplit[-1]

    # Filter nonalphabetical.
    firstname = ''.join(c for c in firstname if c.isalpha())
    surname = ''.join(c for c in surname if c.isalpha())

    return (firstname, surname)


def get_member_through_ldap_login(username, password, session):
    """
    Tries to determine which person in the database the LDAP-account belongs
    to. There's no direct reference to a database entry so the person's name is
    used to search for the right row. A SQLAlchemy Session object is needed to
    perform the database query.
    """

    ldapquery = query_ldap_user_info(username, password)

    common_name = extract_name_from_ldapquery(ldapquery)

    firstname, surname = split_ldap_common_name(common_name)

    # Construct SQL query to fetch user from database
    return get_member_with_real_name(firstname, surname, session)


def get_member_with_real_name(firstname, surname,
        session=None, query=None):
    """
    Tries to retrieve the database entry corresponding to the Member's real
    name.  A SQLAlchemy Session object is needed to perform the database query,
    alternatively you can use an existing query object containing MemberTable.
    """
    if not query:
        query = session.query(Member)

    if surname:
        query = query.filter(Member.surName_fld.like(surname))

    if firstname:
        tempquery = query.filter(Member.preferredName_fld.like(firstname + "%"))
        if tempquery.count() == 0:
            # Try the givenNames_fld instead if preferredName_fld didn't work.
            tempquery = query.filter(Member.givenNames_fld.like(
                '%{}%'.format(firstname)))
            if tempquery.count() == 0:
                raise PersonNotFoundException(firstname + ' ' + surname)
        query = tempquery

    if query.count() != 1:
        raise DuplicateNamesException(query)

    return query.one()
