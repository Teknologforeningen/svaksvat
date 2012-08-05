"""Web interface to login with LDAP username and change contact information."""

# imports
import subprocess
import cherrypy
from jinja2 import Environment, PackageLoader
import sqlalchemy
import os
import sys

sys.path.append(os.path.dirname(os.getcwd()))  # Add .. to path
from backend.ldaplogin import get_member_through_ldap_login
from backend import connect
from backend.orm import (Member, ContactInformation, TooLongValueException,
        update_fields)
import passwordsafe

# constants
env = Environment(loader=PackageLoader('webinterface', 'templates'))


# classes
class WebInterface(object):
    def __init__(self):
        # Create database session
        ps = passwordsafe.PasswordSafe("../svaksvat.cfg")
        SessionMaker = ps.connect_with_config("memberslocalhost")
        self.dbsession = SessionMaker()

    def index(self, message=''):
        template = env.get_template('login.html')
        return template.render(message=message).encode("utf-8")

    index.exposed = True

    def doLogin(self, username=None, password=None):
        try:
            member = get_member_through_ldap_login(username,
                    password, self.dbsession)
        except(subprocess.CalledProcessError):
            return self.index(
                    '<p class="errorMsg">Fel användarnamn eller lösenord!</p>')
        cherrypy.session['Member'] = member

        return self.memberEdit(member)

    doLogin.exposed = True

    def memberEdit(self, member, message=''):
        template = env.get_template('memberEdit.html')
        # The Member class is needed to get the field sizes.
        return template.render(member=member,
                message=message).encode("utf-8")

    memberEdit.exposed = True

    def updateMember(self, **kwargs):
        member = cherrypy.session.get('Member')
        if not member:
            return self.index('<p class="errorMsg">Logga in först!</p>')

        contactinfo = member.contactinfo

        message = '<p class="successMsg">Ändringarna har sparats.</p>'
        try:
            update_fields(member, kwargs)
            update_fields(contactinfo, kwargs)
        except TooLongValueException as e:
            message = ('<p class="errorMsg">Värdet för' +
                    '%s skall vara under %d tecken.</p>') % (
                            e.field, e.maxlength)

        # Autoflush doesn't work here because the server is threaded.
        self.dbsession.merge(member)  # Therefore merge must be used.
        self.dbsession.commit()

        return self.memberEdit(member, message)

    updateMember.exposed = True


def main():
    cherrypy.config.update({'tools.staticdir.root': os.getcwd()})
    cherrypy.quickstart(WebInterface(), '/', './cherrypy.conf')
    return 0

if __name__ == '__main__':
    status = main()
    sys.exit(status)
