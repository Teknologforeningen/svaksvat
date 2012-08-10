"""Password Safe

Implements an OS independent password storage.
"""

# imports
import sys
import getpass
import configparser
import re
import time
import _thread as thread

import sqlalchemy

import keyring

from backend import connect, sshwrapper
# constants
# exception classes
# interface functions
# classes


class PasswordSafe:
    def __init__(self, configfile="svaksvat.cfg", gui_interface=False):
        self.configfile = configfile
        self.configparser = configparser.ConfigParser()
        self.configparser.read(configfile)
        self.askcredentialsfunc = self.askcredentialsCLI
        if gui_interface:
            self.askcredentialsfunc = self.askcredentialsQt

    def get_passid(self, service, usernameparameter):
        """Returns identifier for the password."""
        return service + ":" + usernameparameter

    def get_password(self, service, usernameparameter, username):
        return keyring.get_password(self.get_passid(service, usernameparameter),
            username)

    def set_password(self, service, usernameparameter, username, password):
        keyring.set_password(self.get_passid(service, usernameparameter),
                username, password)

    def get_config_value(self, section, parameter):
        value = self.configparser.get(section, parameter)
        if not value:
            value = input("Input " + section + " " + parameter)

        return value

    def askcredentials(self, authfunction, section, usernameparameter):
        if not self.configparser.has_section(section):
            self.configparser.add_section(section)
            self.configparser.set(section, usernameparameter, "")

        username = self.configparser.get(section, usernameparameter)
        password = None
        if username != '':
            password = self.get_password(
                    section, usernameparameter,
                    username)

        authreturn = None
        passwordchanged = False

        try:
            while True:
                authreturn = authfunction(username, password)
                if authreturn:
                    break
                passwordchanged = True
                username, password = self.askcredentialsfunc(section + " " +
                        usernameparameter)

        except Exception as e:
                print(e)
                return None

        if passwordchanged:
            self.store_credentials(self.configfile, section, usernameparameter,
                    username, password)

        return authreturn, username, password

    def store_credentials(self, configfile, section,
            usernameparameter, username, password):
        # store the username
        self.configparser.set(section, usernameparameter, username)
        self.configparser.write(open(configfile, 'w'))
        try:
            self.set_password(section, usernameparameter, username, password)
            print("Lösenordet sparat")
        except keyring.backend.PasswordSetError:
            print("Det gick inte att spara lösenordet")

    def askcredentialsQt(self, context=""):
        ...

    def askcredentialsCLI(self, context=""):
        print(context)
        username = input("Användarnamn:")
        password = getpass.getpass("Lösenord:")
        return username, password

    def connect_with_config(self, configsection):
        usernameparameter = "dbusername"
        host = self.configparser.get(configsection, "host")
        port = self.configparser.get(configsection, "port")
        database = self.configparser.get(configsection, "database")
        dbtype = self.configparser.get(configsection, "dbtype")
        dbusername = self.configparser.get(configsection, usernameparameter)
        dbpassword = self.get_password(configsection, usernameparameter, dbusername)
        create_metadata = bool(self.configparser.get(configsection, "create_metadata"))
        sshusername = self.configparser.get(configsection,
                "sshusername")

        sshconnecting = False
        threadfinishedmutex = thread.allocate_lock()
        while True:
            try:
                SessionMaker = connect.connect(dbusername,
                        dbpassword, host+":"+port,
                        database, dbtype, create_metadata)

                self.store_credentials(self.configfile, configsection,
                        usernameparameter, dbusername, dbpassword)

                return SessionMaker

            except sqlalchemy.exc.OperationalError as e:
                if re.match(
                    "(.*role .* does not exist.*)|" +
                    "(.*password authentication failed for user.*)|" +
                    "(.*no password supplied.*)", repr(e)):
                    dbusername, dbpassword = self.askcredentialsfunc(
                           "Fel inloggningsinformation för databasen!")

                elif re.match(".*no pg_hba.conf entry for host.*", repr(e)):
                    print("Du måste logga in på servern.")
                    if not sshusername:
                        sshusername = input("SSH användarnamn:")

                    thread.start_new_thread(sshwrapper.portforward_to_localhost,
                            (host, sshusername, port, threadfinishedmutex))

                    host = "localhost"
                    sshconnecting = True

                elif re.match(".*could not connect to server: Connection refused.*",
                        repr(e)) and sshconnecting:
                    time.sleep(1)
                    if threadfinishedmutex.locked(): # SSH-thread exited
                        host = self.configparser.get(configsection, "host")
                        sshusername = None
                        sshconnecting = False
                        threadfinishedmutex.release()

                else:
                    print(e)

# internal functions & classes
def testauth(username, password):
    return username == password

def testfunction():
    import tempfile
    tempfilehandle, tempfilename = tempfile.mkstemp(suffix=".cfg")
    ps = PasswordSafe(configfile=tempfilename)
    testservice = "PasswordSafePasswordIdentifier"
    testuserparameter = "PasswordSafePasswordIdentifierUserParameter"
    testuser = "PasswordSafePasswordIdentifierUser"
    ps.set_password(testservice, testuserparameter, testuser, "")
    if ps.get_password(testservice, testuserparameter, testuser):
        return False

    testpass = "!#?R¤?FI?AF"
    ps.set_password(testservice, testuserparameter, testuser, testpass)
    if ps.get_password(testservice, testuserparameter, testuser) != testpass:
        return False

    ps.askcredentials(testauth, "testsection",
    "testusername")

    return True

def main():
    ps = PasswordSafe()
    ps.connect_with_config("memberslocalhost")

    if testfunction():
        return 0
    return 1

if __name__ == '__main__':
    status = main()
    sys.exit(status)

