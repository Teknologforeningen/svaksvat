"""Password Safe

Implements an OS independent password storage.
"""

# imports
import sys
import getpass
import configparser
import re
import time
import socket
import _thread as thread

from PyQt4 import QtGui
import sqlalchemy

import keyring

from backend import connect, sshwrapper
# constants
# exception classes
# interface functions
# classes
import sys
from PyQt4 import QtGui


class PasswordDialog(QtGui.QDialog):

    def __init__(self, context=""):
        super(PasswordDialog, self).__init__()

        self.initUI(context)

    def initUI(self, context):
        self.formlayout = QtGui.QFormLayout(self)

        self.username_le = QtGui.QLineEdit(self)
        self.username_le.returnPressed.connect(self.accept)

        self.password_le = QtGui.QLineEdit(self)
        self.password_le.setEchoMode(QtGui.QLineEdit.Password)
        self.password_le.returnPressed.connect(self.accept)

        self.okbutton = QtGui.QPushButton('OK', self)
        self.okbutton.clicked.connect(self.accept)
        self.cancelbutton = QtGui.QPushButton('Avbryt', self)
        self.cancelbutton.clicked.connect(self.reject)

        self.buttonrow = QtGui.QHBoxLayout()
        self.buttonrow.addWidget(self.okbutton)
        self.buttonrow.addWidget(self.cancelbutton)

        self.formlayout.addRow("Användarnamn:", self.username_le)
        self.formlayout.addRow("Lösenord:", self.password_le)
        self.formlayout.addRow("", self.buttonrow)

        self.setWindowTitle(context)

        self.show()

    def clearCredentialsAndClose(self):
        self.username_le.clear()
        self.password_le.clear()

    def getCredentials(self):
        if self.result(): # Accepted?
            return self.username_le.text(), self.password_le.text()
        return "",""

class PasswordSafe:
    def __init__(self, configfile="svaksvat.cfg", enablegui=False):
        self.configfile = configfile
        self.configparser = configparser.ConfigParser()
        self.configparser.read(configfile)
        self.askcredentialsfunc = self.askcredentialsCLI
        if not sys.stdin.isatty() or enablegui:
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
        app = QtGui.QApplication(sys.argv)
        pd = PasswordDialog(context)
        app.exec_()
        return pd.getCredentials()

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
        dbpassword = self.get_password(configsection, usernameparameter,
                dbusername) or "" # Can be None which doesn't store.
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
                    # Test if port is open
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        s.connect(("localhost", int(port)))
                        s.shutdown(2)
                        print("Nätverksporten är redan öppen. Testar om" +
                                " portforwarding är redan igång...")

                    except: # Port not open. Commence SSH port forwarding.
                        print("Du måste logga in på servern.")
                        if not sshusername:
                            sshusername = input("SSH användarnamn:")

                        thread.start_new_thread(sshwrapper.portforward_to_localhost,
                                (host, sshusername, port, threadfinishedmutex))

                    sshconnecting = True
                    host = "localhost"


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
    app = QtGui.QApplication(sys.argv)
    pd = PasswordDialog("Hello")
    app.exec_()
    print(pd.getCredentials())
    #status = main()
    #sys.exit(status)

